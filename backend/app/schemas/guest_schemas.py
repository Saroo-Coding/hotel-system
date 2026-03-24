from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class StaffCreateGuest(BaseModel):
    user_id: Optional[UUID] = None
    full_name: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class UpdateGuest(BaseModel):
    full_name: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
