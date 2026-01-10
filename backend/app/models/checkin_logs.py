from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CheckinLog(Base):
    __tablename__ = "checkin_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    booking_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)
    method = Column(String(20), nullable=False)
    performed_by = Column(UUID(as_uuid=True))
    source = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())