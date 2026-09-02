print("AUTH ROUTER LOADED")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import UserRegister, UserLogin
from models import User

from services.auth_service import (
    register_user,
    login_user
)

from security import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# REGISTER
# ==========================================

@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    return register_user(db, user)


# ==========================================
# LOGIN
# ==========================================

@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    return login_user(db, credentials)


# ==========================================
# CURRENT USER
# ==========================================

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
    