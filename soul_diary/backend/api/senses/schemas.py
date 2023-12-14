import uuid
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, PositiveInt


class CreateSenseRequest(BaseModel):
    data: str


class UpdateSenseRequest(BaseModel):
    data: str


class SenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: str
    created_at: datetime


class Pagination(BaseModel):
    page: PositiveInt = 1
    limit: PositiveInt = 10


class SenseListResponse(BaseModel):
    data: list[SenseResponse]
