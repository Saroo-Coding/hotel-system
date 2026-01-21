from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query
from pytest import Session
from sqlalchemy import String, cast, func, or_

from app.core.database import SessionLocal
from app.api.deps import check_roles, pagination_response
from app.models.hotels import Hotel
from app.models.rooms import BedType, Room, RoomStatus
from app.models.users import User, UserRole
from app.schemas.room_schemas import AdminCreateRoom, AdminUpdateRoom

import logging

router = APIRouter()
logger = logging.getLogger("RoomRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/list_room")
def get_list_rooms(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    hotel_id: str | None = Query(None),
    bed_type: BedType | None = Query(None),
    status_room: RoomStatus | None = Query(None),
    keyword: str | None = Query(None),

    db: Session = Depends(get_db)
):
    query = db.query(Room)

    if hotel_id is not None:
        query = query.filter(Room.hotel_id == hotel_id)

    if bed_type is not None:
        query = query.filter(Room.bed_type == bed_type)

    if status_room is not None:
        query = query.filter(Room.status == status_room)

    if keyword:
        keyword = keyword.strip()
        if keyword:
            keyword_like = f"%{keyword}%"

            query = query.filter(
                or_(
                    Room.room_number.ilike(keyword_like),
                    cast(Room.floor, String).ilike(keyword_like)
                )
            )

    total = query.count()

    rooms = (
        query
        .order_by(Room.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = [
        {
            "id": str(room.id),
            "hotel_id": str(room.hotel_id),
            "room_number": room.room_number,
            "floor": room.floor,
            "bed_type": room.bed_type.value,
            "base_price": int(room.base_price),
            "status": room.status.value,
            "description": room.description
        }
        for room in rooms
    ]

    return pagination_response(
            data=data,
            page=page,
            limit=limit,
            total=total
        )

@router.get("/room_details")
def get_room_detail(
    room_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )
        
        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success",
            "data": {
                "id": str(room.id),
                "hotel_id": room.hotel_id,
                "room_number": room.room_number,
                "floor": room.floor,
                "bed_type": room.bed_type.value,
                "base_price": room.base_price,
                "status": room.status.value,
                "description": room.description,
                "created_at": room.created_at.strftime("%d/%m/%Y %H:%M"),
                "updated_at": room.updated_at.strftime("%d/%m/%Y %H:%M")
            }
        }
    except Exception as e:
        logger.exception("Unexpected error in get_room_detail. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@router.post("/admin/create")
def admin_create_room(
    payload: AdminCreateRoom, 
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN))
):
    try:
        if db.query(Hotel).filter(Hotel.id == payload.hotel_id).first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )
        
        room = Room(
            hotel_id = payload.hotel_id,
            room_number = payload.room_number,
            floor = payload.floor,
            bed_type = payload.bed_type,
            base_price = payload.base_price,
            status = payload.status,
            description = payload.description
        )

        db.add(room)
        db.commit()
        db.refresh(room)

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Success"
        }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in admin_create_room. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@router.put("/manager/update")
def update_room(
    room_id: UUID,
    payload: AdminUpdateRoom,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    ''' Update user info (ADMIN and STAFF) '''
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Room not found"
            )
        
        if not db.query(Hotel).filter(Hotel.id == str(payload.hotel_id)).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found"
            )

        update_data = payload.model_dump(exclude_unset=True) # Only fields provided in the request body

        for field, value in update_data.items():
            setattr(room, field, value)

        db.commit()
        db.refresh(room)
    
        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Update successfully",
            "data": {
                "id": room.id
            }
        }
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in update_room. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/manager/room_maintenance")
def room_maintenance(
    room_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Room not found"
            )
        
        room.status = RoomStatus.MAINTENANCE
        room.updated_at = func.now()
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Room maintenance successfully"
            }

    except Exception as e:
        logger.exception("Unexpected error in room_maintenance. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )

@router.patch("/manager/room_available")
def room_available(
    room_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(check_roles(UserRole.ADMIN, UserRole.STAFF))
):
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Room not found"
            )
        
        room.status = RoomStatus.AVAILABLE
        room.updated_at = func.now()
        db.commit()
        
        return {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "Room available successfully"
            }

    except Exception as e:
        logger.exception("Unexpected error in room_available. ERROR: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
        )


