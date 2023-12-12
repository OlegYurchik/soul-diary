import asyncio
import typer

from .service import get_service
from .settings import WebSettings, get_settings


def run(ctx: typer.Context):
    settings: WebSettings = ctx.obj["settings"]

    loop = asyncio.get_event_loop()
    frontend_service = get_service(settings=settings)

    loop.run_until_complete(frontend_service.run())


def settings_callback(ctx: typer.Context):
    ctx.obj = ctx.obj or {}
    ctx.obj["settings"] = get_settings()


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.callback()(settings_callback)
    cli.command(name="run")(run)

    return cli
