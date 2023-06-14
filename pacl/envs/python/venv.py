from pathlib import Path
from shutil import rmtree


def find_venv_folder(path: Path) -> Path:
    for path_ in path.iterdir():
        if path_.is_dir() and (path_ / "pyvenv.cfg").exists():
            return path_


def is_env(path: Path):
    return find_venv_folder(path) is not None


def clean(path: Path):
    if path := find_venv_folder(path):
        rmtree(path, True)


def name():
    return "venv"
