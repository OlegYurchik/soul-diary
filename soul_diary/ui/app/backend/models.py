import uuid
from datetime import datetime

from pydantic import BaseModel, NonNegativeInt

from soul_diary.ui.app.models import Sense


class Paginated(BaseModel):
    data: list
    limit: int
    total_items: NonNegativeInt
    previous: str | None = None
    next: str | None = None


class EncryptedSense(BaseModel):
    id: uuid.UUID
    data: str
    created_at: datetime


class EncryptedSenseList(Paginated):
    data: list[EncryptedSense]


class SenseList(Paginated):
    data: list[Sense]


class Options(BaseModel):
    registration_enabled: bool
