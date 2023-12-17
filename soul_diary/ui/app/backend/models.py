import uuid
from datetime import datetime

from pydantic import BaseModel

from soul_diary.ui.app.models import Sense


class EncryptedSense(BaseModel):
    id: uuid.UUID
    data: str
    created_at: datetime


class EncryptedSenseList(BaseModel):
    senses: list[EncryptedSense]


class SenseList(BaseModel):
    senses: list[Sense]


class Options(BaseModel):
    registration_enabled: bool
