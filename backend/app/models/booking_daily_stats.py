from sqlalchemy import Column, Date, DateTime, Numeric, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BookingDailyStat(Base):
    __tablename__ = "booking_daily_stats"

    hotel_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    date = Column(Date, primary_key=True)
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())