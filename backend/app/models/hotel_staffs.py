from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class HotelStaffRole(enum.Enum):
    STAFF = "STAFF"
    MANAGER = "MANAGER"

class HotelStaff(Base):
    __tablename__ = "hotel_staffs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    hotel_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(Enum(HotelStaffRole), nullable=False, default=HotelStaffRole.STAFF)
    created_at = Column(DateTime(timezone=True), server_default=func.now())