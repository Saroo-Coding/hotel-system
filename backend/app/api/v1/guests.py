from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pytest import Session
from sqlalchemy import or_
from datetime import datetime

from app.core.database import SessionLocal
from app.core.validators import (
    validate_birth_date,
    validate_cccd,
    validate_email,
    validate_full_name,
    validate_guest_search_keyword,
    validate_phone,
)
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

@router.post("/create")
def create_guest(
    payload: StaffCreateGuest,
    db: Session = Depends(get_db),
):
    errors = {}
    full_name = (payload.full_name or "").strip()
    id_type = (payload.id_type or "").strip()
    id_number = (payload.id_number or "").strip()
    date_of_birth_raw = (payload.date_of_birth or "").strip()
    gender = (payload.gender or "").strip()
    nationality = (payload.nationality or "").strip()
    phone = (payload.phone or "").strip()
    email = (payload.email or "").strip()

    if not full_name:
        errors["full_name"] = "booking.validation.nameRequired"
    elif validate_full_name(full_name):
        errors["full_name"] = "booking.validation.nameInvalid"

    if not id_type:
        errors["id_type"] = "booking.validation.idTypeRequired"
    elif id_type not in {"CCCD", "Passport"}:
        errors["id_type"] = "booking.validation.idTypeRequired"

    if not id_number:
        errors["id_number"] = "booking.validation.citizenIdRequired"
    elif id_type == "CCCD" and not validate_cccd(id_number):
        errors["id_number"] = "booking.validation.citizenIdInvalid"
    elif id_type == "Passport" and not id_number.isalnum():
        errors["id_number"] = "booking.validation.passportInvalid"

    date_of_birth = None
    if not date_of_birth_raw:
        errors["date_of_birth"] = "booking.validation.dateOfBirthRequired"
    else:
        try:
            date_of_birth = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
            birth_date_error = validate_birth_date(date_of_birth)
            if birth_date_error == "birth_date_under_18":
                errors["date_of_birth"] = "booking.validation.dateOfBirthUnder18"
            elif birth_date_error:
                errors["date_of_birth"] = "booking.validation.dateOfBirthInvalid"
        except ValueError:
            errors["date_of_birth"] = "booking.validation.dateOfBirthInvalid"

    if not gender:
        errors["gender"] = "booking.validation.genderRequired"
    elif gender not in {"MALE", "FEMALE", "OTHER"}:
        errors["gender"] = "booking.validation.genderRequired"

    if not phone:
        errors["phone"] = "booking.validation.phoneRequired"
    elif not validate_phone(phone):
        errors["phone"] = "booking.validation.phoneInvalid"

    if email and not validate_email(email):
        errors["email"] = "booking.validation.emailInvalid"

    if id_number and db.query(Guest).filter(Guest.id_number == id_number, Guest.del_flag == False).first():
        errors["id_number"] = "booking.validation.citizenIdExists"

    if phone and db.query(Guest).filter(Guest.phone == phone, Guest.del_flag == False).first():
        errors["phone"] = "booking.validation.phoneExists"

    if errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": errors
            }
        )

    try:
        guest = Guest(
            user_id = payload.user_id,
            full_name = full_name,
            id_type = id_type,
            id_number = id_number,
            date_of_birth = date_of_birth,
            gender = gender,
            nationality = nationality or None,
            phone = phone,
            email = email or None
        )

        db.add(guest)
        db.commit()
        db.refresh(guest)

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success",
            "data": {
                "id": str(guest.id)
            }
        }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in create_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="common.internal_server_error"
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

@router.get("/search")
def search_guest(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        keyword = (keyword or "").strip()
        if keyword == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="booking.validation.searchRequired"
            )

        keyword_type = validate_guest_search_keyword(keyword)
        if keyword_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="common.invalid_format"
            )

        query = db.query(Guest)
        if keyword_type == "id_number":
            query = query.filter(
                Guest.id_number == keyword,
                Guest.del_flag == False
            )
        else:
            query = query.filter(
                Guest.phone == keyword,
                Guest.del_flag == False
            )

        guest = query.first()

        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="booking.messages.guestNotFound"
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
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in search_guest. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="common.internal_server_error"
        )
