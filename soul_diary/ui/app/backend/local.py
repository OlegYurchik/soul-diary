import base64
import hashlib
import struct
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from soul_diary.ui.app.models import BackendType
from .base import BaseBackend
from .exceptions import (
    IncorrectCredentialsException,
    NonAuthenticatedException,
    SenseNotFoundException,
    UserAlreadyExistsException,
)
from .models import EncryptedSense, EncryptedSenseList, Options


class CursorData(BaseModel):
    created_at: datetime
    sense_id: uuid.UUID


class LocalBackend(BaseBackend):
    BACKEND = BackendType.LOCAL
    AUTH_BLOCK_TEMPLATE = "auth_block:{username}:{password}"
    AUTH_BLOCK_KEY_TEMPLATE = "soul_diary.backend.users.{username}.auth_block"
    SENSE_LIST_KEY_TEMPLATE = "soul_diary.backend.users.{username}.senses"

    def generate_auth_block(self, username: str, password: str) -> str:
        auth_block_data = (
            self.AUTH_BLOCK_TEMPLATE
            .format(username=username, password=password)
            .encode(self.ENCODING)
        )
        return hashlib.sha256(auth_block_data).hexdigest()

    def get_backend_data(self) -> dict[str, Any]:
        return {}

    async def create_user(self, username: str, password: str) -> str | None:
        auth_block_key = self.AUTH_BLOCK_KEY_TEMPLATE.format(username=username)

        if await self._local_storage.raw_contains(auth_block_key):
            raise UserAlreadyExistsException()

        auth_block = self.generate_auth_block(username=username, password=password)
        await self._local_storage.raw_write(auth_block_key, auth_block)
        return auth_block

    async def auth(self, username: str, password: str) -> str | None:
        auth_block_key = self.AUTH_BLOCK_KEY_TEMPLATE.format(username=username)

        if not await self._local_storage.raw_contains(auth_block_key):
            raise IncorrectCredentialsException()

        auth_block = self.generate_auth_block(username=username, password=password)
        actual_auth_block = await self._local_storage.raw_read(auth_block_key)
        if auth_block != actual_auth_block:
            raise IncorrectCredentialsException()

        return auth_block

    async def deauth(self):
        pass

    async def get_options(self) -> Options:
        return Options(registration_enabled=True)

    def cursor_encode(self, data: CursorData) -> str:
        datetime_bytes = bytes(struct.pack("d", data.created_at.timestamp()))
        sense_id_bytes = data.sense_id.bytes
        cursor_bytes = datetime_bytes + sense_id_bytes
        return base64.b64encode(cursor_bytes).decode(self.ENCODING)

    def cursor_decode(self, cursor: str) -> CursorData:
        cursor_bytes = base64.b64decode(cursor.encode(self.ENCODING))
        created_at = datetime.fromtimestamp(struct.unpack("d", cursor_bytes[:8])[0])
        sense_id = uuid.UUID(bytes=cursor_bytes[8:])
        return CursorData(created_at=created_at, sense_id=sense_id)

    async def fetch_sense_list(
            self,
            cursor: str | None = None,
            limit: int = 10,
    ) -> EncryptedSenseList:
        if not self.is_auth:
            raise NonAuthenticatedException()

        sense_list_key = self.SENSE_LIST_KEY_TEMPLATE.format(username=self._username)
        sense_list = await self._local_storage.raw_read(sense_list_key) or []
        total_items = len(sense_list)

        index = 0
        if cursor is not None:
            cursor_data = self.cursor_decode(cursor)
            cursor_sense = EncryptedSense.model_validate(sense_list[0])
            while (
                    index < total_items and
                    (cursor_data.created_at < cursor_sense.created_at or
                     cursor_data.created_at == cursor_sense.created_at and
                     cursor_data.sense_id < cursor_sense.id)
            ):
                index += 1
                cursor_sense = EncryptedSense.model_validate(sense_list[index])

        previous_cursor = None
        if index - limit >= 0:
            previous_pivot = EncryptedSense.model_validate(sense_list[index - limit])
            previous_cursor_data = CursorData(
                created_at=previous_pivot.created_at,
                sense_id=previous_pivot.id,
            )
            previous_cursor = self.cursor_encode(data=previous_cursor_data)
        next_cursor = None
        if index + limit < len(sense_list):
            next_pivot = EncryptedSense.model_validate(sense_list[index + limit])
            next_cursor_data = CursorData(
                created_at=next_pivot.created_at,
                sense_id=next_pivot.id,
            )
            next_cursor = self.cursor_encode(data=next_cursor_data)

        sense_list = sense_list[index:index + limit]
        data = [EncryptedSense.model_validate(sense) for sense in sense_list]
        return EncryptedSenseList(
            data=data,
            limit=limit,
            total_items=total_items,
            previous=previous_cursor,
            next=next_cursor,
        )

    async def fetch_sense(self, sense_id: uuid.UUID) -> EncryptedSense:
        sense_list = await self.fetch_sense_list()

        for sense in sense_list.senses:
            if sense.id == sense_id:
                return sense

        raise SenseNotFoundException()

    async def pull_sense_data(self, data: str, sense_id: uuid.UUID | None = None) -> EncryptedSense:
        sense_list_key = self.SENSE_LIST_KEY_TEMPLATE.format(username=self._username)
        sense_list = await self._local_storage.raw_read(sense_list_key)

        if sense_id is None:
            sense_ids = {uuid.UUID(sense["id"]) for sense in sense_list}
            sense_id = uuid.uuid4()
            while sense_id in sense_ids:
                sense_id = uuid.uuid4()
            sense = EncryptedSense(
                id=sense_id,
                data=data,
                created_at=datetime.utcnow(),
            )
            index = 0
            cursor_sense = EncryptedSense.model_validate(sense_list[index])
            while (
                index < len(sense_list) and
                (sense.created_at < cursor_sense.created_at or
                 sense.created_at == cursor_sense.created_at and
                 sense.id < cursor_sense.id)
            ):
                index += 1
            sense_list.insert(index, sense.model_dump(mode="json"))
        else:
            for index, sense in enumerate(sense_list):
                if sense.id == sense_id:
                    break
            else:
                raise SenseNotFoundException()

            sense = sense_list[index]
            sense.data = data
            sense_list[index] = sense.model_dump(mode="json")

        await self._local_storage.raw_write(sense_list_key, sense_list)

        return sense

    async def delete_sense(self, sense_id: uuid.UUID):
        sense_list_key = self.SENSE_LIST_KEY_TEMPLATE.format(username=self._username)
        sense_list = await self.fetch_sense_list()

        for index, sense in enumerate(sense_list):
            if sense.id == sense_id:
                break
        else:
            raise SenseNotFoundException()

        sense_list = sense_list[:index] + sense_list[index + 1:]

        await self._local_storage.raw_write(
            sense_list_key,
            [sense.model_dump(mode="json") for sense in sense_list],
        )
