import asyncio

import typer

from . import ui


def run():
    ui_service = ui.get_service()    

    asyncio.run(ui_service.run())


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.add_typer(ui.get_cli(), name="ui")
    cli.command(name="run")(run)

    return cli
