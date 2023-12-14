from functools import partial
from typing import Awaitable, Callable, Sequence

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.middlewares.base import BaseMiddleware
from soul_diary.ui.app.models import Emotion
from soul_diary.ui.app.routes import SENSE_ADD, SENSE_LIST
from .base import BaseView, view


class SenseAddView(BaseView):
    def __init__(
            self,
            local_storage: LocalStorage,
            middlewares: Sequence[BaseMiddleware | Callable[[flet.Page], Awaitable]] = (),
    ):
        self.title: flet.Text
        self.content_container: flet.Container
        self.buttons_row: flet.Row

        self.emotions: list[Emotion] = []
        self.feelings: str | None = None
        self.body: str | None = None
        self.desires: str | None = None

        super().__init__(local_storage=local_storage, middlewares=middlewares)

    async def clear(self):
        self.title.value = ""
        self.content_container.content = None
        self.buttons_row.controls = []

    def clear_data(self):
        self.emotions = []
        self.feelings = None
        self.body = None
        self.desires = None

    async def setup(self):
        # Top
        self.title = flet.Text()
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_container = flet.Container(
            content=flet.Row(
                [self.title, close_button],
                alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            ),
            margin=10,
        )

        # Center
        self.content_container = flet.Container()
        center_container = flet.Container(content=self.content_container, margin=10)

        # Bottom
        self.buttons_row = flet.Row()
        bottom_container = flet.Container(content=self.buttons_row, margin=10)

        # Build
        self.container.content = flet.Column(
            controls=[top_container, center_container, bottom_container],
            width=600,
        )
        self.container.alignment = flet.alignment.center

        self.view.route = SENSE_ADD
        self.view.vertical_alignment = flet.MainAxisAlignment.CENTER

    @view(initial=True)
    async def emotions_view(self, page: flet.Page):
        self.title.value = "Что ты чувствуешь?"

        chips = flet.Row(
            controls=[
                flet.Chip(
                    label=flet.Text(emotion.value),
                    show_checkmark=False,
                    selected=emotion.value in self.emotions,
                    on_select=partial(self.callback_choose_emotion, emotion=emotion),
                )
                for emotion in Emotion
            ],
            wrap=True,
        )
        self.content_container.content = flet.Column(
            controls=[chips],
        )

        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=self.callback_go_feelings_from_emotions,
        )
        self.buttons_row.controls = [next_button]
        self.buttons_row.alignment = flet.MainAxisAlignment.END

    @view()
    async def feelings_view(self, page: flet.Page):
        self.title.value = "Опиши свои чувства"

        self.content_container.content = flet.TextField(
            value=self.feelings,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_feelings,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_go_emotions_from_feelings,
        )
        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=self.callback_go_body_from_feelings,
        )
        self.buttons_row.controls = [previous_button, next_button]
        self.buttons_row.alignment = flet.MainAxisAlignment.SPACE_BETWEEN

    @view()
    async def body_view(self, page: flet.Page):
        self.title.value = "Опиши свои телесные ощущения"

        self.content_container.content = flet.TextField(
            value=self.body,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_body,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_go_feelings_from_body,
        )
        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=self.callback_go_desires_from_body,
        )
        self.buttons_row.controls = [previous_button, next_button]
        self.buttons_row.alignment = flet.MainAxisAlignment.SPACE_BETWEEN

    @view()
    async def desires_view(self, page: flet.Page):
        self.title.value = "Опиши свои желания на данный момент"

        self.content_container.content = flet.TextField(
            value=self.desires,
            multiline=True,
            min_lines=10,
            max_lines=10,
            on_change=self.callback_change_desires,
        )

        previous_button = flet.IconButton(
            flet.icons.ARROW_BACK,
            on_click=self.callback_go_body_from_desires,
        )
        apply_button = flet.IconButton(flet.icons.CREATE, on_click=self.callback_add_sense)
        self.buttons_row.controls = [previous_button, apply_button]
        self.buttons_row.alignment = flet.MainAxisAlignment.SPACE_BETWEEN

    async def callback_close(self, event: flet.ControlEvent):
        self.clear_data()
        await event.page.go_async(SENSE_LIST)

    async def callback_choose_emotion(self, event: flet.ControlEvent, emotion: Emotion):
        if event.control.selected:
            self.emotions.append(emotion)
            emotions_column = self.content_container.content
            if len(emotions_column.controls) > 1:
                emotions_column.controls = emotions_column.controls[:1]
                await event.page.update_async()
        else:
            self.emotions.remove(emotion)

    async def callback_change_feelings(self, event: flet.ControlEvent):
        self.feelings = event.control.value

    async def callback_change_body(self, event: flet.ControlEvent):
        self.body = event.control.value

    async def callback_change_desires(self, event: flet.ControlEvent):
        self.desires = event.control.value

    async def callback_go_emotions_from_feelings(self, event: flet.ControlEvent):
        await self.emotions_view(page=event.page)

    async def callback_go_feelings_from_emotions(self, event: flet.ControlEvent):
        if not self.emotions:
            emotions_column = self.content_container.content
            error_text = flet.Text("Выберите как минимум одну эмоцию", color=flet.colors.RED)
            emotions_column.controls = [emotions_column.controls[0], error_text]
            await event.page.update_async()
            return

        await self.feelings_view(page=event.page)

    async def callback_go_feelings_from_body(self, event: flet.ControlEvent):
        await self.feelings_view(page=event.page)

    async def callback_go_body_from_feelings(self, event: flet.ControlEvent):
        if self.feelings is None or not self.feelings.strip():
            self.content_container.content.error_text = "Коротко опиши свои чувства"
            await event.page.update_async()
            return

        await self.body_view(page=event.page)

    async def callback_go_body_from_desires(self, event: flet.ControlEvent):
        await self.body_view(page=event.page)

    async def callback_go_desires_from_body(self, event: flet.ControlEvent):
        if self.body is None or not self.body.strip():
            self.content_container.content.error_text = "Коротко опиши свои телесные ощущения"
            await event.page.update_async()
            return

        await self.desires_view(page=event.page)

    async def callback_add_sense(self, event: flet.ControlEvent):
        if self.desires is None or not self.desires.strip():
            self.content_container.content.error_text = "Коротко опиши свои желания"
            await event.page.update_async()
            return

        backend_client = await self.get_backend_client()
        async with self.in_progress(page=event.page):
            await backend_client.create_sense(
                emotions=self.emotions,
                feelings=self.feelings,
                body=self.body,
                desires=self.desires,
            )

        self.clear_data()
        await event.page.go_async(SENSE_LIST)
