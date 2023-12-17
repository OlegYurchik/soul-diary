import uuid

import flet
from soul_diary.ui.app.backend.utils import get_backend_client

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage
from soul_diary.ui.app.routes import SENSE_LIST


class SensePage(BasePage):
    def __init__(self, view: flet.View, local_storage: LocalStorage, sense_id: uuid.UUID):
        self.local_storage = local_storage
        self.sense_id = sense_id

        self.title: flet.Text
        self.emotions: flet.Row

        super().__init__(view=view)

    def build(self):
        self.title = flet.Text()
        close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=self.callback_close)
        top_row = flet.Row(
            controls=[self.title, close_button],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.emotions = flet.Row(wrap=True)
        emotions_title = flet.Text("Эмоции", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        self.feelings = flet.Text(style=flet.TextThemeStyle.BODY_LARGE)
        feelings_container = flet.Container(
            content=flet.Column(controls=[emotions_title, self.feelings]),
            margin=flet.margin.symmetric(vertical=15),
        )
        body_title = flet.Text("Телесные ощущения", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        self.body = flet.Text(style=flet.TextThemeStyle.BODY_LARGE)
        body_container = flet.Container(
            content=flet.Column(controls=[body_title, self.body]),
            margin=flet.margin.symmetric(vertical=15),
        )
        desires_title = flet.Text("Желания", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        self.desires = flet.Text(style=flet.TextThemeStyle.BODY_LARGE)
        desires_container = flet.Container(
            content=flet.Column(controls=[desires_title, self.desires]),
            margin=flet.margin.symmetric(vertical=15),
        )

        return flet.Container(
            content=flet.Column(
                controls=[top_row, self.emotions, feelings_container, body_container,
                          desires_container],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    async def did_mount_async(self):
        backend_client = await get_backend_client(local_storage=self.local_storage)
        sense = await backend_client.get_sense(sense_id=self.sense_id)
        self.title.value = f"Запись от {sense.created_at.strftime('%d %b %H:%M')}"
        self.emotions.controls = [
            flet.Chip(
                label=flet.Text(emotion.value),
                show_checkmark=False,
                selected=True,
            )
            for emotion in sense.emotions
        ]
        self.feelings.value = sense.feelings
        self.body.value = sense.body
        self.desires.value = sense.desires
        await self.update_async()

    async def callback_close(self, event: flet.ControlEvent):
        await event.page.go_async(SENSE_LIST)
