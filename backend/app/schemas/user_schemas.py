from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, Literal

from app.core.validators import validate_not_empty, validate_password, validate_phone
from app.models.users import UserRole, UserStatus

class AdminCreateUser(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Literal["STAFF", "CUSTOMER"]

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
        return validate_phone(v)

    @model_validator(mode="after")
    def email_or_phone_required(self):
        if self.email is None and self.phone is None:
            raise ValueError("Account is required")
        return self

class StaffCreateCustomer(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Literal["CUSTOMER"]

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
        return validate_phone(v)

    @model_validator(mode="after")
    def email_or_phone_required(self):
        if self.email is None and self.phone is None:
            raise ValueError("Account is required")
        return self

class UserUpdateDTO(BaseModel):
    full_name: Optional[str] = None

    # ADMIN only
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

    @field_validator("full_name")
    @classmethod
    def full_name_validate(cls, v):
        if v is None:
            return v
        return validate_not_empty(v, "Full name")

class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password")
    @classmethod
    def old_password_validate(cls, v):
        return validate_not_empty(v, "Old password")

    @field_validator("new_password")
    @classmethod
    def new_password_validate(cls, v):
        validate_not_empty(v, "New password")
        return validate_password(v)
    
    @model_validator(mode="after")
    def passwords_not_match(self):
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from old password")
        return self