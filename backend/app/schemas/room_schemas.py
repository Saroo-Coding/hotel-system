from uuid import UUID
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional
from decimal import Decimal

class RoomStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    MAINTENANCE = "MAINTENANCE"
    BOOKED = "BOOKED"

class BedType(str, Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"

class AdminCreateRoom(BaseModel):
    hotel_id: UUID
    room_number: str
    floor: int
    bed_type: BedType
    base_price: Decimal
    status: RoomStatus
    description: Optional[str] = None

    @field_validator("hotel_id", mode="before")
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            value = v.strip()
            if not value:
                raise ValueError("rooms.validation.hotelRequired")
            try:
                return UUID(value)
            except ValueError:
                raise ValueError("rooms.validation.hotelInvalid")
        raise ValueError("rooms.validation.hotelInvalid")

    @field_validator("room_number", mode="before")
    @classmethod
    def validate_room_number(cls, v):
        if not isinstance(v, str):
            raise ValueError("rooms.validation.roomNumberRequired")
        value = v.strip()
        if not value:
            raise ValueError("rooms.validation.roomNumberRequired")
        return value

    @field_validator('floor')
    @classmethod
    def validate_floor(cls, v):
        if v is None:
            raise ValueError("rooms.validation.floorRequired")
        if v <= 0:
            raise ValueError("rooms.validation.floorRequired")
        return v

    @field_validator('base_price')
    @classmethod
    def validate_base_price(cls, v):
        if v is None:
            raise ValueError("rooms.validation.basePriceRequired")
        if v <= 0:
            raise ValueError("rooms.validation.basePriceRequired")
        if v.as_tuple().exponent != 0:
            raise ValueError("rooms.validation.basePriceInvalid")
        return v
    
class AdminUpdateRoom(BaseModel):
    hotel_id: Optional[UUID] = None
    room_number: Optional[str] = None
    floor: Optional[int] = None
    bed_type: Optional[BedType] = None
    base_price: Optional[Decimal] = None
    status: Optional[RoomStatus] = None
    description: Optional[str] = None

    @field_validator("hotel_id", mode="before")
    @classmethod
    def validate_update_hotel_id(cls, v):
        if v is None:
            return v
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            value = v.strip()
            if not value:
                raise ValueError("rooms.validation.hotelRequired")
            try:
                return UUID(value)
            except ValueError:
                raise ValueError("rooms.validation.hotelInvalid")
        raise ValueError("rooms.validation.hotelInvalid")
    
    @field_validator("room_number", mode="before")
    @classmethod
    def full_name_validate(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("rooms.validation.roomNumberRequired")
        value = v.strip()
        if not value:
            raise ValueError("rooms.validation.roomNumberRequired")
        return value

    @field_validator('floor')
    @classmethod
    def validate_floor(cls, v):
        if v is None:
            return v
        if v <= 0:
            raise ValueError("rooms.validation.floorRequired")
        return v

    @field_validator('base_price')
    @classmethod
    def validate_base_price(cls, v):
        if v is None:
            return v
        if v <= 0:
            raise ValueError("rooms.validation.basePriceRequired")
        if v.as_tuple().exponent != 0:
            raise ValueError("rooms.validation.basePriceInvalid")
        return v
