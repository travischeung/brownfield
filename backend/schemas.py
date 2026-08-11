"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(BaseModel):
    """Shared intake/response model for profile updates."""

    id: Optional[int] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None
    api_key: Optional[str] = None
    hashed_password: Optional[str] = None

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    priority: str = "medium"


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    # Required by update_ticket for optimistic concurrency (compare to Ticket.version).
    expected_version: Optional[int] = None


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    owner_id: int
    version: int
    created_at: datetime
    updated_at: datetime
    comment_count: Optional[int] = None
    owner_email: Optional[str] = None

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class CommentOut(BaseModel):
    id: int
    body: str
    ticket_id: int
    author_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookPayload(BaseModel):
    event: str
    ticket_id: int
    callback_url: str


class ActivityOut(BaseModel):
    id: int
    ticket_id: int
    actor_id: int
    action: str
    detail: str
    created_at: datetime

    model_config = {"from_attributes": True}
