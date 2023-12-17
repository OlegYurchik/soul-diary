import hashlib
import uuid
from datetime import datetime
from typing import Any

from soul_diary.ui.app.models import BackendType
from .base import BaseBackend
from .exceptions import (
    IncorrectCredentialsException,
    NonAuthenticatedException,
    SenseNotFoundException,
    UserAlreadyExistsException,
)
from .models import EncryptedSense, EncryptedSenseList, Options


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

    async def fetch_sense_list(
            self,
            cursor: str | None = None,
            limit: int = 10,
    ) -> EncryptedSenseList:
        if not self.is_auth:
            raise NonAuthenticatedException()

        sense_list_key = self.SENSE_LIST_KEY_TEMPLATE.format(username=self._username)
        sense_list = await self._local_storage.raw_read(sense_list_key) or []
        senses = [EncryptedSense.model_validate(sense) for sense in sense_list]
        return EncryptedSenseList(senses=senses)

    async def fetch_sense(self, sense_id: uuid.UUID) -> EncryptedSense:
        sense_list = await self.fetch_sense_list()

        for sense in sense_list.senses:
            if sense.id == sense_id:
                return sense

        raise SenseNotFoundException()

    async def pull_sense_data(self, data: str, sense_id: uuid.UUID | None = None) -> EncryptedSense:
        sense_list_key = self.SENSE_LIST_KEY_TEMPLATE.format(username=self._username)
        sense_list = await self.fetch_sense_list()

        if sense_id is None:
            sense_ids = {sense.id for sense in sense_list.senses}
            sense_id = uuid.uuid4()
            while sense_id in sense_ids:
                sense_id = uuid.uuid4()
            sense = EncryptedSense(
                id=sense_id,
                data=data,
                created_at=datetime.now().astimezone(),
            )
            sense_list.senses.insert(0, sense)
        else:
            for index, sense in enumerate(sense_list):
                if sense.id == sense_id:
                    break
            else:
                raise SenseNotFoundException()

            sense = sense_list.senses[index]
            sense.data = data
            sense_list.senses[index] = sense
        
        await self._local_storage.raw_write(
            sense_list_key,
            [sense.model_dump(mode="json") for sense in sense_list.senses],
        )

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
