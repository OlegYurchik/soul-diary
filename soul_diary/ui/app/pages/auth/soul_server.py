from functools import partial

import flet
from pydantic import AnyHttpUrl

from soul_diary.ui.app.backend.soul import SoulBackend
from soul_diary.ui.app.controls.utils import in_progress
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle


class SoulServerPage(BasePage):
    def __init__(self, view: flet.View, local_storage: LocalStorage, url: str | None = None):
        self.local_storage = local_storage
        self.url = url

        super().__init__(view=view)

    def build(self) -> flet.Container:
        label = flet.Text("Soul Diary сервер")
        backend_button = flet.IconButton(
            icon=flet.icons.ARROW_BACK,
            on_click=self.callback_return_back,
        )
        top_row = flet.Row(
            controls=[backend_button, label],
            alignment=flet.MainAxisAlignment.START,
        )

        url_field = flet.TextField(
            width=300,
            label="URL",
            value=self.url,
            on_change=self.callback_change_url,
        )
        connect_button = flet.ElevatedButton(
            "Подключиться",
            width=300,
            height=50,
            on_click=partial(self.callback_connect, url_field=url_field),
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, url_field, connect_button],
                width=300,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_change_url(self, event: flet.ControlEvent):
        try:
            AnyHttpUrl(event.control.value or "")
        except:
            event.control.error_text = "Некорректный URL"
            self.url = None
        else:
            event.control.error_text = None
            self.url = event.control.value
        await event.control.update_async()

    @callback_error_handle
    async def callback_return_back(self, event: flet.ControlEvent):
        try:
            backend_url = AnyHttpUrl(self.url)
        except ValueError:
            pass
        else:
            await self.local_storage.add_shared_data(backend_data={"url": str(backend_url)})
        
        backend = await self.local_storage.get_shared_data("backend")
        if backend is not None:
            backend = BackendType(backend)

        from .backend import BackendPage
        await BackendPage(
            view=self.view,
            local_storage=self.local_storage,
            backend=backend,
        ).apply()

    @callback_error_handle
    async def callback_connect(self, event: flet.ControlEvent, url_field: flet.TextField):
        try:
            backend_url = AnyHttpUrl(self.url)
        except ValueError:
            url_field.error_text = "Некорректный URL"
            await url_field.update_async()
            return

        backend_client = SoulBackend(local_storage=self.local_storage, url=str(backend_url))
        async with in_progress(page=event.page):
            try:
                options = await backend_client.get_options()
            except:
                url_field.error_text = "Невозможно подключиться к серверу"
                await url_field.update_async()
                return

        await self.local_storage.add_shared_data(backend_data={"url": str(backend_url)})
        username = await self.local_storage.get_shared_data(key="username")
        password = await self.local_storage.get_shared_data(key="password")

        from .login import LoginPage
        await LoginPage(
            view=self.view,
            local_storage=self.local_storage,
            backend=BackendType.SOUL,
            backend_registration_enabled=options.registration_enabled,
            username=username,
            password=password,
        ).apply()
