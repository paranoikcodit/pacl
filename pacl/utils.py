from pathlib import Path
from subprocess import run, PIPE
from typing import Callable, Any, TypeVar
from concurrent.futures import ThreadPoolExecutor


T = TypeVar("T")
R = TypeVar("R")


def get_in_parent(parent: Path, paths: list[Path] | list[list[Path]]):
    if len(paths) and type(paths[0]) == list:
        path_ = []
        for paths_ in paths:
            for path in paths_:
                if path.parent == parent:
                    path_.append(path)

        return path_
    else:
        return [path for path in paths if path.parent == parent]


def get_all_parents(paths: list[Path]):
    return list(set([path.parent for path in paths]))


def get_all_parents_upto_certain(certain: Path, paths: list[Path]) -> list[list[Path]]:
    paths_ = []

    for path in paths:
        i = 0

        while path.absolute() != certain.absolute():
            if (len(paths_) - 1) < i:
                paths_.append([])

            if path not in paths_[i]:
                paths_[i].append(path)

            path = path.parent
            i += 1
    return paths_ + [[certain]]


def shell_exec(command: str, cwd: Path):
    result = run(command.split(), stdout=PIPE, stderr=PIPE, cwd=cwd)

    return (result.returncode, result.stdout, result.stderr)


def run_in_executor(
    fn: Callable[[T], R], iterables: list[Any], *, max_workers: int = 20
) -> list[R]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return executor.map(fn, iterables)
