import flet


class BasePage(flet.UserControl):
    async def apply(self, page: flet.Page):
        await page.clean_async()
        await page.add_async(self)
