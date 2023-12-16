import base64
import hashlib
import json
import uuid
from typing import Any

from Cryptodome.Cipher import AES

from soul_diary.ui.app.backend.models import SenseBackendData
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType, Emotion, Options, Sense


class BaseBackend:
    BACKEND: BackendType
    NONCE = b"\x00" * 16
    MODE = AES.MODE_EAX
    ENCODING = "utf-8"
    ENCRYPTION_KEY_TEMPLATE = "backend:encryption_key:{username}:{password}"

    def __init__(
            self,
            local_storage: LocalStorage,
            username: str | None = None,
            encryption_key: str | None = None,
            token: str | None = None,
    ):
        self._local_storage = local_storage
        self._username = username
        self._encryption_key = (
            None
            if encryption_key is None else
            encryption_key.encode(self.ENCODING)
        )
        self._token = token

    def generate_encryption_key(self, username: str, password: str) -> bytes:
        data = (
            self.ENCRYPTION_KEY_TEMPLATE
            .format(username=username, password=password)
            .encode(self.ENCODING)
        )
        return hashlib.sha256(data).hexdigest().encode(self.ENCODING)[:16]

    def encode(self, data: dict[str, Any]) -> str:
        if self._encryption_key is None:
            raise ValueError("Need crypto key. For generating key you should authenticate.")

        cipher = AES.new(self._encryption_key, self.MODE, nonce=self.NONCE)

        data_string = json.dumps(data)
        data_bytes = data_string.encode(self.ENCODING)
        data_bytes_encoded, _ = cipher.encrypt_and_digest(data_bytes)
        data_bytes_encoded_base64 = base64.b64encode(data_bytes_encoded).decode(self.ENCODING)
        
        return data_bytes_encoded_base64

    def decode(self, data: str) -> dict[str, Any]:
        if self._encryption_key is None:
            raise ValueError("Need crypto key. For generating key you should authenticate.")

        cipher = AES.new(self._encryption_key, self.MODE, nonce=self.NONCE)

        data_bytes_encoded = base64.b64decode(data)
        data_bytes = cipher.decrypt(data_bytes_encoded)
        data_string = data_bytes.decode(self.ENCODING)
        data_decoded = json.loads(data_string)

        return data_decoded

    def convert_sense_data_to_sense(self, sense_data: SenseBackendData) -> Sense:
        return Sense(
            id=sense_data.id,
            created_at=sense_data.created_at,
            **self.decode(sense_data.data),
        )

    async def registration(self, username: str, password: str):
        self._token = await self.create_user(username=username, password=password)
        self._encryption_key = self.generate_encryption_key(username=username, password=password)
        self._username = username
        await self._local_storage.store_auth_data(
            backend=self.BACKEND,
            backend_data=self.get_backend_data(),
            username=self._username,
            encryption_key=self._encryption_key.decode(self.ENCODING),
            token=self._token,
        )

    async def login(self, username: str, password: str):
        self._token = await self.auth(username=username, password=password)
        self._encryption_key = self.generate_encryption_key(username=username, password=password)
        self._username = username
        await self._local_storage.store_auth_data(
            backend=self.BACKEND,
            backend_data=self.get_backend_data(),
            username=self._username,
            encryption_key=self._encryption_key.decode(self.ENCODING),
            token=self._token,
        )

    async def logout(self):
        await self.deauth()
        self._token = None
        self._encryption_key = None
        self._username = None
        await self._local_storage.clear_auth_data()

    @property
    def is_auth(self) -> bool:
        return all((self._token, self._encryption_key))

    async def get_sense_list(self, page: int = 1, limit: int = 10) -> list[Sense]:
        sense_data_list = await self.fetch_sense_list(page=page, limit=limit) 
        return [
            self.convert_sense_data_to_sense(sense_data)
            for sense_data in sense_data_list
        ]

    async def create_sense(
            self,
            emotions: list[Emotion],
            feelings: str,
            body: str,
            desires: str,
    ) -> Sense:
        data = {
            "emotions": emotions,
            "feelings": feelings,
            "body": body,
            "desires": desires
        }
        encoded_data = self.encode(data)

        sense_data = await self.pull_sense_data(data=encoded_data)

        return self.convert_sense_data_to_sense(sense_data)

    async def get_sense(self, sense_id: uuid.UUID) -> Sense:
        sense_data = await self.fetch_sense(sense_id=sense_id)
        return self.convert_sense_data_to_sense(sense_data)

    async def edit_sense(
            self,
            sense_id: uuid.UUID,
            emotions: list[Emotion] | None = None,
            feelings: str | None = None,
            body: str | None = None,
            desires: str | None = None,
    ):
        data = {
            "emotions": emotions,
            "feelings": feelings,
            "body": body,
            "desires": desires,
        }
        encoded_data = self.encode(data)

        sense_data = await self.pull_sense_data(data=encoded_data, sense_id=sense_id)

        return self.convert_sense_data_to_sense(sense_data)

    def get_backend_data(self) -> dict[str, Any]:
        raise NotImplementedError

    async def create_user(self, username: str, password: str) -> str:
        raise NotImplementedError

    async def auth(self, username: str, password: str) -> str:
        raise NotImplementedError

    async def deauth(self):
        raise NotImplementedError

    async def get_options(self) -> Options:
        raise NotImplementedError

    async def fetch_sense_list(
            self,
            page: int = 1,
            limit: int = 10,
    ) -> list[SenseBackendData]:
        raise NotImplementedError

    async def fetch_sense(self, sense_id: uuid.UUID) -> SenseBackendData:
        raise NotImplementedError

    async def pull_sense_data(
            self,
            data: str,
            sense_id: uuid.UUID | None = None,
    ) -> SenseBackendData:
        raise NotImplementedError

    async def delete_sense(self, sense_id: uuid.UUID):
        raise NotImplementedError
