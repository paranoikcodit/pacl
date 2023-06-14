from pathlib import Path
from shutil import rmtree
from ...utils import shell_exec


ACTIVATE_POSTFIX = " (Activated)"


def safe_exec(command: str, cwd: Path):
    (returncode, stdout, stderr) = shell_exec(command, cwd)

    if returncode == 0:
        return stdout.decode("utf-8").strip()
    else:
        return None


def is_env(path: Path):
    return get_active_env(path) is not None


def get_active_env(path: Path):
    env = safe_exec("poetry env info -p", cwd=path)

    if env:
        return Path(env)


def get_env_list(cwd: Path):
    data = safe_exec("poetry env list --full-path", cwd=cwd)

    if data:
        lines = data.strip().split("\n")
        lines = [
            line[0 : -len(ACTIVATE_POSTFIX)]
            if line.endswith(ACTIVATE_POSTFIX)
            else line
            for line in lines
        ]

        return [Path(line) for line in lines]


def get_envs_contains_work_dir(cwd: Path) -> list[Path]:
    envs = get_env_list(cwd)

    if envs:
        return list(filter(lambda env: env.parent.cwd() == cwd.cwd(), envs))

    return []


def clean(path: Path):
    envs = get_envs_contains_work_dir(path)

    for env in envs:
        rmtree(env, True)


def name():
    return "poetry"
