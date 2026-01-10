import datetime
import re

# TODO: Chuẩn hoá error response format

def validate_password(password: str) -> str:
    ''' Validate password strength '''
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least 1 uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least 1 lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least 1 number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least 1 special character")

    return password

def validate_username(username: str) -> str:
    ''' Validate username format '''
    if not re.fullmatch(r"[a-zA-Z0-9_]{4,20}", username):
        raise ValueError(
            "Username must be 4-20 characters, only letters, numbers, underscore"
        )
    return username

def validate_phone_vn(phone: str) -> str:
    ''' Validate Vietnamese phone number '''
    if not re.fullmatch(r"0[3|5|7|8|9][0-9]{8}", phone):
        raise ValueError("Invalid Vietnamese phone number")
    return phone

def validate_full_name(name: str) -> str:
    ''' Validate full name '''
    if len(name.strip()) < 2:
        raise ValueError("Full name is too short")

    if not re.fullmatch(r"[A-Za-zÀ-ỹ\s]+", name):
        raise ValueError("Full name contains invalid characters")

    return name.strip()

def validate_birth_date(birth_date: datetime) -> datetime:
    ''' Validate birth date (user must be at least 18 years old) '''
    age = (datetime.now() - birth_date).days / 365
    if age < 18:
        raise ValueError("User must be at least 18 years old")
    return birth_date

def validate_not_empty(value: str, field_name="Field") -> str:
    ''' Validate field is not empty '''
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value.strip()

def validate_positive_number(value: int | float, field_name="Value"):
    ''' Validate value is a positive number '''
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value

def validate_checkin_checkout(check_in, check_out):
    ''' Validate check-in and check-out dates '''
    if check_in >= check_out:
        raise ValueError("Check-out date must be after check-in date")
    return check_in, check_out
