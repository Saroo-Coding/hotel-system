from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import not_, or_
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone
import secrets
import string

from app.core.database import SessionLocal
from app.models.bookings import Booking, BookingStatus
from app.models.checkin_tokens import CheckinToken, CheckinTokenType
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


def generate_checkin_token() -> str:
    return secrets.token_urlsafe(32)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def cleanup_expired_pending_bookings(db: Session) -> None:
    now_utc = datetime.now(timezone.utc)

    expired_booking_ids = (
        db.query(CheckinToken.booking_id)
        .join(Booking, Booking.id == CheckinToken.booking_id)
        .filter(
            CheckinToken.type == CheckinTokenType.CHECKIN,
            CheckinToken.used_at.is_(None),
            CheckinToken.expires_at <= now_utc,
            Booking.status == BookingStatus.PENDING,
        )
        .all()
    )

    booking_ids = [row[0] for row in expired_booking_ids]
    if not booking_ids:
        return

    db.query(CheckinToken).filter(CheckinToken.booking_id.in_(booking_ids)).delete(
        synchronize_session=False
    )
    db.query(Booking).filter(
        Booking.id.in_(booking_ids),
        Booking.status == BookingStatus.PENDING,
    ).delete(synchronize_session=False)


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
            cleanup_expired_pending_bookings(db)

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

            checkin_token_value = None
            for _ in range(10):
                candidate = generate_checkin_token()
                token_exists = db.query(CheckinToken.id).filter(CheckinToken.token == candidate).first()
                if not token_exists:
                    checkin_token_value = candidate
                    break

            if not checkin_token_value:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="common.internal_server_error",
                )

            checkin_token = CheckinToken(
                booking_id=booking.id,
                token=checkin_token_value,
                type=CheckinTokenType.CHECKIN,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                used_at=None,
            )
            db.add(checkin_token)
            db.flush()

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


@router.get("/search")
def search_booking_by_code(
    booking_code: str,
    db: Session = Depends(get_db),
):
    with db.begin():
        cleanup_expired_pending_bookings(db)

    normalized_code = str(booking_code or "").strip().upper()
    if not normalized_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="booking.pending.missingCode",
        )

    result = (
        db.query(Booking, CheckinToken)
        .join(
            CheckinToken,
            CheckinToken.booking_id == Booking.id,
        )
        .filter(
            Booking.booking_code == normalized_code,
            CheckinToken.type == CheckinTokenType.CHECKIN,
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="booking.pending.notFound",
        )

    booking, checkin_token = result
    expires_at = checkin_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    now_utc = datetime.now(timezone.utc)
    is_pending = booking.status == BookingStatus.PENDING

    if is_pending and checkin_token.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="booking.pending.tokenUsed",
        )

    if is_pending and expires_at <= now_utc:
        # Expired payment session: remove token + booking immediately.
        with db.begin():
            db.query(CheckinToken).filter(CheckinToken.booking_id == booking.id).delete(
                synchronize_session=False
            )
            db.query(Booking).filter(
                Booking.id == booking.id,
                Booking.status == BookingStatus.PENDING,
            ).delete(synchronize_session=False)

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="booking.pending.tokenExpired",
        )

    remaining_seconds = int((expires_at - now_utc).total_seconds())

    payment_status = "PENDING"
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT]:
        payment_status = "PAID"
    elif booking.status in [BookingStatus.CANCELLED, BookingStatus.NO_SHOW]:
        payment_status = "FAILED"

    return {
        "id": str(booking.id),
        "booking_code": booking.booking_code,
        "status": booking.status.value,
        "payment_status": payment_status,
        "checkin_date": booking.checkin_date.isoformat(),
        "checkout_date": booking.checkout_date.isoformat(),
        "total_price": int(booking.total_price),
        "expires_at": expires_at.isoformat(),
        "remaining_seconds": max(remaining_seconds, 0),
    }


@router.delete("/cancel")
def cancel_pending_booking(
    booking_code: str,
    db: Session = Depends(get_db),
):
    normalized_code = str(booking_code or "").strip().upper()
    if not normalized_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="booking.lookup.searchRequired",
        )

    try:
        with db.begin():
            booking = db.query(Booking).filter(Booking.booking_code == normalized_code).first()
            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="booking.pending.notFound",
                )

            if booking.status != BookingStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="booking.lookup.cannotCancel",
                )

            db.query(CheckinToken).filter(CheckinToken.booking_id == booking.id).delete(
                synchronize_session=False
            )
            db.query(Booking).filter(Booking.id == booking.id).delete(synchronize_session=False)

        return {"message": "booking.lookup.cancelSuccess"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in cancel_pending_booking. ERROR: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="common.internal_server_error",
        )
