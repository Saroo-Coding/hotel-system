from sqlalchemy import Column, String, Enum, DateTime, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class RoomStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    MAINTENANCE = "MAINTENANCE"
    BOOKED = "BOOKED"

class BedType(enum.Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    hotel_id = Column(UUID(as_uuid=True), nullable=False)
    room_number = Column(String(10), nullable=False)
    floor = Column(Integer)
    bed_type = Column(Enum(BedType), nullable=False, default=BedType.SINGLE)
    base_price = Column(Numeric(15, 0), nullable=False)
    status = Column(Enum(RoomStatus), nullable=False, default=RoomStatus.AVAILABLE)
    description = Column(Text)
    image = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())