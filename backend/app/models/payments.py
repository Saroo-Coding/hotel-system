from sqlalchemy import Column, String, Enum, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class PaymentMethod(enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    CASH = "CASH"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    BANK_TRANSFER = "BANK_TRANSFER"

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    booking_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_ref = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())