from typing import Any

import flet
from flet_route import Routing, path

from .local_storage import LocalStorage
from .middleware import middleware
from .models import BackendType
from .routes import AUTH, INDEX, SENSE_ADD, SENSE_LIST
from .views.auth import AuthView
from .views.base import BaseView
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

    def get_routes(self, page: flet.Page) -> dict[str, BaseView]:
        local_storage = LocalStorage(client_storage=page.client_storage)
        sense_list_view = SenseListView(local_storage=local_storage)

        return {
            INDEX: sense_list_view,
            AUTH: AuthView(
                local_storage=local_storage,
                backend=self._backend,
                backend_data=self._backend_data,
            ),
            SENSE_LIST: sense_list_view,
            SENSE_ADD: SenseAddView(local_storage=local_storage),
        }

    async def run(self, page: flet.Page):
        page.title = "Soul Diary"
        page.app = self

        routes = self.get_routes(page)
        Routing(
            page=page,
            async_is=True,
            app_routes=[
                path(url=url, clear=False, view=view.entrypoint)
                for url, view in routes.items()
            ],
            middleware=middleware,
        )

        return await page.go_async(page.route)
