import flet
from flet_route import Params

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage
from soul_diary.ui.app.pages.sense_list import SenseListPage
from .base import BaseView


class SenseListView(BaseView):
    async def entrypoint(self, page: flet.Page, params: Params) -> BasePage:
        local_storage = LocalStorage(client_storage=page.client_storage)
        extend = await local_storage.get_client_data(key="extend_list_view") or False
        return SenseListPage(view=self.view, local_storage=local_storage, extend=extend)
