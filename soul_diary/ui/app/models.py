import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, constr


class Emotion(str, enum.Enum):
    JOY = "радость"
    FORCE = "сила"
    CALMNESS = "спокойствие"
    SADNESS = "грусть"
    MADNESS = "бешенство"
    FEAR = "страх"


class BackendType(str, enum.Enum):
    LOCAL = "local"
    SOUL = "soul"


class Sense(BaseModel):
    id: uuid.UUID
    emotions: list[Emotion] = []
    feelings: constr(min_length=1, strip_whitespace=True)
    body: constr(min_length=1, strip_whitespace=True)
    desires: constr(min_length=1, strip_whitespace=True)
    created_at: datetime
