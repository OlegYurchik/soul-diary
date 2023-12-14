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
        await self.raw_write("soul_diary.client", auth_data.model_dump(mode="json"))

    async def get_auth_data(self) -> AuthData | None:
        if not await self.raw_contains("soul_diary.client"):
            return None

        data = await self.raw_read("soul_diary.client")
        return AuthData.model_validate(data)

    async def remove_auth_data(self):
        if await self.raw_contains("soul_diary.client"):
            await self.raw_remove("soul_diary.client")

    async def clear(self):
        await self._client_storage.clear_async()

    async def raw_contains(self, key: str) -> bool:
        return await self._client_storage.contains_key_async(key)

    async def raw_read(self, key: str):
        return await self._client_storage.get_async(key)

    async def raw_write(self, key: str, value):
        await self._client_storage.set_async(key, value)

    async def raw_remove(self, key: str):
        await self._client_storage.remove_async(key)
