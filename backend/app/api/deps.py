from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import DemoUser

def get_current_user_and_role(
    x_demo_user_id: Optional[str] = Header(None),
    x_demo_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> DemoUser:
    """
    Extracts the current demo user from headers.
    If x_demo_role is explicitly provided, ensures the resolved user matches the role.
    """
    if x_demo_user_id:
        user = db.query(DemoUser).filter(DemoUser.id == x_demo_user_id).first()
        if user:
            # If role header was also passed and mismatches, override role for testing or use user with that role
            if x_demo_role and user.role != x_demo_role:
                alt = db.query(DemoUser).filter(DemoUser.role == x_demo_role).first()
                if alt:
                    return alt
            return user
            
    if x_demo_role:
        user = db.query(DemoUser).filter(DemoUser.role == x_demo_role).first()
        if user:
            return user
            
    # Default to prof_sharma
    prof = db.query(DemoUser).filter(DemoUser.id == "prof_sharma").first()
    if prof:
        return prof
        
    return DemoUser(
        id="prof_sharma",
        name="Dr. R. Sharma",
        role="faculty",
        email="r.sharma@college.edu"
    )

def require_faculty(
    current_user: DemoUser = Depends(get_current_user_and_role)
) -> DemoUser:
    if current_user.role != "faculty":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: This endpoint requires Faculty permissions."
        )
    return current_user

def require_student(
    current_user: DemoUser = Depends(get_current_user_and_role)
) -> DemoUser:
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: This endpoint is for Students only."
        )
    return current_user
