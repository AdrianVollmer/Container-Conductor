from xdg.BaseDirectory import save_data_path
import os
import glob
import yaml
import logging
from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CocoCliOption:
    click_args: Optional[list[str]] = field(default_factory=lambda: [])
    click_kwargs: Optional[dict[str, Any]] = field(default_factory=lambda: {})


@dataclass
class CocoCliArgument(CocoCliOption):
    pass


@dataclass
class CocoCliCommand:
    name: str
    help: str
    arguments: list[CocoCliArgument] = field(default_factory=lambda: [])
    options: list[CocoCliOption] = field(default_factory=lambda: [])
    commands: list["CocoCliCommand"] = field(default_factory=lambda: [])

    def __post_init__(self):
        if self.arguments:
            self.arguments = [CocoCliArgument(**a) for a in self.arguments]
        if self.options:
            self.options = [CocoCliOption(**a) for a in self.options]
        if self.commands:
            self.commands = [CocoCliCommand(**c) for c in self.commands]


@dataclass
class CocoCli:
    help: str
    commands: list[CocoCliCommand] = field(default_factory=lambda: [])
    options: list[CocoCliOption] = field(default_factory=lambda: [])

    def __post_init__(self):
        if self.commands:
            self.commands = [CocoCliCommand(**c) for c in self.commands]
        if self.options:
            self.options = [CocoCliOption(**a) for a in self.options]


@dataclass
class CocoApp:
    name: str
    cli: CocoCli
    compose_file: Optional[str] = None
    podman_cmd: Optional[str] = None

    def __post_init__(self):
        self.cli = CocoCli(**self.cli)


APP_CACHE_BY_NAME: dict[str, CocoApp] = {}
APP_CACHE_BY_PATH: dict[str, CocoApp] = {}

key_map = {
    "podman-cmd": "podman_cmd",
    "compose-file": "compose_file",
}


def map_key_names(data: dict) -> None:
    for k in key_map:
        if k in data:
            data[key_map[k]] = data[k]
            del data[k]


def load_app(path: Path | str) -> CocoApp:
    if path in APP_CACHE_BY_PATH:
        return APP_CACHE_BY_PATH[str(path)]

    data = yaml.safe_load(open(path))
    map_key_names(data)
    result = CocoApp(**data)

    if result.name in APP_CACHE_BY_NAME:
        logger.warning(f"Duplicate app name in file: {path}")

    APP_CACHE_BY_PATH[str(path)] = result
    APP_CACHE_BY_NAME[result.name] = result
    return result


def load_all_apps(*extra_file_paths: list[Path | str]) -> list[CocoApp]:
    data_dir = save_data_path("coco")
    files: list[str] = glob.glob(os.path.join(data_dir, "*.coco"))
    files.extend(map(str, extra_file_paths))
    result = []

    for f in files:
        try:
            result += [load_app(f)]
        except Exception as e:
            logger.error(f"Error while parsing file '{f}': {e}")

    return result


def get_app_by_name(name: str, *extra_file_paths: list[Path | str]) -> CocoApp:
    if name in APP_CACHE_BY_NAME:
        return APP_CACHE_BY_NAME[name]

    load_all_apps(*extra_file_paths)
    return APP_CACHE_BY_NAME[name]
