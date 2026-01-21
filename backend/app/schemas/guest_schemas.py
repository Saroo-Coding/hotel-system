from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import date
from typing import Optional

from app.core.validators import validate_birth_date, validate_full_name, validate_not_empty, validate_phone_vn, validate_vnd_decimal, validate_positive_number

class StaffCreateGuest(BaseModel):
    user_id: Optional[UUID] = None
    full_name: str
    id_type: str
    id_number: str
    date_of_birth: date
    gender: str
    nationality: str
    phone: str
    email: EmailStr

    @field_validator('full_name')
    def validate_full_name_field(cls, v):
        return validate_full_name(v)

    @field_validator('phone')
    def validate_phone_field(cls, v):
        if v is not None:
            return validate_phone_vn(v)
        return v

    @field_validator('date_of_birth')
    def validate_birth_date_field(cls, v):
        if v is not None:
            return validate_birth_date(v)
        return v

    @field_validator('id_number')
    def validate_id_number_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "ID number")
        return v

    @field_validator('id_type')
    def validate_id_type_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "ID type")
        return v

    @field_validator('gender')
    def validate_gender_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "Gender")
        return v

    @field_validator('nationality')
    def validate_nationality_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "Nationality")
        return v

class UpdateGuest(BaseModel):
    full_name: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator('full_name')
    def validate_full_name_field(cls, v):
        return validate_full_name(v)

    @field_validator('phone')
    def validate_phone_field(cls, v):
        if v is not None:
            return validate_phone_vn(v)
        return v

    @field_validator('date_of_birth')
    def validate_birth_date_field(cls, v):
        if v is not None:
            return validate_birth_date(v)
        return v

    @field_validator('id_number')
    def validate_id_number_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "ID number")
        return v

    @field_validator('id_type')
    def validate_id_type_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "ID type")
        return v

    @field_validator('gender')
    def validate_gender_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "Gender")
        return v

    @field_validator('nationality')
    def validate_nationality_field(cls, v):
        if v is not None:
            return validate_not_empty(v, "Nationality")
        return v