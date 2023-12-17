import uuid
from functools import partial

import flet

from soul_diary.ui.app.backend.utils import get_backend_client
from soul_diary.ui.app.controls.utils import in_progress
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import Sense
from soul_diary.ui.app.routes import AUTH, SENSE, SENSE_ADD
from .base import BasePage, callback_error_handle


class SenseListPage(BasePage):
    def __init__(self, view: flet.View, local_storage: LocalStorage, extend: bool = False):
        self.local_storage = local_storage
        self.senses = []
        self.senses_cards: flet.Column
        self.extend = extend

        super().__init__(view=view)

    def build(self) -> flet.Container:
        self.view.vertical_alignment = flet.MainAxisAlignment.START
        self.view.scroll = flet.ScrollMode.ALWAYS

        view_switch = flet.Switch(
            label="Расширенный вид",
            value=self.extend,
            on_change=self.callback_switch_view,
        )
        top_row_left = flet.Row(
            controls=[view_switch],
            alignment=flet.MainAxisAlignment.START,
        )
        add_button = flet.IconButton(
            icon=flet.icons.ADD_CIRCLE_OUTLINE,
            on_click=self.callback_add_sense,
        )
        settings_button = flet.IconButton(
            icon=flet.icons.SETTINGS,
            visible=False,
        )
        logout_button = flet.IconButton(
            icon=flet.icons.LOGOUT,
            on_click=self.callback_logout,
        )
        top_row_right = flet.Row(
            controls=[add_button, settings_button, logout_button],
            alignment=flet.MainAxisAlignment.END,
        )
        top_row = flet.Row(
            controls=[top_row_left, top_row_right],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.senses_cards = flet.Column(alignment=flet.alignment.center)

        return flet.Container(
            content=flet.Column(
                controls=[top_row, self.senses_cards],
                width=600,
            ),
            alignment=flet.alignment.center,
        )

    async def did_mount_async(self):
        await self.render_cards()

    async def render_cards(self):
        function = self.render_extend_card if self.extend else self.render_compact_card
        backend_client = await get_backend_client(self.local_storage)
        self.senses = await backend_client.get_sense_list()
        self.senses_cards.controls = [await function(sense) for sense in self.senses]
        await self.update_async()

    async def render_compact_card(self, sense: Sense) -> flet.Card:
        feelings = flet.Container(content=flet.Text(sense.feelings), expand=True)
        created_datetime = flet.Text(sense.created_at.strftime("%d %b %H:%M"))
        emotions = flet.Row(
            controls=[
                flet.Chip(
                    label=flet.Text(emotion.value),
                    show_checkmark=False,
                    selected=True,
                )
                for emotion in sense.emotions
            ],
            wrap=True,
        )
        bottom_row = flet.Row(
            controls=[created_datetime, emotions],
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
        )

        card = flet.Container(
            content=flet.Card(
                content=flet.Container(
                    content=flet.Column(controls=[feelings, bottom_row]),
                    padding=10,
                ),
                width=600,
                height=150,
            ),
            on_click=partial(self.callback_card_click, sense_id=sense.id),
        )
        gesture_detector = flet.GestureDetector(
            mouse_cursor=flet.MouseCursor.CLICK,
            content=card,
        )

        return gesture_detector

    async def render_extend_card(self, sense: Sense) -> flet.Card:
        title = flet.Text(f"Запись от {sense.created_at.strftime('%d %b %H:%M')}")
 
        emotions_title = flet.Text("Эмоции", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        emotions = flet.Row(
            controls=[
                flet.Chip(
                    label=flet.Text(emotion.value),
                    show_checkmark=False,
                    selected=True,
                )
                for emotion in sense.emotions
            ],
            wrap=True,
        )

        feelings = flet.Text(sense.feelings, style=flet.TextThemeStyle.BODY_LARGE)
        feelings_container = flet.Container(
            content=flet.Column(controls=[emotions_title, feelings]),
            margin=flet.margin.symmetric(vertical=5),
        )

        body_title = flet.Text("Телесные ощущения", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        body = flet.Text(sense.body, style=flet.TextThemeStyle.BODY_LARGE)
        body_container = flet.Container(
            content=flet.Column(controls=[body_title, body]),
            margin=flet.margin.symmetric(vertical=5),
        )

        desires_title = flet.Text("Желания", style=flet.TextThemeStyle.HEADLINE_MEDIUM)
        desires = flet.Text(sense.desires, style=flet.TextThemeStyle.BODY_LARGE)
        desires_container = flet.Container(
            content=flet.Column(controls=[desires_title, desires]),
            margin=flet.margin.symmetric(vertical=5),
        )
        card = flet.Card(
            content=flet.Container(
                content=flet.Column(controls=[title, emotions, feelings_container, body_container,
                                              desires_container]),
                padding=10,
            ),
            width=600,
        )
        card = flet.Container(
            content=card,
            on_click=partial(self.callback_card_click, sense_id=sense.id),
        )
        gesture_detector = flet.GestureDetector(
            mouse_cursor=flet.MouseCursor.CLICK,
            content=card,
        )

        return gesture_detector

    @callback_error_handle
    async def callback_switch_view(self, event: flet.ControlEvent):
        self.extend = event.control.value
        await self.local_storage.add_client_data(key="extend_list_view", value=self.extend)
        await self.render_cards()

    @callback_error_handle
    async def callback_card_click(self, event: flet.ControlEvent, sense_id: uuid.UUID):
        await event.page.go_async(SENSE.replace(":sense_id", str(sense_id)))

    @callback_error_handle
    async def callback_add_sense(self, event: flet.ControlEvent):
        await event.page.go_async(SENSE_ADD)

    @callback_error_handle
    async def callback_logout(self, event: flet.ControlEvent):
        backend_client = await get_backend_client(local_storage=self.local_storage)
        async with in_progress(page=event.page):
            await backend_client.logout()
        await self.local_storage.clear_shared_data()
        await event.page.go_async(AUTH)
