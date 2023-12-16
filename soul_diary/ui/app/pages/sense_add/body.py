from functools import partial

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle
from soul_diary.ui.app.routes import SENSE_LIST


class BodyPage(BasePage):
    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            body: str | None = None,
    ):
        self.local_storage = local_storage
        self.body = body

        super().__init__(view=view)

    def build(self) -> flet.Container:
        title = flet.Text("Опиши свои телесные ощущения")
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_row = flet.Row(
            controls=[title, close_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        body_field = flet.TextField(
            value=self.body,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_body,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_previous,
        )
        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=partial(self.callback_next, body_field=body_field),
        )
        bottom_row = flet.Row(
            controls=[previous_button, next_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, body_field, bottom_row],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_close(self, event: flet.ControlEvent):
        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)

    @callback_error_handle
    async def callback_change_body(self, event: flet.ControlEvent):
        self.body = event.control.value

    @callback_error_handle
    async def callback_previous(self, event: flet.ControlEvent):
        await self.local_storage.add_shared_data(body=self.body)
        feelings = await self.local_storage.get_shared_data("feelings")

        from .feelings import FeelingsPage
        await FeelingsPage(
            view=self.view,
            local_storage=self.local_storage,
            feelings=feelings,
        ).apply()

    @callback_error_handle
    async def callback_next(self, event: flet.ControlEvent, body_field: flet.TextField):
        if self.body is None or not self.body.strip():
            body_field.error_text = "Коротко опиши свои телесные ощущения"
            await body_field.update_async()
            return

        await self.local_storage.add_shared_data(body=self.body)
        desires = await self.local_storage.get_shared_data("desires")

        from .desires import DesiresPage
        await DesiresPage(
            view=self.view,
            local_storage=self.local_storage,
            desires=desires,
        ).apply()
