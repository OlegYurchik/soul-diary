import asyncio
from typing import Any

import flet

from soul_diary.ui.app.backend.soul import SoulBackend
from soul_diary.ui.app.controls.utils import in_progress
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.pages.auth.backend import BackendPage
from soul_diary.ui.app.pages.auth.login import LoginPage
from soul_diary.ui.app.pages.auth.soul_server import SoulServerPage
from soul_diary.ui.app.pages.base import BasePage
from .base import BaseView


class AuthView(BaseView):
    def __init__(
            self,
            backend: BackendType | None = None,
            backend_data: dict[str, Any] | None = None,
    ):
        self.backend = backend
        self.backend_data = backend_data

    async def entrypoint(self, page: flet.Page) -> BasePage:
        local_storage = LocalStorage(client_storage=page.client_storage)
        if self.backend == BackendType.SOUL:
            return await self.connect_to_soul_server(
                page=page,
                local_storage=local_storage,
            )
        elif self.backend == BackendType.LOCAL:
            return LoginPage(
                view=self.view,
                backend=self.backend,
                backend_data=self.backend_data,
                backend_registration_enabled=True,
                local_storage=local_storage,
                can_return_back=False,
            )
        else:
            return BackendPage(view=self.view, local_storage=local_storage)

    async def connect_to_soul_server(self, page: flet.Page, local_storage: LocalStorage) -> BasePage:
        backend_data = await local_storage.get_shared_data("backend_data")
        if backend_data is None:
            backend_data = {}
        soul_backend_client = SoulBackend(
            local_storage=local_storage,
            url=self.backend_data.get("url") or backend_data.get("url"),
        )
        try:
            async with in_progress(page=page):
                options = await soul_backend_client.get_options()
        except:
            return SoulServerPage(
                view=self.view,
                local_storage=local_storage,
                url=self.backend_data.get("url") or backend_data.get("url"),
            )
        else:
            return LoginPage(
                view=self.view,
                local_storage=local_storage,
                backend=self.backend,
                backend_data=self.backend_data,
                backend_registration_enabled=options.registration_enabled,
                can_return_back=False,
            )
