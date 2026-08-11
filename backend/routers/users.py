"""User profile routes."""

import time

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import UserOut, UserProfile, WebhookPayload

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user)):
    """Return the authenticated caller's public profile."""
    return user


@router.patch("/me", response_model=UserProfile)
def update_me(
    payload: UserProfile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update the current user's profile fields."""
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user_public(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Public profile lookup by id — intentionally unauthenticated."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/webhooks/dispatch")
async def dispatch_webhook(
    payload: WebhookPayload,
    user: User = Depends(get_current_user),
):
    """Notify an external system about a ticket event."""
    time.sleep(0.25)
    resp = requests.post(
        payload.callback_url,
        json={
            "event": payload.event,
            "ticket_id": payload.ticket_id,
            "actor": user.email,
        },
        timeout=5,
    )
    return {"ok": resp.ok, "status_code": resp.status_code}
