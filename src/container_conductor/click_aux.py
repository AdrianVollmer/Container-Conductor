import sys
import os
from functools import update_wrapper

import click

from container_conductor.config import load_all_apps, get_app_by_name

help_alias = dict(context_settings=dict(help_option_names=["-h", "--help"]))


def create_command(command_config):
    @click.command(name=command_config["name"], help=command_config["help"])
    @add_arguments(command_config.get("arguments", []))
    @add_options(command_config.get("options", []))
    def command(**kwargs):
        #  print(kwargs)
        pass

    return command


def add_arguments(arguments):
    def decorator(f):
        for arg in arguments:
            f = click.argument(*arg.get("args", []), **arg.get("kwargs", {}))(f)
        return f

    return decorator


def add_options(options):
    def decorator(f):
        for opt in options:
            f = click.option(*opt.get("args", []), **opt.get("kwargs", {}))(f)
        return f

    return decorator


@click.group(**help_alias)  # type: ignore
@click.pass_context
def cli(ctx, *args, **kwargs):
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
    from container_conductor.compose import spawn_podman_process

    spawn_podman_process(cli_args, app_name)


def build_root_cli(parent_command, name, config):
    """This constructs the click interface if `coco` is called"""

    @parent_command.group(name=name, help=config["help"], **help_alias)
    @click.pass_context
    def main_command(ctx):
        pass

    for command_config in config.get("commands", []):
        command = create_command(command_config)
        main_command.add_command(command)
        if command_config.get("commands"):
            build_root_cli(main_command, command_config["name"], command_config)


def build_app_cli(parent_command, name, config, root=True):
    """This constructs the click interface if *a link to* `coco` is called"""

    if root:
        global cli
        cli = add_options(config.get("options", []))(cli)

    for command_config in config.get("commands", []):
        command = create_command(command_config)
        parent_command.add_command(command)
        build_app_cli(command, command_config["name"], command_config, root=False)


def main():
    root_command = sys.argv[0]

    if root_command == "coco" or root_command.endswith("/coco"):
        # The program is called via "coco ..."
        apps = load_all_apps("examples/typst.coco")
        for app in apps:
            build_root_cli(cli, app["name"], app["cli"])
    else:
        # The program is called via a *link to coco*
        root_command = os.path.basename(root_command)
        app = get_app_by_name(root_command, "examples/typst.coco")
        build_app_cli(cli, app["name"], app["cli"])

    cli()
