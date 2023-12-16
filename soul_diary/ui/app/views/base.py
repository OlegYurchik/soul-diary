import flet
from flet_route import Basket, Params

from soul_diary.ui.app.pages.base import BasePage


class BaseView:
    async def __call__(self, page: flet.Page, params: Params, basket: Basket) -> flet.View:
        self.view = flet.View(vertical_alignment=flet.MainAxisAlignment.CENTER)

        page = await self.entrypoint(page=page, params=params)
        self.view.controls = [page]

        return self.view

    async def entrypoint(self, page: flet.Page, params: Params) -> BasePage:
        raise NotImplementedError
