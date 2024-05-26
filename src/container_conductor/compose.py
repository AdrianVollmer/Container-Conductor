import sys


def run_podman_compose(ctx):
    cli = sys.argv

    # Check if help was passed
    if "-h" in cli or "--help" in cli:
        return

    # remove leading arguments
    if cli[0] == "coco" or cli[0].endswith("/coco"):
        cli.pop(0)

    # remove app name
    app_name = cli.pop(0)

    spawn_podman_process(cli, app_name)


def spawn_podman_process(cli, app_name):
    import subprocess
    import os
    import shlex

    import yaml
    from xdg.BaseDirectory import save_cache_path
    from container_conductor.config import APP_CACHE_BY_NAME

    cmdline = " ".join(map(shlex.quote, cli))
    env = os.environ
    extra_vars = dict(
        CLI_ARGS=cmdline,
        CWD=os.getcwd(),
    )
    env.update(extra_vars)
    pyexec = sys.executable

    app = APP_CACHE_BY_NAME[app_name]

    compose_file_path = os.path.join(save_cache_path("coco"), app_name + ".yml")

    with open(compose_file_path, "w") as fp:
        yaml.dump(app["compose-file"], fp)
        fp.close()

        subprocess.run(
            [
                pyexec,
                "-m",
                "podman_compose",
                "-f",
                fp.name,
                "run",
                f"coco_{app_name}",
            ],
            env=env,
        )
