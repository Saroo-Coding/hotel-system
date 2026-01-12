from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.models.users import User, UserRole, UserStatus
from app.api.deps import check_roles, get_current_user, pagination_response
from app.schemas.user_schemas import AdminCreateUser, StaffCreateCustomer, UserUpdateDTO, ChangePasswordDTO

import logging

from backend.app.models.bookings import Booking
from backend.app.models.refresh_tokens import RefreshToken

router = APIRouter()
logger = logging.getLogger("UsersRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/list_users")
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = Query(None),
    status: str | None = Query(None),
    keyword: str | None = Query(None),

    db: Session = Depends(get_db),
    _: User = Depends(check_roles("ADMIN", "STAFF"))
):
    """ Get users with pagination & filters """
    try:
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if status:
            query = query.filter(User.status == status)

        if keyword:
            keyword_like = f"%{keyword}%"
            query = query.filter(
                or_(
                    User.email.ilike(keyword_like),
                    User.phone.ilike(keyword_like),
                    User.full_name.ilike(keyword_like),
                )
            )

        total = query.count()

        users = (
            query
            .order_by(User.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        data = [
            {
                "id": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role.value,
                "status": user.status,
                "updated_at": user.updated_at.strftime("%d/%m/%Y %H:%M"),
            }
            for user in users
        ]

        return pagination_response(
            data=data,
            page=page,
            limit=limit,
            total=total,
        )

    except Exception as e:
        logger.exception("Unexpected error in get_all_users. ERROR: " + str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.get("/{user_id}/info")
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles("ADMIN","STAFF"))
):
    ''' Get user by ID (only ADMIN and STAFF) '''
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        return {
        "success": True,
        "code": 200,
        "message": "Success",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status,
            "updated_at": user.updated_at.strftime("%d/%m/%Y %H:%M")
        }
    }

    except Exception as e:
        logger.exception("Unexpected error in get_user_by_id. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

# TODO: gửi email thông báo mật khẩu tạm thời
@router.post("/admin/users")
def admin_create_user(
    payload: AdminCreateUser,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    ''' Register new user role STAFF or CUSTOMER (only ADMIN) '''
    try:
        if payload.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already exists")
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

        return {
            "success": True,
            "code": 200,
            "message": "Success"
        }

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in admin_create_user. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.post("/staff/customers")
def staff_create_customer(
    payload: StaffCreateCustomer,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.STAFF))
):
    ''' Register new customer (only STAFF) '''
    try:
        if payload.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        if payload.phone:
            if db.query(User).filter(User.phone == payload.phone).first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already exists")
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

        return {
            "success": True,
            "code": 200,
            "message": "Success"
        }

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in staff_create_customer. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    
@router.put("/{user_id}/update")
def update_user(
    user_id: str,
    payload: UserUpdateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ''' Update user info (ADMIN and STAFF) '''
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )

        if current_user.role == "STAFF" and user.role == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="STAFF cannot update ADMIN user"
            )

        if current_user.role == "STAFF":
            if payload.role is not None or payload.status is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="STAFF cannot change role or status"
                )

        update_data = payload.model_dump(exclude_unset=True) # Only fields provided in the request body

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
    
        return {
            "success": True,
            "code": 200,
            "message": "Update successfully",
            "data": {
                "id": user.id
            }
    }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in update_user. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
@router.patch("/staff/{user_id}/status")
def change_user_status(
    user_id: str,
    user_status: UserStatus,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles("ADMIN","STAFF"))
):
    ''' Change user status (only ADMIN and STAFF) '''
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.status = user_status

        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "code": 200,
            "message": "Change status successfully"
        }

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in change_user_status. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

# TODO: thêm chức năng avatar
@router.get("/me")
def get_current_user_info(
    user: User = Depends(get_current_user)
):
    ''' Get current logged in user info '''
    try:
        return {
            "success": True,
            "code": 200,
            "message": "Success",
            "data": {
                "id": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role.value,
                "status": user.status,
                "updated_at": user.updated_at.strftime("%d/%m/%Y %H:%M")
            }
        }
    except Exception as e:
        logger.exception("Unexpected error in get_current_user_info. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.put("/me/change-password")
def user_change_password(
    payload: ChangePasswordDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ''' Update current logged in current_user password '''
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    try:
        with db.begin():
            user = db.get(User, current_user.id)
            user.password_hash = hash_password(payload.new_password)

        return {
            "success": True,
            "code": 200,
            "message": "Success"
        }

    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in update_current_user_info. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.delete("/me/delete-account")
def deactivate_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ''' Deactivate current logged in user account (only CUSTOMER) '''
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    try:
        with db.begin():
            db.query(User).filter(
                User.id == current_user.id,
                User.status == UserStatus.ACTIVE
            ).update(
                {"status": UserStatus.INACTIVE},
                synchronize_session=False
            )

            # db.query(Booking).filter(
            #     Booking.guest_id == current_user.id,
            #     Booking.status.in_(["PENDING", "CONFIRMED"])
            # ).update(
            #     {"status": "CANCELLED"},
            #     synchronize_session=False
            # )

            db.query(RefreshToken).filter(
                RefreshToken.user_id == current_user.id
            ).delete(synchronize_session=False)

    except Exception as e:
        logger.exception("Unexpected error in deactivate_my_account. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )