import uuid

from pydantic import AwareDatetime, BaseModel


class SenseBackendData(BaseModel):
    id: uuid.UUID
    data: str
    created_at: AwareDatetime
