from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, Literal
from app.core.validators import validate_not_empty, validate_password, validate_phone_vn

class RegisterRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
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
        return validate_phone_vn(v)

    @field_validator("password")
    @classmethod
    def password_validate(cls, v):
        validate_not_empty(v, "Password")
        return validate_password(v)

    @model_validator(mode="after")
    def email_or_phone_required(self):
        if not self.email and not self.phone:
            raise ValueError("Account is required")
        return self