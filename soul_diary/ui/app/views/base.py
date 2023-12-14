import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable

import flet
from flet_route import Basket, Params

from soul_diary.ui.app.backend.base import BaseBackend
from soul_diary.ui.app.backend.exceptions import NonAuthenticatedException
from soul_diary.ui.app.backend.local import LocalBackend
from soul_diary.ui.app.backend.soul import SoulBackend
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType


def view(initial: bool = False, disabled: bool = False):
    def decorator(function: Callable):
        async def wrapper(self, page: flet.Page):
            await self.clear()

            await function(self, page=page)
            await page.update_async()

        wrapper._view_enabled = not disabled
        wrapper._view_initial = initial

        return wrapper
    return decorator


class MetaView(type):
    def __init__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]):
        super().__init__(name, bases, attrs)

        is_abstract = attrs.pop("is_abstract", False)
        if not is_abstract:
            cls.setup_class(attrs=attrs)

    def setup_class(cls, attrs: dict[str, Any]):
        initial_view = None
        for attr in attrs.values():
            view_enabled = getattr(attr, "_view_enabled", False)
            view_initial = getattr(attr, "_view_initial", False)
            if view_enabled and view_initial:
                if initial_view is not None:
                    raise ValueError(f"Initial view already defined: {initial_view.__name__}")
                initial_view = attr
        if initial_view is None:
            raise ValueError("Initial view must be defined")

        cls._initial_view = initial_view


class BaseView(metaclass=MetaView):
    BACKEND_MAPPING = {
        BackendType.LOCAL: LocalBackend,
        BackendType.SOUL: SoulBackend,
    }

    is_abstract = True
    _initial_view: Callable | None

    def __init__(self, local_storage: LocalStorage):
        self.local_storage = local_storage

        self.container: flet.Container
        self.view: flet.View

    async def entrypoint(self, page: flet.Page, params: Params, basket: Basket) -> flet.View:
        self.container = flet.Container()
        self.view = flet.View(controls=[self.container])

        await self.setup()
        await self.clear()
        self.clear_data()

        loop = asyncio.get_running_loop()
        loop.create_task(self.run_initial_view(page=page))

        return self.view

    async def setup(self):
        pass

    async def clear(self):
        pass

    def clear_data(self):
        pass

    @asynccontextmanager
    async def in_progress(self, page: flet.Page, tooltip: str | None = None):
        self.container.disabled = True
        page.splash = flet.Column(
            controls=[flet.Container(
                content=flet.ProgressRing(tooltip=tooltip),
                alignment=flet.alignment.center,
            )],
            alignment=flet.MainAxisAlignment.CENTER,
        )
        await page.update_async()

        yield

        self.container.disabled = False
        page.splash = None
        await page.update_async()

    async def run_initial_view(self, page: flet.Page):
        if self._initial_view is not None:
            await self._initial_view(page=page)

    async def get_backend_client(self) -> BaseBackend:
        auth_data = await self.local_storage.get_auth_data()
        if auth_data is None:
            raise NonAuthenticatedException()

        backend_client_class = self.BACKEND_MAPPING.get(auth_data.backend, None)
        if backend_client_class is None:
            raise

        return backend_client_class(
            local_storage=self.local_storage,
            username=auth_data.username,
            encryption_key=auth_data.encryption_key,
            token=auth_data.token,
            **auth_data.backend_data,
        )
