print("AUTH ROUTER LOADED")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserRegister, UserLogin
from models import User

from services.auth_service import (
    register_user,
    login_user,
)

from security import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================================
# REGISTER
# ==========================================

@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return register_user(
            db,
            user,
        )

    except ValueError as exc:
        raise Exception(
            str(exc)
        ) from exc


# ==========================================
# LOGIN
# ==========================================

@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        return login_user(
            db,
            credentials,
        )

    except ValueError as exc:
        raise Exception(
            str(exc)
        ) from exc


# ==========================================
# CURRENT USER
# ==========================================

@router.get("/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
