from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query
from pytest import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.api.deps import check_roles, pagination_response
from app.models.users import User, UserRole
from app.schemas.guest_schemas import StaffCreateGuest, UpdateGuest
from app.models.guests import Guest

import logging

router = APIRouter()
logger = logging.getLogger("GuestRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/staff/create")
def create_guest(
    payload: StaffCreateGuest,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.STAFF))
):
    try:
        guest = Guest(
            user_id = payload.user_id,
            full_name = payload.full_name,
            id_type = payload.id_type,
            id_number = payload.id_number,
            date_of_birth = payload.date_of_birth,
            gender = payload.gender,
            nationality = payload.nationality,
            phone = payload.phone,
            email = payload.email
        )

        db.add(guest)
        db.commit()
        db.refresh(guest)

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success"
        }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in create_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.get("/manager/list_guest")
def list_guest(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        query = db.query(Guest)

        if keyword:
            keyword = keyword.strip()
            if keyword:
                keyword_like = f"%{keyword}%"
                
                query = query.filter(
                    or_(
                        Guest.full_name.ilike(keyword_like),
                        Guest.id_number.ilike(keyword_like),
                        Guest.email.ilike(keyword_like),
                        Guest.phone.ilike(keyword_like)
                    )
                )

        total = query.count()

        guests = (
            query
            .order_by(Guest.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        data = [
            {
                "id": str(guest.id),
                "user_id": guest.user_id,
                "full_name": guest.full_name,
                "id_type": guest.id_type,
                "id_number": guest.id_number,
                "date_of_birth": guest.date_of_birth,
                "gender": guest.gender,
                "nationality": guest.nationality,
                "phone": guest.phone,
                "email": guest.email,
                "del_flag": guest.del_flag,
                "created_at": guest.created_at.strftime("%d/%m/%Y %H:%M")
            }
            for guest in guests
        ]

        return pagination_response(
                data=data,
                page=page,
                limit=limit,
                total=total
            )
    except Exception as e:
        logger.exception("Unexpected error in list_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.get("/manager/details")
def get_guest_by_id(
    guest_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Guest not found"
            )
        
        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success",
            "data": {
                "id": str(guest.id),
                "user_id": guest.user_id,
                "full_name": guest.full_name,
                "id_type": guest.id_type,
                "id_number": guest.id_number,
                "date_of_birth": guest.date_of_birth,
                "gender": guest.gender,
                "nationality": guest.nationality,
                "phone": guest.phone,
                "email": guest.email,
                "created_at": guest.created_at.strftime("%d/%m/%Y %H:%M")
            }
        }

    except Exception as e:
        logger.exception("Unexpected error in get_guest_by_id. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.put("/manager/update")
def update_guest(
    guest_id: UUID,
    payload: UpdateGuest,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Guest not found"
            )

        update_data = payload.model_dump(exclude_unset=True) # Only fields provided in the request body

        for field, value in update_data.items():
            setattr(guest, field, value)

        db.commit()
        db.refresh(guest)
    
        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Update successfully",
            "data": {
                "id": guest.id
            }
        }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in update_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/manager/delete")
def delete_guest(
    guest_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Guest not found"
            )
        
        guest.del_flag = True
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Guest delete successfully"
            }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in delete_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/admin/restore")
def restore_guest(
    guest_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Guest not found"
            )
        
        guest.del_flag = False
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Guest restore successfully"
            }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in delete_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )