from functools import partial

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import Emotion
from soul_diary.ui.app.pages.base import BasePage, callback_error_handle
from soul_diary.ui.app.routes import SENSE_LIST


class EmotionsPage(BasePage):
    def __init__(
            self,
            view: flet.View,
            local_storage: LocalStorage,
            emotions: list[Emotion] | None = None,
    ):
        self.local_storage = local_storage
        self.emotions = emotions or []

        super().__init__(view=view)

    def build(self) -> flet.Container:
        title = flet.Text("Что ты чувствуешь?")
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_row = flet.Row(
            controls=[title, close_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        error_text = flet.Text(
            "Выберите как минимум одну эмоцию",
            color=flet.colors.RED,
            visible=False,
        )
        emotions_chips = flet.Row(
            controls=[
                flet.Chip(
                    label=flet.Text(emotion.value),
                    show_checkmark=False,
                    selected=emotion.value in self.emotions,
                    on_select=partial(
                        self.callback_choose_emotion,
                        emotion=emotion,
                        error_text=error_text,
                    ),
                )
                for emotion in Emotion
            ],
            wrap=True,
        )
        emotions = flet.Column(controls=[emotions_chips, error_text])

        next_button = flet.IconButton(
            flet.icons.ARROW_FORWARD,
            on_click=partial(self.callback_next, error_text=error_text),
        )
        bottom_row = flet.Row(
            controls=[next_button],
            alignment=flet.MainAxisAlignment.END,
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, emotions, bottom_row],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    @callback_error_handle
    async def callback_close(self, event: flet.ControlEvent):
        await self.local_storage.clear_shared_data()
        await event.page.go_async(SENSE_LIST)

    @callback_error_handle
    async def callback_choose_emotion(
            self,
            event: flet.ControlEvent,
            emotion: Emotion,
            error_text: flet.Text,
    ):
        if event.control.selected:
            self.emotions.append(emotion)
            if error_text.visible:
                error_text.visible = False
                await error_text.update_async()
        else:
            self.emotions.remove(emotion)

    @callback_error_handle
    async def callback_next(self, event: flet.ControlEvent, error_text: flet.Text):
        if not self.emotions:
            error_text.visible = True
            await self.update_async()
            return
        await self.local_storage.add_shared_data(emotions=self.emotions)

        from .feelings import FeelingsPage

        await FeelingsPage(
            view=self.view,
            local_storage=self.local_storage,
            feelings=await self.local_storage.get_shared_data("feelings"),
        ).apply()
