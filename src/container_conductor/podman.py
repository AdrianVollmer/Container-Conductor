import asyncio
import logging
import os
import shlex
import subprocess
import sys

import yaml
from podman_compose import podman_compose  # type: ignore
from xdg.BaseDirectory import save_cache_path

from container_conductor.config import CocoApp, PodmanRun, get_app_by_name

logger = logging.getLogger(__name__)


def spawn_podman_process(cli: list[str], app_name: str) -> None:
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
    elif app.podman_run:
        run_podman_run(app)


def run_podman_run(app: CocoApp) -> None:
    assert isinstance(app.podman_run, PodmanRun)

    cmd = ["podman", "run"]

    if app.podman_run.rm:
        cmd += ["--rm"]

    for v in app.podman_run.volumes:
        cmd += ["--volume", v]

    cmd += [app.podman_run.image]

    for i, _ in enumerate(cmd):
        cmd[i] = cmd[i].format(**os.environ)

    expanded_args = app.podman_run.args.format(**os.environ)
    cmd.extend(shlex.split(expanded_args))

    logger.debug(f"Running: {cmd}")
    subprocess.run(cmd, check=False)


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
