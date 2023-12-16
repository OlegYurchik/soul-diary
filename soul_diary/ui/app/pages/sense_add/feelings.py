from functools import partial

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle
from soul_diary.ui.app.routes import SENSE_LIST


class FeelingsPage(BasePage):
    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            feelings: str | None = None,
    ):
        self.local_storage = local_storage
        self.feelings = feelings

        super().__init__(view=view)

    def build(self) -> flet.Container:
        title = flet.Text("Опиши свои чувства")
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_row = flet.Row(
            controls=[title, close_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        feelings_field = flet.TextField(
            value=self.feelings,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_feelings,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_previous,
        )
        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=partial(self.callback_next, feelings_field=feelings_field),
        )
        bottom_row = flet.Row(
            controls=[previous_button, next_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, feelings_field, bottom_row],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_close(self, event: flet.ControlEvent):
        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)

    @callback_error_handle
    async def callback_change_feelings(self, event: flet.ControlEvent):
        self.feelings = event.control.value

    @callback_error_handle
    async def callback_previous(self, event: flet.ControlEvent):
        await self.local_storage.add_shared_data(feelings=self.feelings)
        emotions = await self.local_storage.get_shared_data("emotions")

        from .emotions import EmotionsPage
        await EmotionsPage(
            view=self.view,
            local_storage=self.local_storage,
            emotions=emotions,
        ).apply()

    @callback_error_handle
    async def callback_next(self, event: flet.ControlEvent, feelings_field: flet.TextField):
        if self.feelings is None or not self.feelings.strip():
            feelings_field.error_text = "Коротко опиши свои чувства"
            await feelings_field.update_async()
            return

        await self.local_storage.add_shared_data(feelings=self.feelings)
        body = await self.local_storage.get_shared_data("body")

        from .body import BodyPage
        await BodyPage(
            view=self.view,
            local_storage=self.local_storage,
            body=body,
        ).apply()
