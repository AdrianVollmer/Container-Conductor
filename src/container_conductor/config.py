from xdg.BaseDirectory import save_data_path
import os
import glob
import yaml


APP_CACHE_BY_NAME = {}
APP_CACHE_BY_PATH: dict[str, dict] = {}


def load_app(path):
    if path in APP_CACHE_BY_PATH:
        return APP_CACHE_BY_PATH[path]

    result = yaml.safe_load(open(path))
    APP_CACHE_BY_PATH[path] = result
    APP_CACHE_BY_NAME[result["name"]] = result
    return result


def load_all_apps(*extra_file_paths):
    data_dir = save_data_path("coco")
    files = glob.glob(os.path.join(data_dir, "*.coco"))
    files.extend(extra_file_paths)
    result = [load_app(f) for f in files]
    return result
