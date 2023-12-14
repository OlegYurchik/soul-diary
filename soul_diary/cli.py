import asyncio

import typer

from . import backend, ui
from .service import get_service


def run():
    soul_diary_service = get_service()

    asyncio.run(soul_diary_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.add_typer(backend.get_cli(), name="backend")
    cli.add_typer(ui.get_cli(), name="ui")
    cli.command(name="run")(run)

    return cli
