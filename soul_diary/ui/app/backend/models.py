import uuid
from datetime import datetime

from pydantic import BaseModel


class SenseBackendData(BaseModel):
    id: uuid.UUID
    data: str
    created_at: datetime
