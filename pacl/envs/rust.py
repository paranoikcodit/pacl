from pathlib import Path
from shutil import rmtree
from ..utils import shell_exec


def is_env(path: Path):
    for file in path.iterdir():
        if "cargo.toml" in file.name.lower():
            return True


def clean(path: Path, delete_target: bool = False):
    returncode = shell_exec("cargo clean", cwd=path)[0]

    if returncode != 0 and delete_target:
        rmtree(path / "target", True)


def name():
    return "rust"
