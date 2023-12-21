import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, NonNegativeInt


class Pagination(BaseModel):
    cursor: str | None = None
    limit: int = 10


class PaginatedResponse(BaseModel):
    data: list
    limit: int
    total_items: NonNegativeInt
    previous: str | None = None
    next: str | None = None


class CreateSenseRequest(BaseModel):
    data: str


class UpdateSenseRequest(BaseModel):
    data: str


class SenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: str
    created_at: datetime


class SenseListResponse(PaginatedResponse):
    data: list[SenseResponse]
