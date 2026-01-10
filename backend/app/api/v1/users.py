from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.config import settings
from app.models.users import User, UserRole, UserStatus
from app.api.deps import check_roles, get_current_user
from app.schemas.user_schemas import AdminCreateUser, StaffCreateCustomer

import logging

router = APIRouter()
logger = logging.getLogger("UsersRouter")

# db: Session = Depends(get_db) nghĩa là:
# FastAPI tạo DB session giúp bạn đưa session đó vào biến db và tự đóng nó sau khi request xong.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get tất cả người dùng (dành cho ADMIN và STAFF)
# TODO: thêm ?page=1&limit=20&role=CUSTOMER&status=ACTIVE&keyword=nguyen
@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(check_roles("ADMIN","STAFF"))
):
    try:
        users = db.query(User).all()
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role.value,
                "updated_at": user.updated_at.strftime("%d/%m/%Y %H:%M")
            }
            for user in users
        ]

    except Exception as e:
        logger.exception("Unexpected error in get_all_users")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# Get user by ID (dành cho ADMIN và STAFF)
@router.get("/users/{user_id}")
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles("ADMIN","STAFF"))
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": str(user.id),
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role.value,
            "updated_at": user.updated_at.strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        logger.exception("Unexpected error in get_user_by_id")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# Register dùng cho ADMIN tạo STAFF hoặc CUSTOMER mới
# TODO: gửi email thông báo mật khẩu tạm thời
@router.post("/admin/users")
def admin_create_user(
    payload: AdminCreateUser,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        if payload.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=400, detail="Email already exists")

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(status_code=400, detail="Phone already exists")

        user = User(
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(settings.BASE_PASSWORD),
            full_name=payload.full_name if payload.full_name is not None else payload.role,
            role=payload.role
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "User created successfully"}

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in admin_create_user")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# Register dùng cho STAFF tạo khách hàng mới
@router.post("/staff/customers")
def staff_create_customer(
    payload: StaffCreateCustomer,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.STAFF))
):
    try:
        if payload.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=400, detail="Email already exists")

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(status_code=400, detail="Phone already exists")

        user = User(
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(settings.BASE_PASSWORD),
            full_name=payload.full_name if payload.full_name is not None else UserRole.CUSTOMER,
            role=UserRole.CUSTOMER
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "Customer created successfully"}

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in staff_create_customer")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )