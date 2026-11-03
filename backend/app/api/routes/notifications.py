from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.db.models import Notification, DemoUser
from app.api.deps import get_current_user_and_role

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def list_notifications(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """Lists notifications for current user/role."""
    notifs = (
        db.query(Notification)
        .filter((Notification.role == user.role) | (Notification.role == "all") | (Notification.user_id == user.id))
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    return notifs

@router.patch("/{id}/read")
def mark_notification_read(id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"success": True}

@router.post("/clear-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    notifs = (
        db.query(Notification)
        .filter((Notification.role == user.role) | (Notification.role == "all") | (Notification.user_id == user.id))
        .all()
    )
    for n in notifs:
        n.is_read = True
    db.commit()
    return {"success": True}
