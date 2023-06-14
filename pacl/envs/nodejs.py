from pathlib import Path
from shutil import rmtree


def is_env(path: Path):
    for file in path.iterdir():
        if "package.json" in file.name.lower():
            return True


def clean(path: Path):
    rmtree((path / ".next"), True)
    rmtree((path / "node_modules"), True)


def name():
    return "nodejs"
