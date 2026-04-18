import click
from deps_lil_chyn.messaging import run_message_dispatcher

from deps_generic_unifier_plugin.plugin import UnifierPlugin


@click.group()
def cli() -> None:
    pass


@click.command()
def listen() -> None:
    click.secho("Connection to queue...", bg="blue", fg="white")
    run_message_dispatcher(UnifierPlugin())


if __name__ == "__main__":
    cli.add_command(listen)
    cli()
