"""Ticket CRUD routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..cache import get_cached_ticket, invalidate_cached_ticket, put_cached_ticket
from ..db import get_db, ticket_to_client_payload
from ..deps import get_current_user
from ..models import Activity, Comment, Ticket, User
from ..schemas import TicketCreate, TicketOut, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Priority ladder used by the inline SLA / escalation rules below.
_PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
_ALLOWED_TRANSITIONS = {
    "open": {"in_progress", "closed"},
    "in_progress": {"open", "closed"},
    "closed": {"open"},
}


def _apply_sla_and_transitions(ticket: Ticket, updates: dict) -> dict:
    """
    Product rules live in the route module today — status machine, SLA bump,
    and auto-title tagging. There is no service layer; a second client that
    needs the same rules must reimplement or call these HTTP handlers.
    """
    if "status" in updates:
        current = ticket.status
        nxt = updates["status"]
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if nxt != current and nxt not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition {current} → {nxt}",
            )

    if "priority" in updates:
        new_rank = _PRIORITY_RANK.get(updates["priority"], 1)
        old_rank = _PRIORITY_RANK.get(ticket.priority, 1)
        if new_rank > old_rank and ticket.status == "open":
            # Escalation: open + higher priority ⇒ auto move to in_progress.
            updates.setdefault("status", "in_progress")

    if "title" in updates and updates["title"]:
        title = updates["title"].strip()
        if ticket.priority == "urgent" or updates.get("priority") == "urgent":
            if not title.startswith("[URGENT]"):
                updates["title"] = f"[URGENT] {title}"

    return updates


@router.get("/", response_model=list[TicketOut])
def list_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return tickets owned by the authenticated user, with activity counts."""
    tickets = db.query(Ticket).filter(Ticket.owner_id == user.id).all()
    results: list[TicketOut] = []
    for ticket in tickets:
        # N+1: per-ticket comment count + owner email lookups.
        comment_count = (
            db.query(Comment).filter(Comment.ticket_id == ticket.id).count()
        )
        owner = db.query(User).filter(User.id == ticket.owner_id).first()
        out = TicketOut.model_validate(ticket)
        out.comment_count = comment_count
        out.owner_email = owner.email if owner else None
        results.append(out)
    return results


@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    """
    Create a ticket scoped to the current user.

    When Idempotency-Key is present, look up (owner_id, key) and return the
    existing ticket on retry instead of inserting again. Key is stored on the
    Ticket row (MVP). Requests without a key remain non-idempotent.
    """
    _ = request.headers.get("X-Request-Id")
    key = (idempotency_key or "").strip() or None

    if key is not None:
        existing = (
            db.query(Ticket)
            .filter(Ticket.owner_id == user.id, Ticket.idempotency_key == key)
            .first()
        )
        if existing is not None:
            response.status_code = status.HTTP_200_OK
            return existing

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        owner_id=user.id,
        idempotency_key=key,
        version=1,
    )
    db.add(ticket)
    try:
        db.commit()
    except IntegrityError:
        # Concurrent retry lost the race; return the winner's row.
        db.rollback()
        if key is None:
            raise
        existing = (
            db.query(Ticket)
            .filter(Ticket.owner_id == user.id, Ticket.idempotency_key == key)
            .first()
        )
        if existing is None:
            raise
        response.status_code = status.HTTP_200_OK
        return existing

    db.refresh(ticket)
    response.status_code = status.HTTP_201_CREATED
    return ticket


@router.get("/search", response_model=list[TicketOut])
def search_tickets(
    q: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Title search limited to the caller's tickets (parameterized)."""
    rows = db.execute(
        text(
            "SELECT * FROM tickets WHERE owner_id = :owner_id "
            "AND title LIKE :pattern"
        ),
        {"owner_id": user.id, "pattern": f"%{q}%"},
    ).mappings().all()
    return [TicketOut.model_validate(dict(r)) for r in rows]


@router.get("/admin/by-status/{status_name}", response_model=list[TicketOut])
def tickets_by_status(
    status_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Admin-style filter by status string."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    query = f"SELECT * FROM tickets WHERE status = '{status_name}'"
    rows = db.execute(text(query)).mappings().all()
    return [TicketOut.model_validate(dict(r)) for r in rows]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # TODO(security): IDOR — cache hit returns any ticket by id; no owner check.
    cached = get_cached_ticket(ticket_id)
    if cached is not None:
        return cached

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # TODO(security): IDOR — DB path also loads by ticket_id only; any auth user can read.
    put_cached_ticket(ticket_id, ticket)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # TODO(security): IDOR — PATCH loads by ticket_id only; any auth user can update.

    updates = payload.model_dump(exclude_unset=True)
    expected_version = updates.pop("expected_version", None)
    if expected_version is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expected_version is required for optimistic concurrency",
        )
    if expected_version != ticket.version:
        # Fail loudly — do not commit; caller must reload and retry.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Version conflict: expected {expected_version}, "
                f"current {ticket.version}"
            ),
        )

    updates = _apply_sla_and_transitions(ticket, updates)

    for field, value in updates.items():
        setattr(ticket, field, value)
    ticket.version = ticket.version + 1
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    # Write-aside: invalidate so subsequent GETs do not serve the pre-patch row.
    invalidate_cached_ticket(ticket_id)
    return ticket


@router.post("/{ticket_id}/close", response_model=TicketOut)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Close a ticket and write an activity row.

    The two writes are separate commits — if the activity insert fails, the
    ticket stays closed with no audit trail (and vice versa on partial failure
    in other stores).
    """
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.owner_id == user.id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = "closed"
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    activity = Activity(
        ticket_id=ticket.id,
        actor_id=user.id,
        action="close",
        detail=f"Closed by {user.email}",
    )
    db.add(activity)
    db.commit()

    invalidate_cached_ticket(ticket_id)
    return ticket


@router.get("/{ticket_id}/client-view")
def ticket_client_view(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Shared payload shaped for the web client (and anyone else on this API)."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket_to_client_payload(ticket)
