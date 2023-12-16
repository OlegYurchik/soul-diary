from functools import partial

import flet
from soul_diary.ui.app.backend.utils import get_backend_client

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import Emotion
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle
from soul_diary.ui.app.routes import SENSE_LIST


class DesiresPage(BasePage):
    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            desires: str | None = None,
    ):
        self.local_storage = local_storage
        self.desires = desires

        super().__init__(view=view)

    def build(self) -> flet.Container:
        title = flet.Text("Опиши свои желания на данный момент")
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_row = flet.Row(
            controls=[title, close_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        desires_field = flet.TextField(
            value=self.desires,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_desires,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_previous,
        )
        add_button = flet.IconButton(
            flet.icons.CREATE,
            on_click=partial(self.callback_add_sense, desires_field=desires_field),
        )
        bottom_row = flet.Row(
            controls=[previous_button, add_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, desires_field, bottom_row],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_close(self, event: flet.ControlEvent):
        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)

    @callback_error_handle
    async def callback_change_desires(self, event: flet.ControlEvent):
        self.desires = event.control.value

    @callback_error_handle
    async def callback_previous(self, event: flet.ControlEvent):
        await self.local_storage.add_shared_data(desires=self.desires)
        body = await self.local_storage.get_shared_data("body")

        from .body import BodyPage
        await BodyPage(
            view=self.view,
            local_storage=self.local_storage,
            body=body,
        ).apply()

    @callback_error_handle
    async def callback_add_sense(self, event: flet.ControlEvent, desires_field: flet.TextField):
        if self.desires is None or not self.desires.strip():
            desires_field.error_text = "Коротко опиши свои желания"
            await desires_field.update_async()
            return

        emotions = await self.local_storage.get_shared_data("emotions") or []
        emotions = [Emotion(emotion) for emotion in emotions]
        feelings = await self.local_storage.get_shared_data("feelings")
        body = await self.local_storage.get_shared_data("body")
        backend_client = await get_backend_client(local_storage=self.local_storage)
        await backend_client.create_sense(
            emotions=emotions,
            feelings=feelings,
            body=body,
            desires=self.desires,
        )

        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)
