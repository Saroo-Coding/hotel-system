from uuid import UUID

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    booking_id: UUID
    method: str
