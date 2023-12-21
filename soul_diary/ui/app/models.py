import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, constr, field_validator


class Emotion(str, enum.Enum):
    SADNESS = "грусть"
    JOY = "радость"
    CALMNESS = "спокойствие"
    IRRITATION = "раздражение"
    ANGER = "злость"
    FEAR = "страх"
    SHAME = "стыд"
    GUILD = "вина"
    RESENTMENT = "обида"
    BOREDOM = "скука"
    ANXIETY = "тревога"
    COURAGE = "смелость"
    PRIDE = "гордость"
    ENERGY = "энергичность"
    THANKFULNESS = "благодарность"
    PLEASURE = "удовольствие"
    DELIGHT = "восхищение"


class EmotionLegacy(str, enum.Enum):
    MADNESS = "бешенство"
    FORCE = "сила"


class BackendType(str, enum.Enum):
    LOCAL = "local"
    SOUL = "soul"


class Sense(BaseModel):
    id: uuid.UUID
    emotions: list[Emotion | EmotionLegacy] = []
    feelings: constr(min_length=1, strip_whitespace=True)
    body: constr(min_length=1, strip_whitespace=True)
    desires: constr(min_length=1, strip_whitespace=True)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def created_at_validator(cls, created_at: datetime) -> datetime:
        created_at = created_at.replace(tzinfo=timezone.utc)
        local_timezone = datetime.now().astimezone().tzinfo
        return created_at.astimezone(local_timezone)
