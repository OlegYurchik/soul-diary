import flet

from soul_diary.ui.app.backend.utils import get_backend_client
from soul_diary.ui.app.controls.utils import in_progress
from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.models import Sense
from soul_diary.ui.app.routes import AUTH, SENSE_ADD
from .base import BasePage, callback_error_handle


class SenseListPage(BasePage):
    def __init__(self, view: flet.View, local_storage: LocalStorage):
        self.local_storage = local_storage
        self.senses_cards: flet.Column

        super().__init__(view=view)

    def build(self) -> flet.Container:
        self.view.vertical_alignment = flet.MainAxisAlignment.START

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

        self.senses_cards = flet.Column(alignment=flet.alignment.center)

        return flet.Container(
            content=flet.Column(
                controls=[top_container, self.senses_cards],
                width=400,
            ),
            alignment=flet.alignment.center,
        )

    async def did_mount_async(self):
        await self.render_cards()

    async def render_cards(self):
        backend_client = await get_backend_client(self.local_storage)
        senses = await backend_client.get_sense_list()
        self.senses_cards.controls = [
            await self.render_card(sense)
            for sense in senses
        ]
        await self.update_async()

    async def render_card(self, sense: Sense) -> flet.Card:
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
