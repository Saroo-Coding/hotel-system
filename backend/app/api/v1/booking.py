from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import not_, or_
from sqlalchemy.orm import Session
from datetime import date
import secrets
import string

from app.core.database import SessionLocal
from app.models.bookings import Booking, BookingStatus
from app.models.guests import Guest
from app.models.rooms import Room, RoomStatus
from app.schemas.booking_schemas import CreateBookingRequest

import logging

router = APIRouter()
logger = logging.getLogger("BookingRouter")


def generate_booking_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(3)) + "_" + "".join(
        secrets.choice(chars) for _ in range(3)
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/bookings")
def create_booking(
    payload: CreateBookingRequest,
    db: Session = Depends(get_db),
):
    # Disallow booking start date in the past
    if payload.checkin_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="booking.validation.checkinPastNotAllowed",
        )

    # Validate date range
    if payload.checkin_date >= payload.checkout_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="booking.validation.dateRangeInvalid",
        )

    try:
        # Transaction boundary: lock room row, then check overlap + insert booking.
        # This serializes booking creation per room and prevents race condition.
        with db.begin():
            guest = (
                db.query(Guest)
                .filter(
                    Guest.id == payload.guest_id,
                    Guest.del_flag == False,
                )
                .first()
            )
            if not guest:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="booking.messages.guestNotFound",
                )

            room = (
                db.query(Room)
                .filter(Room.id == payload.room_id)
                .with_for_update()
                .first()
            )
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="room.messages.notFound",
                )

            if room.status != RoomStatus.AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="booking.messages.roomNotActive",
                )

            has_overlap = (
                db.query(Booking.id)
                .filter(
                    Booking.room_id == payload.room_id,
                    Booking.status.in_(
                        [
                            BookingStatus.PENDING,
                            BookingStatus.CONFIRMED,
                            BookingStatus.CHECKED_IN,
                        ]
                    ),
                    not_(
                        or_(
                            Booking.checkout_date <= payload.checkin_date,
                            Booking.checkin_date >= payload.checkout_date,
                        )
                    ),
                )
                .first()
                is not None
            )

            if has_overlap:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="booking.messages.roomNotAvailableInRange",
                )

            nights = (payload.checkout_date - payload.checkin_date).days
            total_price = int(room.base_price) * nights

            booking_code = None
            for _ in range(10):
                candidate = generate_booking_code()
                exists = db.query(Booking.id).filter(Booking.booking_code == candidate).first()
                if not exists:
                    booking_code = candidate
                    break

            if not booking_code:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="common.internal_server_error",
                )

            booking = Booking(
                booking_code=booking_code,
                room_id=payload.room_id,
                guest_id=payload.guest_id,
                checkin_date=payload.checkin_date,
                checkout_date=payload.checkout_date,
                status=BookingStatus.PENDING,
                total_price=total_price,
            )
            db.add(booking)
            db.flush()
            db.refresh(booking)

            return {
                "id": str(booking.id),
                "booking_code": booking.booking_code,
                "status": booking.status.value,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in create_booking. ERROR: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="common.internal_server_error",
        )
