from pathlib import Path
from .envs import rust, python, nodejs

from typing import TypedDict


class Env:
    def is_env(path: Path):
        ...

    def clean(path: Path):
        ...

    def name() -> str:
        ...


class PythonEnvs(TypedDict):
    venv: Env
    poetry: Env


class Envs(TypedDict):
    rust: Env
    nodejs: Env
    python: PythonEnvs


envs: Envs = {"rust": rust, "nodejs": nodejs, "python": python.envs}


def detect_env(path: Path) -> Env:
    for env in envs:
        if env == "python":
            for python_env in envs[env]:
                if envs[env][python_env].is_env(path):
                    return envs[env][python_env], path
        else:
            if envs[env].is_env(path):
                return envs[env], path

    return None, path
