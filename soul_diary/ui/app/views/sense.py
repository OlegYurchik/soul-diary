import uuid

import flet
from flet_route import Params

from soul_diary.ui.app.local_storage import LocalStorage
from soul_diary.ui.app.pages.base import BasePage
from soul_diary.ui.app.pages.sense import SensePage
from .base import BaseView


class SenseView(BaseView):
    async def entrypoint(self, page: flet.Page, params: Params) -> BasePage:
        sense_id = uuid.UUID(params.sense_id)
        local_storage = LocalStorage(page.client_storage)
        return SensePage(view=self.view, local_storage=local_storage, sense_id=sense_id)
