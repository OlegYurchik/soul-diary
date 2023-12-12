import typer

from . import web


def get_cli() -> typer.Typer:
    cli = typer.Typer()

    cli.add_typer(web.get_cli(), name="web")

    return cli
