from functools import partial

import flet

from soul_diary.ui.app.models import BackendType
from soul_diary.ui.app.pages.base import BasePage


class ChooseBackendPage(BasePage):
    BACKENDS = {
        BackendType.LOCAL: "Локально",
        BackendType.SOUL: "Soul Diary сервер",
    }

    def __init__(self, backend: BackendType | None = None):
        self.backend: BackendType | None = backend

        super().__init__()

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

    async def callback_change_backend(self, event: flet.ControlEvent):
        self.backend = BackendType(event.control.value)
        event.control.error_text = None
        await event.control.update_async()

    async def callback_choose_backend(self, event: flet.ControlEvent, dropdown: flet.Dropdown):
        if self.backend == BackendType.LOCAL:
            await self.credentials_view(page=event.page)
        elif self.backend == BackendType.SOUL:
            await self.soul_server_data_view(page=event.page)
        else:
            dropdown.error_text = "Выберите тип бекенда"
            await self.update_async()
