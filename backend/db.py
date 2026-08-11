"""Database session helpers and tightly-coupled data access."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./tickets.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ticket_to_client_payload(ticket, *, include_web_chrome: bool = True) -> dict:
    """
    Shape a ticket for callers.

    include_web_chrome defaults True — the web app expects rendered_html and
    nav crumbs. Mobile / third clients inherit the same payload today.
    """
    payload = {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "priority": ticket.priority,
        "owner_id": ticket.owner_id,
        "version": ticket.version,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
    }
    if include_web_chrome:
        # Web-only presentation baked into the shared data layer.
        payload["rendered_html"] = (
            f"<article class='ticket-card' data-id='{ticket.id}'>"
            f"<h2>{ticket.title}</h2>"
            f"<p class='meta'>{ticket.status} · {ticket.priority}</p>"
            f"</article>"
        )
        payload["web_nav"] = {
            "crumbs": ["Home", "Tickets", ticket.title],
            "detail_path": f"/tickets/{ticket.id}",
        }
    return payload
