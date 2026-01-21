from uuid import UUID
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional
from decimal import Decimal

from app.core.validators import validate_not_empty, validate_vnd_decimal, validate_positive_number

class RoomStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    MAINTENANCE = "MAINTENANCE"
    BOOKED = "BOOKED"

class BedType(str, Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"

class AdminCreateRoom(BaseModel):
    hotel_id: Optional[UUID]
    room_number: Optional[str]
    floor: Optional[int]
    bed_type: Optional[BedType]
    base_price: Optional[Decimal]
    status: Optional[RoomStatus]
    description: Optional[str]

    @field_validator("hotel_id")
    @classmethod
    def validate_id(cls, v):
        return validate_not_empty(v, "Hotel ID")

    @field_validator('floor')
    @classmethod
    def validate_floor(cls, v):
        return validate_positive_number(v, "Floor")

    @field_validator('base_price')
    @classmethod
    def validate_base_price(cls, v):
        validate_positive_number(v, "Price")
        return validate_vnd_decimal(v)
    
class AdminUpdateRoom(BaseModel):
    hotel_id: Optional[UUID] = None
    room_number: Optional[str] = None
    floor: Optional[int] = None
    bed_type: Optional[BedType] = None
    base_price: Optional[Decimal] = None
    status: Optional[RoomStatus] = None
    description: Optional[str] = None
    
    @field_validator("room_number")
    @classmethod
    def full_name_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Room number")

    @field_validator('floor')
    @classmethod
    def validate_floor(cls, v):
        return validate_positive_number(v, "Floor")

    @field_validator('base_price')
    @classmethod
    def validate_base_price(cls, v):
        validate_positive_number(v, "Price")
        return validate_vnd_decimal(v)