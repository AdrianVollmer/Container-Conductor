import sys
import os


def run_podman_compose(ctx):
    cli = sys.argv

    # Check if help was passed
    if "-h" in cli or "--help" in cli:
        return

    # remove leading arguments
    if cli[0] == "coco" or cli[0].endswith("/coco"):
        cli.pop(0)

    # remove app name
    app_name = os.path.basename(cli.pop(0))

    spawn_podman_process(cli, app_name)


def spawn_podman_process(cli, app_name):
    import shlex
    import logging
    import asyncio

    import yaml
    from xdg.BaseDirectory import save_cache_path
    from podman_compose import podman_compose

    from container_conductor.config import get_app_by_name

    cmdline = " ".join(map(shlex.quote, cli))
    env = os.environ
    extra_vars = dict(
        CLI_ARGS=cmdline,
        CWD=os.getcwd(),
    )
    env.update(extra_vars)
    #  pyexec = sys.executable

    app = get_app_by_name(app_name)

    pod_path = os.path.join(save_cache_path("coco"), app_name)
    os.makedirs(pod_path, exist_ok=True)
    compose_file_path = os.path.join(pod_path, "compose.yml")

    with open(compose_file_path, "w") as fp:
        yaml.dump(app["compose-file"], fp)
        fp.close()

        podman_logger = logging.getLogger("podman_compose")
        #  podman_logger.setLevel("INFO")
        podman_logger.handlers.clear()

        sys.argv = [
            "podman_compose",
            "--pod-args=--replace",
            "-f",
            fp.name,
            "run",
            "--rm",
            f"{app_name}",
        ]
        asyncio.run(podman_compose.run())
