import click

from container_conductor.compose import run_podman_compose
from container_conductor.config import load_all_apps

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


def build_cli(parent_command, name, config):
    @parent_command.group(name=name, help=config["help"], **help_alias)
    @click.pass_context
    def main_command(ctx):
        pass

    for command_config in config.get("commands", []):
        command = create_command(command_config)
        main_command.add_command(command)
        if command_config.get("commands"):
            build_cli(main_command, command_config["name"], command_config)


def main():
    apps = load_all_apps("examples/typst.coco")
    for app in apps:
        build_cli(cli, app["name"], app["cli"])
    cli()
