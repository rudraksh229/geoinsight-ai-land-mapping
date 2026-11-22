from datetime import datetime
from pymongo.database import Database
from fastapi import HTTPException, status

from database import get_next_sequence
from models import User
from schemas import UserRegister, UserLogin

from security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(
    db: Database,
    user: UserRegister,
):
    clean_email = str(user.email).strip().lower()
    existing = db["users"].find_one({"email": clean_email})

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists.",
        )

    try:
        new_id = get_next_sequence("users")
        new_user = User(
            id=new_id,
            name=user.name.strip(),
            email=clean_email,
            password_hash=hash_password(user.password),
            role="user",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        db["users"].insert_one(new_user.to_dict())

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account.",
        ) from exc

    return {
        "success": True,
        "message": "User registered successfully.",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "is_active": new_user.is_active,
        },
    }


def login_user(
    db: Database,
    credentials: UserLogin,
):
    email = str(credentials.email).strip().lower()
    user_doc = db["users"].find_one({"email": email})
    user = User.from_doc(user_doc)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    if not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    }
