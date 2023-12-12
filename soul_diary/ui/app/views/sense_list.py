import asyncio
from typing import Awaitable, Callable, Sequence

import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.middlewares.base import BaseMiddleware
from soul_diary.ui.app.models import Sense
from soul_diary.ui.app.routes import AUTH, SENSE_ADD, SENSE_LIST
from .base import BaseView, view


class SenseListView(BaseView):
    def __init__(
            self,
            local_storage: LocalStorage,
            middlewares: Sequence[BaseMiddleware | Callable[[flet.Page], Awaitable]] = (),
    ):
        self.cards: flet.Column

        self.local_storage = local_storage

        super().__init__(middlewares=middlewares)

    async def setup(self):
        self.cards = flet.Column(alignment=flet.alignment.center, width=400)

        add_button = flet.IconButton(
            icon=flet.icons.ADD_CIRCLE_OUTLINE,
            on_click=self.callback_add_sense,
        )
        settings_button = flet.IconButton(
            icon=flet.icons.SETTINGS,
        )
        logout_button = flet.IconButton(
            icon=flet.icons.LOGOUT,
            on_click=self.callback_logout,
        )
        top_container = flet.Container(
            content=flet.Row(
                controls=[add_button, settings_button, logout_button],
                alignment=flet.MainAxisAlignment.END,
            ),
        )

        self.container.content = flet.Column(
            controls=[top_container, self.cards],
            width=400,
        )
        self.container.alignment = flet.alignment.center

        self.view.route = SENSE_LIST
        self.view.vertical_alignment = flet.MainAxisAlignment.CENTER
        self.view.scroll = flet.ScrollMode.ALWAYS

    async def clear(self):
        self.cards.controls = []

    @view(initial=True)
    async def sense_list_view(self, page: flet.Page):
        self.cards.controls = [
            flet.Container(
                content=flet.ProgressRing(),
                alignment=flet.alignment.center,
            ),
        ]

        loop = asyncio.get_running_loop()
        loop.create_task(self.render_sense_list(page=page))

    async def render_sense_list(self, page: flet.Page):
        senses = await page.app.backend_client.get_sense_list()
        self.cards.controls = [await self.render_card_from_sense(sense) for sense in senses]
        await page.update_async()

    async def render_card_from_sense(self, sense: Sense) -> flet.Card:
        feelings = flet.Container(content=flet.Text(sense.feelings), expand=True)
        created_datetime = flet.Text(sense.created_at.strftime("%d %b %H:%M"))

        return flet.Card(
            content=flet.Container(
                content=flet.Column(controls=[feelings, created_datetime]),
                padding=10,
            ),
            width=400,
            height=100,
        )

    async def callback_add_sense(self, event: flet.ControlEvent):
        await event.page.go_async(SENSE_ADD)

    async def callback_logout(self, event: flet.ControlEvent):
        await self.local_storage.remove_auth_data()
        event.page.app.backend_client = None
        await event.page.go_async(AUTH)
