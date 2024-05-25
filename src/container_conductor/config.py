from xdg.BaseDirectory import save_data_path
import os
import glob
import yaml
from pathlib import Path


class CocoApp(object):
    def __init__(self, file: str | Path):
        file = Path(file)
        if not file.name.endswith(".coco"):
            raise RuntimeError(f"Cannot load this file: {file}")
        self.file = file
        self.data = yaml.safe_load(self.file.name)

        self.name = self.data.get("name", os.path.basename(self.file)[:-4])


def get_coco_apps() -> list[CocoApp]:
    data_dir = save_data_path("coco")
    files = glob.glob(os.path.join(data_dir, "*.coco"))
    result = [CocoApp(f) for f in files]
    return result
