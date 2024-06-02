import os
import shlex
import subprocess
import sys
import logging
import asyncio

import yaml
from xdg.BaseDirectory import save_cache_path
from podman_compose import podman_compose  # type: ignore

from container_conductor.config import get_app_by_name, CocoApp

logger = logging.getLogger(__name__)


def spawn_podman_process(cli: str, app_name: str) -> None:
    cmdline = " ".join(map(shlex.quote, cli))
    env = os.environ
    extra_vars = dict(
        CLI_ARGS=cmdline,
        CWD=os.getcwd(),
    )
    env.update(extra_vars)
    app = get_app_by_name(app_name)

    if app.compose_file:
        run_podman_compose(app)
    elif app.podman_cmd:
        run_podman_run(app)


def run_podman_run(app: CocoApp) -> None:
    assert isinstance(app.podman_cmd, str)
    cmd = app.podman_cmd.replace("\\\n", "")
    cmd = cmd.format(**os.environ)
    arg_list = shlex.split(cmd)
    subprocess.run(["podman"] + arg_list)


def run_podman_compose(app: CocoApp) -> None:
    pod_path = os.path.join(save_cache_path("coco"), app.name)
    os.makedirs(pod_path, exist_ok=True)
    compose_file_path = os.path.join(pod_path, "compose.yml")

    with open(compose_file_path, "w") as fp:
        yaml.dump(app.compose_file, fp)
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
        f"{app.name}",
    ]

    asyncio.run(podman_compose.run())
