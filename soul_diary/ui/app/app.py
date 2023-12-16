from typing import Any

import flet
from flet_route import Routing, path

from .local_storage import LocalStorage
from .middleware import middleware
from .models import BackendType
from .routes import AUTH, INDEX, SENSE, SENSE_ADD, SENSE_LIST
from .views.auth import AuthView
from .views.base import BaseView
from .views.sense import SenseView
from .views.sense_add import SenseAddView
from .views.sense_list import SenseListView


class SoulDiaryApp:
    def __init__(
            self,
            backend: BackendType | None = None,
            backend_data: dict[str, Any] | None = None,
    ):
        self._backend = backend
        self._backend_data = backend_data

    def get_routes(self) -> dict[str, BaseView]:
        sense_list_view = SenseListView()

        return {
            INDEX: sense_list_view,
            AUTH: AuthView(
                backend=self._backend,
                backend_data=self._backend_data,
            ),
            SENSE_LIST: sense_list_view,
            SENSE_ADD: SenseAddView(),
            SENSE: SenseView(),
        }

    async def run(self, page: flet.Page):
        page.title = "Soul Diary"
        page.app = self
        page.on_disconect = self.callback_disconnect

        routes = self.get_routes()
        Routing(
            page=page,
            async_is=True,
            app_routes=[
                path(url=url, clear=False, view=view)
                for url, view in routes.items()
            ],
            middleware=middleware,
        )

        return await page.go_async(page.route)

    async def callback_disconnect(self, event: flet.ControlEvent):
        local_storage = LocalStorage(event.page.client_storage)
        await local_storage.clear_shared_data()
