import asyncio

import typer

from . import api, database
from .service import get_service


def run():
    backend_service = get_service()

    asyncio.run(backend_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.add_typer(api.get_cli(), name="api")
    cli.add_typer(database.get_cli(), name="database")
    cli.command(name="run")(run)

    return cli
