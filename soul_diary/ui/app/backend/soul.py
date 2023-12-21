import uuid
from typing import Any

import httpx
import yarl

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from .base import BaseBackend
from .exceptions import (
    IncorrectCredentialsException,
    NonAuthenticatedException,
    RegistrationNotSupportedException,
    SenseNotFoundException,
    UserAlreadyExistsException,
)
from .models import EncryptedSense, EncryptedSenseList, Options


class SoulBackend(BaseBackend):
    BACKEND = BackendType.SOUL

    def __init__(
            self,
            url: yarl.URL | str,
            local_storage: LocalStorage,
            username: str | None = None,
            encryption_key: str | None = None,
            token: str | None = None,
    ):
        self._url = yarl.URL(url)
        self._client = httpx.AsyncClient()

        super().__init__(
            local_storage=local_storage,
            username=username,
            encryption_key=encryption_key,
            token=token,
        )

    def get_backend_data(self) -> dict[str, Any]:
        return {"url": str(self._url)}

    async def request(
            self,
            method: str,
            path: str,
            json = None,
            params: dict[str, Any] | None = None,
    ):
        url = self._url / path.lstrip("/")
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = await self._client.request(
            method=method,
            url=str(url),
            json=json,
            params=params,
            headers=headers,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise NonAuthenticatedException()
            else:
                raise exc

        return response.json()

    async def create_user(self, username: str, password: str) -> str:
        path = "/signup"
        data = {
            "username": username,
            "password": password,
        }

        try:
            response = await self.request(method="POST", path=path, json=data)
        except httpx.HTTPStatusError as exc:
            response = exc.response.json()
            if response == {"detail": "User already exists."}:
                raise UserAlreadyExistsException()
            elif response == {"detail": "Registration not supported."}:
                raise RegistrationNotSupportedException()
            else:
                raise exc

        return response["token"]

    async def auth(self, username: str, password: str) -> str:
        path = "/signin"
        data = {
            "username": username,
            "password": password,
        }

        try:
            response = await self.request(method="POST", path=path, json=data)
        except NonAuthenticatedException:
            raise IncorrectCredentialsException()

        return response["token"]

    async def deauth(self):
        path = "/logout"

        await self.request(method="POST", path=path)

    async def get_options(self) -> Options:
        path = "/options"

        response = await self.request(method="GET", path=path)

        return Options.model_validate(response)

    async def fetch_sense_list(
            self,
            cursor: str | None = None,
            limit: int = 10,
    ) -> EncryptedSenseList:
        path = "/senses/"
        params = {"limit": limit, "cursor": cursor}
        params = {key: value for key, value in params.items() if value is not None}

        response = await self.request(method="GET", path=path, params=params)
        data = [EncryptedSense.model_validate(sense) for sense in response["data"]]

        return EncryptedSenseList(
            data=data,
            limit=response["limit"],
            total_items=response["total_items"],
            previous=response["previous"],
            next=response["next"],
        )

    async def fetch_sense(self, sense_id: uuid.UUID) -> EncryptedSense:
        path = f"/senses/{sense_id}"

        try:
            response = await self.request(method="GET", path=path)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise SenseNotFoundException()
            else:
                raise exc

        return EncryptedSense.model_validate(response)

    async def pull_sense_data(
            self,
            data: str,
            sense_id: uuid.UUID | None = None,
    ) -> EncryptedSense:
        path = "/senses/" if sense_id is None else f"/senses/{sense_id}"
        request_data = {"data": data}

        try:
            response = await self.request(method="POST", path=path, json=request_data)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise SenseNotFoundException()
            else:
                raise exc

        return EncryptedSense.model_validate(response)

    async def delete_sense(self, sense_id: uuid.UUID):
        path = f"/senses/{sense_id}"

        try:
            await self.request(method="DELETE", path=path)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise SenseNotFoundException()
            else:
                raise exc
