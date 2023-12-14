import asyncio

import typer

from . import web
from .service import get_service


def run():
    ui_service = get_service()

    asyncio.run(ui_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.command(name="run")(run)
    cli.add_typer(web.get_cli(), name="web")

    return cli
