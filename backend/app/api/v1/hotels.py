from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query
from pytest import Session
from sqlalchemy import func, or_

from app.core.database import SessionLocal
from app.api.deps import check_roles, pagination_response
from app.models.users import User, UserRole
from app.models.hotels import Hotel, HotelStatus
from app.schemas.hotel_schemas import HotelUpdate

import logging

router = APIRouter()
logger = logging.getLogger("HotelRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/list_hotels")
def get_hotels(
    db: Session = Depends(get_db),

    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None)
):
    try:
        query = db.query(Hotel)

        if keyword:
            keyword_like = f"%{keyword}%"
            query = query.filter(
                or_(
                    Hotel.name.ilike(keyword_like),
                    Hotel.address.ilike(keyword_like),
                    Hotel.phone.ilike(keyword_like),
                    Hotel.email.ilike(keyword_like),
                )
            )        

        total = query.count()
        
        hotels = (
            query
            .order_by(Hotel.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        data = [
            {
                "id": hotel.id,
                "name": hotel.name,
                "address": hotel.address,
                "phone": hotel.phone,
                "email": hotel.email,
                "description": hotel.description,
                "updated_at": hotel.updated_at.strftime("%d/%m/%Y %H:%M"),
            }
            for hotel in hotels
        ]

        return pagination_response(
            data=data,
            page=page,
            limit=limit,
            total=total
        )
    except Exception as e:
        logger.exception("Unexpected error in get_hotels. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )
    
@router.get("/details")
def get_hotel_details(
    hotel_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success",
            "data": {
                "id": str(hotel.id),
                "name": hotel.name,
                "address": hotel.address,
                "phone": hotel.phone,
                "email": hotel.email,
                "status": hotel.status.value,
                "created_at": hotel.created_at.strftime("%d/%m/%Y %H:%M"),
                "updated_at": hotel.updated_at.strftime("%d/%m/%Y %H:%M")
            }
        }

    except Exception as e:
        logger.exception("Unexpected error in get_hotel_details. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@router.put("/admin/update")
def update_hotel(
    hotel_id: UUID,
    payload: HotelUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )
        
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(hotel, field, value)

        db.commit()
        db.refresh(hotel)
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Update successfully",
                "data": {
                    "id": hotel.id
                }
            }

    except Exception as e:
        logger.exception("Unexpected error in update_hotel. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@router.patch("/admin/activate")
def activate_hotel(
    hotel_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )
        
        hotel.status = HotelStatus.ACTIVE
        hotel.updated_at = func.now()
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Hotel activated successfully"
            }

    except Exception as e:
        logger.exception("Unexpected error in activate_hotel. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@router.patch("/admin/deactivate")
def deactivate_hotel(
    hotel_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )
        
        hotel.status = HotelStatus.INACTIVE
        hotel.updated_at = func.now()
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Hotel deactivated successfully"
            }

    except Exception as e:
        logger.exception("Unexpected error in deactivate_hotel. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )