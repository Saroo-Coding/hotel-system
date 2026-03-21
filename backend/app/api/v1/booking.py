from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query
from pytest import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.api.deps import check_roles
from app.models.users import User, UserRole
from app.models.guests import Guest
from app.models.bookings import Booking
from app.models.rooms import Room, RoomStatus

import logging

router = APIRouter()
logger = logging.getLogger("BookingRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/guests/bookings")
def create_booking(
    guest_id: UUID = Query(..., description="ID of the guest making the booking"),
    hotel_id: UUID = Query(..., description="ID of the hotel to book"),
    room_id: UUID = Query(..., description="ID of the room to book"),
    db: Session = Depends(get_db),
):
    try:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")

        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        elif room.status != RoomStatus.AVAILABLE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is not available for booking")
        # For simplicity, we assume they exist

        # Create booking
        new_booking = Booking(
            guest_id=guest_id,
            hotel_id=hotel_id,
            room_id=room_id,
            status="booked"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Booking created successfully",
            "data": {
                "id": str(new_booking.id)
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the booking")