import flet
from flet_route import Params

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage
from soul_diary.ui.app.pages.sense_add.emotions import EmotionsPage
from .base import BaseView


class SenseAddView(BaseView):
    async def entrypoint(self, page: flet.Page, params: Params) -> BasePage:
        local_storage = LocalStorage(page.client_storage)
        return EmotionsPage(view=self.view, local_storage=local_storage)
