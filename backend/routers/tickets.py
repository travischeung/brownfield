"""Ticket CRUD routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..cache import get_cached_ticket, put_cached_ticket
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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    """
    Create a ticket scoped to the current user.

    Clients may send Idempotency-Key on flaky networks; it is accepted and
    ignored — retries always insert a new row.
    """
    _ = idempotency_key  # acknowledged, not enforced
    _ = request.headers.get("X-Request-Id")

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        owner_id=user.id,
        version=1,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
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
    cached = get_cached_ticket(ticket_id)
    if cached is not None:
        return cached

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # Missing ownership check — any authenticated user can read any ticket.
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
    # Missing ownership check — any authenticated user can patch any ticket.

    updates = payload.model_dump(exclude_unset=True)
    # expected_version is accepted on the wire and discarded — last write wins.
    updates.pop("expected_version", None)
    updates = _apply_sla_and_transitions(ticket, updates)

    for field, value in updates.items():
        setattr(ticket, field, value)
    ticket.updated_at = datetime.utcnow()
    # version is never incremented and never compared.
    db.commit()
    db.refresh(ticket)
    # Cache is not invalidated — subsequent GETs may return the pre-patch row.
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
