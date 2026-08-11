"""SQLAlchemy models for the ticket tracker."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    api_key = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="owner")
    comments = relationship("Comment", back_populates="author")
    activities = relationship("Activity", back_populates="actor")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "idempotency_key",
            name="uq_ticket_owner_idempotency",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(32), default="open", nullable=False)
    priority = Column(String(16), default="medium", nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # MVP idempotency: nullable; multiple NULLs allowed. Set when client sends
    # Idempotency-Key — unique per owner so retries return the same row.
    idempotency_key = Column(String(128), nullable=True)
    # Optimistic concurrency token — writers must send expected_version on PATCH.
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete")
    activities = relationship("Activity", back_populates="ticket", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Activity(Base):
    """Audit / activity-stream row written alongside ticket mutations."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(64), nullable=False)
    detail = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="activities")
    actor = relationship("User", back_populates="activities")
