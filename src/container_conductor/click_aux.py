import sys
import os
from functools import update_wrapper

import click

from container_conductor.compose import run_podman_compose
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
def cli(ctx):
    run_podman_compose(ctx)


def build_root_cli(parent_command, name, config):
    @parent_command.group(name=name, help=config["help"], **help_alias)
    @click.pass_context
    def main_command(ctx):
        pass

    for command_config in config.get("commands", []):
        command = create_command(command_config)
        main_command.add_command(command)
        if command_config.get("commands"):
            build_root_cli(main_command, command_config["name"], command_config)


def build_app_cli(name, config, parent_command=None):
    for arg in config.get("arguments") or []:
        update_wrapper(
            parent_command or cli,
            lambda: (parent_command or click).argument(
                *arg.get("args", []), **arg.get("kwargs", {})
            ),
        )
    for opt in config.get("options", []):
        update_wrapper(
            parent_command or cli,
            lambda: (parent_command or click).option(
                *opt.get("args", []), **opt.get("kwargs", {})
            ),
        )
    for c in config.get("commands", []):

        @ (parent_command or cli).group(name=c["name"], help=c["help"], **help_alias)
        @click.pass_context
        def command(ctx):
            pass

        build_app_cli(c["name"], c, command)


def main():
    root_command = sys.argv[0]
    if root_command == "coco" or root_command.endswith("/coco"):
        # The program is called via "coco ..."
        apps = load_all_apps("examples/typst.coco")
        for app in apps:
            build_root_cli(cli, app["name"], app["cli"])
    else:
        # The program is called via a *link to coco*
        app = get_app_by_name(os.path.basename(root_command), "examples/typst.coco")
        build_app_cli(app["name"], app["cli"], cli)

    cli()
