from datetime import date
from uuid import UUID

from pydantic import BaseModel


class CreateBookingRequest(BaseModel):
    room_id: UUID
    guest_id: UUID
    checkin_date: date
    checkout_date: date
