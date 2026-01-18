from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class BasePaginationResponse(BaseModel, Generic[T]):
    success: bool = True
    code: int = 200
    message: str = "Success"
    data: List[T]
    meta: PaginationMeta
