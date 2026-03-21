import uuid
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings
from app.core.validators import validate_email, validate_phone, validate_password, validate_full_name
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
    email: str | None = Form(None),
    phone: str | None = Form(None),
    full_name: str | None = Form(None),
    password: str | None = Form(None),
    confirm_password: str | None = Form(None),
    db: Session = Depends(get_db),
):
    errors = {}
    email = email.strip() if email else None
    phone = phone.strip() if phone else None
    full_name = full_name.strip() if full_name else None
    password = password.strip() if password else None
    confirm_password = confirm_password.strip() if confirm_password else None

    if not email and not phone:
        errors["email"] = "auth.error_email_required"
        errors["phone"] = "auth.error_phone_required"

    if email and phone:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "email": "auth.error_only_one_identifier",
                    "phone": "auth.error_only_one_identifier",
                },
            },
        )

    if email and not validate_email(email):
        errors["email"] = "auth.error_invalid_email"

    if phone and not validate_phone(phone):
        errors["phone"] = "auth.error_invalid_phone"

    if not full_name:
        errors["full_name"] = "auth.error_full_name_required"
    elif full_name_error := validate_full_name(full_name):
        errors["full_name"] = f"auth.{full_name_error}"

    if not password:
        errors["password"] = "auth.error_password_required"
    elif password_error := validate_password(password):
        errors["password"] = f"auth.{password_error}"

    if not confirm_password:
        errors["confirm_password"] = "auth.error_confirm_password_required"

    if password and confirm_password and password != confirm_password:
        errors["confirm_password"] = "auth.error_passwords_do_not_match"

    if email and db.query(User).filter(User.email == email).first():
        errors["email"] = "auth.error_email_exists"

    if phone and db.query(User).filter(User.phone == phone).first():
        errors["phone"] = "auth.error_phone_exists"

    if errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": errors
            }
        )

    try:
        user = User(
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            full_name=full_name
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "auth.register.success",
            }
        )

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
        errors["email"] = "auth.error_email_required"
        errors["phone"] = "auth.error_phone_required"

    if email and phone:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "email": "auth.error_only_one_identifier",
                    "phone": "auth.error_only_one_identifier",
                },
            },
        )

    if email and not validate_email(email):
        errors["email"] = "auth.error_invalid_email"

    if phone and not validate_phone(phone):
        errors["phone"] = "auth.error_invalid_phone"

    if not password:
        errors["password"] = "auth.error_password_required"

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

