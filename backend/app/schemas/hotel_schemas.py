from pydantic import BaseModel, field_validator
from typing import Optional

from app.models.hotels import HotelStatus
from backend.app.core.validators import validate_not_empty, validate_phone_vn

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None

    status: Optional[HotelStatus] = None

    @field_validator("name")
    @classmethod
    def name_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Name")
    
    @field_validator("address")
    @classmethod
    def address_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Address")

    @field_validator("email")
    @classmethod
    def email_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Email")

    @field_validator("phone")
    @classmethod
    def phone_validate(cls, v):
        if v is None:
            return v
        validate_not_empty(v, "Phone")
        return validate_phone_vn(v)
    
    @field_validator("description")
    @classmethod
    def description_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Description")