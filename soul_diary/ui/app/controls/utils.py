from contextlib import asynccontextmanager

import flet


@asynccontextmanager
async def in_progress(page: flet.Page, tooltip: str | None = None):
    page.splash = flet.Column(
        controls=[flet.Container(
            content=flet.ProgressRing(tooltip=tooltip),
            alignment=flet.alignment.center,
        )],
        alignment=flet.MainAxisAlignment.CENTER,
    )
    await page.update_async()

    yield

    page.splash = None
    await page.update_async()
