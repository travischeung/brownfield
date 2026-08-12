from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, Session

app = FastAPI()

DATABASE_URL = "sqlite:///./notifications.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    member_id = Column(String, index=True)
    result_id = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class NotificationRequest(BaseModel):
    member_id: str
    result_id: str
    message: str


class NotificationResponse(BaseModel):
    member_id: str
    result_id: str
    message: str
    created_at: str


@app.post("/notifications")
def create_notification(notification: NotificationRequest) -> NotificationResponse:
    db = Session(engine)
    
    created_at = datetime.utcnow()
    db_notification = Notification(
        id=f"{notification.member_id}_{notification.result_id}_{int(created_at.timestamp() * 1000)}",
        member_id=notification.member_id,
        result_id=notification.result_id,
        message=notification.message,
        created_at=created_at,
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    db.close()
    
    return NotificationResponse(
        member_id=db_notification.member_id,
        result_id=db_notification.result_id,
        message=db_notification.message,
        created_at=db_notification.created_at.isoformat(),
    )


@app.get("/notifications/{member_id}")
def get_notifications(member_id: str) -> dict:
    db = Session(engine)
    
    notifications = (
        db.query(Notification)
        .filter(Notification.member_id == member_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    
    db.close()
    
    notification_list = [
        {
            "member_id": n.member_id,
            "result_id": n.result_id,
            "message": n.message,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]
    
    return {"member_id": member_id, "notifications": notification_list}


@app.get("/health")
def health() -> dict:
    return {"ok": True}
