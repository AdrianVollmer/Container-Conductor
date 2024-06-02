import os
import shlex
import subprocess
import sys
import logging
import asyncio

import yaml
from xdg.BaseDirectory import save_cache_path
from podman_compose import podman_compose  # type: ignore

from container_conductor.config import get_app_by_name

logger = logging.getLogger(__name__)


def spawn_podman_process(cli, app_name):
    cmdline = " ".join(map(shlex.quote, cli))
    env = os.environ
    extra_vars = dict(
        CLI_ARGS=cmdline,
        CWD=os.getcwd(),
    )
    env.update(extra_vars)
    app = get_app_by_name(app_name)

    if "compose-file" in app:
        run_podman_compose(app)
    elif "podman-cmd" in app:
        run_podman_run(app)


def run_podman_run(app):
    cmd = app["podman-cmd"].replace("\\\n", "")
    cmd = cmd.format(**os.environ)
    cmd = shlex.split(cmd)
    subprocess.run(["podman"] + cmd)


def run_podman_compose(app):

    pod_path = os.path.join(save_cache_path("coco"), app["name"])
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
        f"{app['name']}",
    ]

    asyncio.run(podman_compose.run())
