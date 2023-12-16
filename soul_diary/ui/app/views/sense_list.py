import flet

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage
from soul_diary.ui.app.pages.sense_list import SenseListPage
from .base import BaseView


class SenseListView(BaseView):
    async def entrypoint(self, page: flet.Page) -> BasePage:
        local_storage = LocalStorage(client_storage=page.client_storage)
        return SenseListPage(view=self.view, local_storage=local_storage)
