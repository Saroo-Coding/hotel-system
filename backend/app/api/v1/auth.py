from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings
from app.schemas.auth_schemas import RegisterRequest
from app.api.deps import get_current_user
from app.models.users import User, UserRole
from app.models.refresh_tokens import RefreshToken

import uuid
import logging

router = APIRouter()
logger = logging.getLogger("AuthRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_customer(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        if payload.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=400, detail="Email already exists")

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(status_code=400, detail="Phone already exists")

        user = User(
            user = User(
                email=payload.email,
                phone=payload.phone,
                password_hash=hash_password(payload.password),
                full_name=UserRole.CUSTOMER,
                role=UserRole.CUSTOMER
            )
        )

        db.add(user)
        db.commit()
        db.refresh(user) 

        return {
            "email": user.email,
            "phone": user.phone
        }
    
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in register_customer")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# TODO: Thêm try except cho các hàm dưới và log lỗi
@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            (User.email == form_data.username) |
            (User.phone == form_data.username)
        )
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    refresh_token_value = str(uuid.uuid4())

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_value,
        expires_at=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )

    db.add(refresh_token)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token_value,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/auth/refresh",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/refresh")
def refresh_token(
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token_in_db = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now()
        )
        .first()
    )

    if not token_in_db:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).get(token_in_db.user_id)

    new_access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    _: User = Depends(get_current_user),
    refresh_token: str | None = Cookie(default=None),
    response: Response = None,
    db: Session = Depends(get_db),
):
    if refresh_token:
        token_in_db = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .first()
        )
        if token_in_db:
            token_in_db.revoked = True
            db.commit()

    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")

    return {"message": "Logged out"}
