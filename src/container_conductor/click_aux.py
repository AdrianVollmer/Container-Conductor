import sys
import os
from typing import Callable

import click

from container_conductor.config import (
    load_all_apps,
    get_app_by_name,
    CocoCli,
    CocoCliOption,
    CocoCliArgument,
    CocoCliCommand,
)

help_alias = dict(context_settings=dict(help_option_names=["-h", "--help"]))


def create_command(command_config: CocoCliCommand) -> click.Command:
    @click.command(name=command_config.name, help=command_config.help)
    @add_arguments(command_config.arguments)
    @add_options(command_config.options)
    def command(**kwargs):
        pass

    return command


def add_arguments(arguments: list[CocoCliArgument]) -> Callable:
    def decorator(f):
        for arg in arguments:
            f = click.argument(*arg.click_args, **arg.click_kwargs)(f)
        return f

    return decorator


def add_options(options: list[CocoCliOption]) -> Callable:
    def decorator(f):
        for opt in options:
            f = click.option(*opt.click_args, **opt.click_kwargs)(f)
        return f

    return decorator


@click.group(**help_alias)  # type: ignore
@click.pass_context
def cli(ctx, *args, **kwargs) -> None:
    cli_args = sys.argv

    # Check if help was passed
    if "-h" in cli_args or "--help" in cli_args:
        return

    # remove leading arguments
    if cli_args[0] == "coco" or cli_args[0].endswith("/coco"):
        cli_args.pop(0)

    # remove app name
    app_name = os.path.basename(cli_args.pop(0))

    # This is not imported earlier because we want to save startup time when
    # only help is called
    from container_conductor.podman import spawn_podman_process

    spawn_podman_process(cli_args, app_name)


def build_root_cli(
    parent_command: click.Command, name: str, config: CocoCli | CocoCliCommand
) -> None:
    """This constructs the click interface if `coco` is called"""

    @parent_command.group(name=name, help=config.help, **help_alias)  # type: ignore
    @click.pass_context
    def main_command(ctx):
        pass

    for command in config.commands:
        com = create_command(command)
        main_command.add_command(com)
        if command.commands:
            build_root_cli(main_command, command.name, command)


def build_app_cli(
    parent_command: click.Command, name: str, config: CocoCli | CocoCliCommand
) -> None:
    """This constructs the click interface if *a link to* `coco` is called"""

    global cli
    if parent_command == cli:
        cli = add_options(config.options)(cli)

    for command in config.commands:
        com = create_command(command)
        parent_command.add_command(com)
        build_app_cli(com, command.name, command)


def main():
    root_command = sys.argv[0]

    if root_command == "coco" or root_command.endswith("/coco"):
        # The program is called via "coco ..."
        apps = load_all_apps("examples/typst.coco")
        for app in apps:
            build_root_cli(cli, app.name, app.cli)
    else:
        # The program is called via a *link to coco*
        root_command = os.path.basename(root_command)
        app = get_app_by_name(root_command, "examples/typst.coco")
        build_app_cli(cli, app.name, app.cli)

    cli()
