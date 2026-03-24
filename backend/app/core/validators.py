from datetime import date, datetime
from decimal import Decimal
import re

def validate_password(password: str) -> str:
    if len(password) < 8:
        return "password_min_length"

    if not re.search(r"[A-Z]", password):
        return "password_uppercase"

    if not re.search(r"[a-z]", password):
        return "password_lowercase"

    if not re.search(r"\d", password):
        return "password_number"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "password_special"

    return None

def validate_email(email: str) -> bool:
    ''' Validate email format '''
    return bool(re.fullmatch(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email))

def validate_phone(phone: str) -> bool:
    ''' Validate Vietnamese phone number '''
    return bool(re.fullmatch(r"0[35789][0-9]{8}", (phone or "").strip()))

def validate_cccd(id_number: str) -> bool:
    ''' Validate CCCD: exactly 12 digits '''
    return bool(re.fullmatch(r"\d{12}", (id_number or "").strip()))

def validate_guest_search_keyword(keyword: str) -> str | None:
    '''
    Return matched field for guest search:
    - "id_number" for CCCD
    - "phone" for Vietnamese phone number
    - None if invalid
    '''
    keyword = (keyword or "").strip()
    if validate_cccd(keyword):
        return "id_number"
    if validate_phone(keyword):
        return "phone"
    return None

def validate_full_name(name: str) -> str:
    ''' Validate full name '''
    if len(name.strip()) < 2:
        return "full_name_too_short"

    if not re.fullmatch(r"[A-Za-zÀ-ỹ\s]+", name):
        return "full_name_invalid_chars"

    return None

def validate_birth_date(birth_date: datetime) -> datetime:
    if birth_date is None:
        return "birth_date_required"
    
    if isinstance(birth_date, datetime):
        birth = birth_date.date()
    elif isinstance(birth_date, date):
        birth = birth_date
    else:
        return "birth_date_type"

    today = date.today()

    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1

    if age < 18:
        return "birth_date_under_18"

    return None

def validate_not_empty(value: str, field_name="Field") -> str:
    ''' Validate field is not empty '''
    if value is None:
        return f"{field_name.lower()}_required"

    if not isinstance(value, str):
        return f"{field_name.lower()}_not_string"

    value = value.strip()
    if value == "":
        return f"{field_name.lower()}_empty"

    return None

def validate_positive_number(value: int | float, field_name="Value"):
    ''' Validate value is a positive number '''
    if value is None:
        return f"{field_name.lower()}_required"

    if value <= 0:
        return f"{field_name.lower()}_not_positive"
    return None

def validate_checkin_checkout(check_in, check_out):
    ''' Validate check-in and check-out dates '''
    if check_in >= check_out:
        return "checkout_after_checkin"
    return None

def validate_vnd_decimal(value: Decimal) -> Decimal:
    if value is None:
            return "base_price_required"

    if not isinstance(value, Decimal):
        return "base_price_not_decimal"

    if value.as_tuple().exponent != 0:
        return "base_price_has_decimal"

    if value <= 0:
        return "base_price_not_positive"

    return None
