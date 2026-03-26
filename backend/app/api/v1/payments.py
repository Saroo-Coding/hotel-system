from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.booking import cleanup_expired_pending_bookings
from app.core.database import SessionLocal
from app.models.bookings import Booking, BookingStatus
from app.models.checkin_tokens import CheckinToken, CheckinTokenType
from app.models.payments import Payment, PaymentMethod, PaymentStatus
from app.schemas.payment_schemas import CreatePaymentRequest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


PAYMENT_METHOD_MAP = {
    "CREDIT_CARD": PaymentMethod.CREDIT_CARD,
    "CASH": PaymentMethod.CASH,
    "MOBILE_PAYMENT": PaymentMethod.MOBILE_PAYMENT,
    "BANK_TRANSFER": PaymentMethod.BANK_TRANSFER,
}


@router.post("")
def create_payment(
    payload: CreatePaymentRequest,
    db: Session = Depends(get_db),
):
    normalized_method = str(payload.method or "").strip().upper()
    payment_method = PAYMENT_METHOD_MAP.get(normalized_method)
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payment.validation.invalidMethod",
        )

    try:
        with db.begin():
            cleanup_expired_pending_bookings(db)

            booking = (
                db.query(Booking)
                .filter(Booking.id == payload.booking_id)
                .with_for_update()
                .first()
            )
            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="booking.pending.notFound",
                )

            if booking.status != BookingStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="payment.messages.bookingNotPending",
                )

            checkin_token = (
                db.query(CheckinToken)
                .filter(
                    CheckinToken.booking_id == booking.id,
                    CheckinToken.type == CheckinTokenType.CHECKIN,
                )
                .with_for_update()
                .first()
            )
            if not checkin_token:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="booking.pending.notFound",
                )

            expires_at = checkin_token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at <= datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="booking.pending.tokenExpired",
                )

            existing_payment = (
                db.query(Payment)
                .filter(
                    Payment.booking_id == booking.id,
                    Payment.status == PaymentStatus.COMPLETED,
                )
                .first()
            )
            if existing_payment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="payment.messages.alreadyPaid",
                )

            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_price,
                method=payment_method,
                status=PaymentStatus.COMPLETED,
                transaction_ref=f"fakenumber1234-{booking.booking_code}",
            )
            db.add(payment)

            booking.status = BookingStatus.CONFIRMED
            checkin_token.expires_at = datetime.combine(
                booking.checkout_date,
                time.max,
                tzinfo=timezone.utc,
            )

            db.flush()

            return {
                "success": True,
                "message": "payment.messages.completed",
                "payment": {
                    "id": str(payment.id),
                    "booking_id": str(booking.id),
                    "method": payment.method.value,
                    "status": payment.status.value,
                    "transaction_ref": payment.transaction_ref,
                },
            }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="common.internal_server_error",
        )
