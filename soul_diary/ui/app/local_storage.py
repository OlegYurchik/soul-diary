from typing import Any

from pydantic import BaseModel

from soul_diary.ui.app.models import BackendType


class AuthData(BaseModel):
    backend: BackendType
    backend_data: dict[str, Any]
    username: str
    encryption_key: str
    token: str


class LocalStorage:
    AUTH_DATA_KEY = "soul_diary.client.auth_data"
    SHARED_DATA_KEY = "soul_diary.client.shared_data"

    def __init__(self, client_storage):
        self._client_storage = client_storage

    async def store_auth_data(
            self,
            backend: BackendType,
            backend_data: dict[str, Any],
            username: str,
            encryption_key: str,
            token: str,
    ):
        auth_data = AuthData(
            backend=backend,
            backend_data=backend_data,
            username=username,
            encryption_key=encryption_key,
            token=token,
        )
        await self.raw_write(self.AUTH_DATA_KEY, auth_data.model_dump(mode="json"))

    async def get_auth_data(self) -> AuthData | None:
        if not await self.raw_contains(self.AUTH_DATA_KEY):
            return None

        data = await self.raw_read(self.AUTH_DATA_KEY)
        return AuthData.model_validate(data)

    async def clear_auth_data(self):
        if await self.raw_contains(self.AUTH_DATA_KEY):
            await self.raw_remove(self.AUTH_DATA_KEY)

    async def add_shared_data(self, **kwargs):
        if await self.raw_contains(self.SHARED_DATA_KEY):
            tmp_data = await self.raw_read(self.SHARED_DATA_KEY)
        else:
            tmp_data = {}

        tmp_data.update(kwargs)
        await self.raw_write(self.SHARED_DATA_KEY, tmp_data)

    async def get_shared_data(self, key: str):
        if not await self.raw_contains(self.SHARED_DATA_KEY):
            return None

        tmp_data = await self.raw_read(self.SHARED_DATA_KEY)
        return tmp_data.get(key)

    async def clear_shared_data(self):
        if not await self.raw_contains(self.SHARED_DATA_KEY):
            return

        await self.raw_remove(self.SHARED_DATA_KEY)

    async def raw_contains(self, key: str) -> bool:
        return await self._client_storage.contains_key_async(key)

    async def raw_read(self, key: str):
        return await self._client_storage.get_async(key)

    async def raw_write(self, key: str, value):
        await self._client_storage.set_async(key, value)

    async def raw_remove(self, key: str):
        await self._client_storage.remove_async(key)
