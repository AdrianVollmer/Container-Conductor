from typing import Callable
from container_conductor.config import get_coco_apps
import click


def from_config(func: Callable) -> Callable:
    """This meta-decorator reads the coco config and applies click decorators to
    func"""
    result = func

    coco_apps = get_coco_apps()

    for coco_app in coco_apps:
        decorator = getattr(click, coco_app.name)
        result = decorator(*coco_app["args"], **coco_app["kwargs"])(result)

    return result
