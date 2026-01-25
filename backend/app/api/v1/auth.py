import uuid
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings
from app.core.validators import validate_email, validate_phone
from app.schemas.auth_schemas import RegisterRequest
from app.api.deps import get_current_user
from app.models.users import User, UserRole, UserStatus
from app.models.refresh_tokens import RefreshToken

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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Email already exists"
                )

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone already exists"
                )

        user = User(
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            full_name=UserRole.CUSTOMER.value,
            role=UserRole.CUSTOMER
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
        logger.exception("Unexpected error in register_customer. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.post("/login")
def login(
    response: Response,
    email: str | None = Form(None),
    phone: str | None = Form(None),
    password: str | None = Form(None),
    db: Session = Depends(get_db),
):
    errors = {}
    email = email.strip() if email else None
    phone = phone.strip() if phone else None
    password = password.strip() if password else None

    if not email and not phone:
        errors["email"] = "login.error_email_required"
        errors["phone"] = "login.error_phone_required"

    if email and phone:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "email": "login.error_only_one_identifier",
                    "phone": "login.error_only_one_identifier",
                },
            },
        )

    if email and not validate_email(email):
        errors["email"] = "login.error_invalid_email"

    if phone and not validate_phone(phone):
        errors["phone"] = "login.error_invalid_phone"

    if not password:
        errors["password"] = "login.error_password_required"

    if errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": errors
            }
        )

    if email:
        user = db.query(User).filter(User.email == email).first()
    else:
        user = db.query(User).filter(User.phone == phone).first()

    if not user or not verify_password(password, user.password_hash):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "error.INVALID_CREDENTIALS",
            }
        )

    if user.status != UserStatus.ACTIVE:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "message": "error.ACCOUNT_INACTIVE",
            }
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    refresh_token_value = str(uuid.uuid4())

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_value,
        expires_at=datetime.utcnow()
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
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
    _: User = Depends(get_current_user),
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    try:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh token"
            )

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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )

        user = db.query(User).get(token_in_db.user_id)

        if not user or user.status != UserStatus.ACTIVE:
            token_in_db.revoked = True
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account inactive or blocked"
            )

        new_access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.value}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.exception("Unexpected error in refresh_token. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

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
            .filter(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False
            )
            .first()
        )
        if token_in_db:
            token_in_db.revoked = True
            db.commit()

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth/refresh",
        httponly=True,
    )

    return {"message": "Logged out"}

