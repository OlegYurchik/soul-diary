from functools import partial

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle


class BackendPage(BasePage):
    BACKENDS = {
        BackendType.LOCAL: "Локально",
        BackendType.SOUL: "Soul Diary сервер",
    }

    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            backend: BackendType | None = None,
    ):
        self.local_storage = local_storage
        self.backend = backend

        super().__init__(view=view)

    def build(self) -> flet.Container:
        label = flet.Container(
            content=flet.Text("Выберите сервер"),
            alignment=flet.alignment.center,
        )
        dropdown = flet.Dropdown(
            label="Бэкенд",
            options=[
                flet.dropdown.Option(text=text, key=key.value)
                for key, text in self.BACKENDS.items()
            ],
            value=None if self.backend is None else self.backend.value,
            on_change=self.callback_change_backend,
        )
        connect_button = flet.ElevatedButton(
            "Выбрать",
            width=300,
            height=50,
            on_click=partial(self.callback_choose_backend, dropdown=dropdown),
        )

        return flet.Container(
            content=flet.Column(
                controls=[label, dropdown, connect_button],
                width=300,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_change_backend(self, event: flet.ControlEvent):
        self.backend = BackendType(event.control.value)
        event.control.error_text = None
        await event.control.update_async()

    @callback_error_handle
    async def callback_choose_backend(self, event: flet.ControlEvent, dropdown: flet.Dropdown):
        if self.backend is None or self.backend not in BackendType:
            dropdown.error_text = "Выберите тип бекенда"
            await self.update_async()
            return

        await self.local_storage.add_shared_data(backend=self.backend.value)

        if self.backend == BackendType.LOCAL:
            from .login import LoginPage

            await LoginPage(
                view=self.view,
                local_storage=self.local_storage,
                backend=self.backend,
                backend_registration_enabled=True,
                username=await self.local_storage.get_shared_data(key="username"),
                password=await self.local_storage.get_shared_data(key="password"),
            ).apply()
        elif self.backend == BackendType.SOUL:
            from .soul_server import SoulServerPage

            backend_data = await self.local_storage.get_shared_data(key="backend_data")
            if backend_data is None:
                backend_data = {}
            await SoulServerPage(
                view=self.view,
                local_storage=self.local_storage,
                url=backend_data.get("url"),
            ).apply()
