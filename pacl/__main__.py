from concurrent.futures import ThreadPoolExecutor
from typing import Any
from alive_progress import alive_it
from pytermgui.ansi_interface import MouseEvent
import typer

from time import sleep
from pytermgui import (
    Widget,
    Container,
    cursor_next_line,
    cursor_right,
    get_terminal,
    Label,
    hide_cursor,
    palette,
    print_to,
    report_cursor,
    save_cursor,
    boxes,
    clear,
    restore_cursor,
    set_echo,
    show_cursor,
    unset_echo,
)
from pathlib import Path
from threading import Thread
from tarfile import TarFile

from . import detect_env
from .utils import (
    get_all_parents,
    get_all_parents_upto_certain,
    get_in_parent,
    run_in_executor,
)


app = typer.Typer()

palette.regenerate(primary="skyblue")


def render_widget(widget: Widget, need_clear_widget: bool = False):
    try:
        unset_echo()
        hide_cursor()

        cursor = report_cursor()

        if cursor is not None:
            widget.pos = cursor

        def _print_widget() -> None:
            save_cursor()

            for line in widget.get_lines():
                print(line)

            for pos, line in widget.positioned_line_buffer:
                print_to(pos, line)
            widget.positioned_line_buffer = []

            restore_cursor()

        while widget.is_working:
            _print_widget()

            sleep(0.1)

        if need_clear_widget:
            clear_widget(widget, get_terminal())
        else:
            cursor_right(num=widget.width)
            cursor_next_line(num=widget.height)

    except KeyboardInterrupt:
        clear_widget(widget, get_terminal())
    finally:
        set_echo()
        show_cursor()

        return widget.result


def clear_widget(widget: Widget, terminal) -> None:
    save_cursor()

    for _ in range(widget.height):
        clear("line")
        terminal.write("\n")

    restore_cursor()
    terminal.flush()


class EnvsLoadWidget(Container):
    is_working = True

    def __init__(self, paths: list[Path]) -> None:
        # super().__init__(Label("NodeJS: 0 Rust: 0 Poetry: 0 Venv: 0"))
        super().__init__(width=80, box=boxes.ROUNDED)

        self.paths = [path for path in paths if path.is_dir()]
        self.result = []

        self.thread = Thread(target=self.render, daemon=True)
        self.thread.start()

    def render(self):
        counters = {
            "nodejs": 0,
            "rust": 0,
            "poetry": 0,
            "venv": 0,
            "unknown": 0,
        }

        self.set_widgets(
            [
                Label("Detected environments:"),
                "",
                Label(
                    " ".join(
                        [
                            f"{counter}: [bold primary]{str(counters[counter])}[/]"
                            for counter in counters
                        ]
                    ),
                ),
            ]
        )

        with ThreadPoolExecutor(max_workers=20) as executor:
            for env, path in executor.map(detect_env, self.paths):
                if env:
                    counters[env.name()] += 1
                else:
                    counters["unknown"] += 1

                self.set_widgets(
                    [
                        Label("Detected environments:"),
                        "",
                        Label(
                            " ".join(
                                [
                                    f"{counter}: [bold primary]{str(counters[counter])}[/]"
                                    for counter in counters
                                ]
                            )
                        ),
                    ]
                )

                self.result.append((env, path))

        self._add_widget(Label("[bold green]Success"))

        sleep(1)
        self.is_working = False


def archive_path(path: Path, files: list[Path] = None):
    tar_path = path.with_name(path.name + ".tar.gz")
    tar = TarFile.open(tar_path, "w:gz")

    if files:
        for file in files:
            tar.add(file, arcname=file.name)
    else:
        tar.add(path, path.name)

    tar.close()

    return (tar_path, tar)


@app.command()
def archive(
    paths: list[Path],
    save_in_parent: Path = typer.Option(
        default=None,
        help="Archive and store in the parent archive(need provide a end path)",
    ),
    skip_dirs: str = typer.Option(default=""),
):
    skip_dirs = skip_dirs.split(",")

    paths = [path for path in paths if path.is_dir() and path.name not in skip_dirs]

    # # for dir in get_all_parents_upto_certain(save_in_parent, paths):

    # # print(tar_paths)

    if save_in_parent:
        # parents = get_all_parents(paths)
        parents = get_all_parents_upto_certain(save_in_parent, paths)

        tared_parents = []

        for i, parent in enumerate(parents):
            if (len(tared_parents) - 1) < i:
                tared_parents.append([])

            for j, parent_ in enumerate(parent):
                if (len(tared_parents[i]) - 1) < j:
                    tared_parents[i].append([])

                if i > 0:
                    (tar_path, _) = archive_path(
                        parent_, get_in_parent(parent_, tared_parents[i - 1])
                    )
                else:
                    (tar_path, _) = archive_path(
                        parent_, get_in_parent(parent_, tared_parents[i][j - 1])
                    )

                tared_parents[i][j].append(tar_path)
    else:
        bar = alive_it(
            paths,
            title="Archiving...",
            spinner="dots",
        )

        tar_paths = []

        for path in bar:
            (tar_path, _) = archive_path(path)
            tar_paths.append(tar_path)
            bar.text(f"Archived {path.name}")


@app.command()
def clean(paths: list[Path]):
    result = render_widget(EnvsLoadWidget(paths))

    result = [(env, path) for env, path in result if path.name != "pacl"]

    bar = alive_it(result, title="Cleaning...", spinner="dots")

    for env, path in bar:
        if env:
            env.clean(path)

        bar.text(f"Cleaned {path.name}")


@app.command()
def run(path: str):
    pass


if __name__ == "__main__":
    app()
