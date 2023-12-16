from typing import Callable

import flet


class BasePage(flet.UserControl):
    def __init__(self, view: flet.View):
        self.view = view

        super().__init__()

    async def apply(self):
        self.view.controls = [self]
        await self.view.update_async()


def callback_error_handle(function: Callable) -> Callable:
    async def wrapper(self, event: flet.ControlEvent, *args, **kwargs):
        async def close_dialog(event: flet.ControlEvent):
            dialog.open = False
            await dialog.update_async()

        try:
            await function(self, event, *args, **kwargs)
        except:
            text = flet.Text("Ошибка")
            close_button = flet.IconButton(icon=flet.icons.CLOSE, on_click=close_dialog)
            dialog = flet.AlertDialog(
                modal=True,
                open=True,
                title=flet.Row(
                    controls=[text, close_button],
                    alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                ),
                content=flet.Text("Произошла ошибка"),
            )
            event.page.dialog = dialog
            await event.page.update_async()

    return wrapper
