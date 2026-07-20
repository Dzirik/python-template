"""
Marimo documentation notebook - explains, in markdown cells, how marimo's reactive execution model works, the
``src``-import bootstrap pattern used by ``marimo/template/template_notebook.py``, and how this workflow differs
from the jupytext-paired Jupyter notebooks under ``notebooks/``.

This notebook is documentation-only: unlike the template notebook, it does not instantiate the Envs/Logger/
ApplicationConfig singletons - see ``marimo/template/template_notebook.py`` for that integration reference.
"""

import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    """
    Imports marimo's UI/markdown namespace under its conventional alias.

    :return: tuple. Single-element tuple exposing ``mo`` to later cells.
    """
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    """
    Renders the notebook title and scope.

    :param mo: module. marimo's public namespace.
    """
    mo.md(
        """
        # Marimo Documentation Notebook

        Explains marimo's reactive execution model, the `src`-import bootstrap used by
        `marimo/template/template_notebook.py`, and how this second notebook ecosystem differs from the
        jupytext-paired Jupyter notebooks under `notebooks/`.
        """
    )
    return


@app.cell
def _(mo):
    """
    Explains marimo's reactive, dataflow-graph execution model.

    :param mo: module. marimo's public namespace.
    """
    mo.md(
        """
        ## How Marimo Reactivity Works

        A marimo notebook is a **directed acyclic graph**, not a sequence of cells executed top-to-bottom. Each
        cell is a function whose *arguments* are the global variables it reads but does not define (its
        "refs"), and whose *return value* is the global variables it defines (its "defs"). marimo statically
        analyzes every cell's source - without running it - to build the graph: there is an edge from cell A to
        cell B whenever B references a variable defined by A.

        **The single rule that drives everything:** when a cell runs, every other cell that references a
        variable it defines runs automatically, in topologically-sorted order. This means:

        - **Cell order in the file is presentation order, not execution order.** You can rearrange cells in the
          file for readability; the dataflow graph, not file position, decides what runs when.
        - **Re-running a cell re-runs its descendants**, not the cells above or below it. Change a `mo.ui.slider`
          value and only the cells that actually depend on it recompute - nothing else.
        - **There is no hidden state.** Unlike a Jupyter kernel, where a variable can be defined in a cell
          that was later deleted or never re-run (leaving stale state only visible in `dir()`), a marimo
          notebook's variables always match what its current cells define. Re-opening the notebook and running
          it top-to-bottom always reproduces the same state as the interactive session.

        The reactive example at the bottom of `marimo/template/template_notebook.py` demonstrates this
        concretely: moving the `amplitude_slider` UI element re-runs the cell that displays its value
        automatically - no "run all cells" step required, which is marimo's key differentiator from Jupyter's
        manual, order-dependent execution model.
        """
    )
    return


@app.cell
def _(mo):
    """
    Creates a small, self-contained reactive demo to make the dataflow-graph explanation tangible.

    :param mo: module. marimo's public namespace.
    :return: tuple. Single-element tuple exposing the number input so the next cell can react to it.
    """
    repetitions_input = mo.ui.number(start=1, stop=5, value=1, label="Repetitions")
    repetitions_input
    return (repetitions_input,)


@app.cell
def _(mo, repetitions_input):
    """
    Reruns automatically whenever ``repetitions_input`` changes - this cell's body is its only ref.

    :param mo: module. marimo's public namespace.
    :param repetitions_input: mo.ui.number. The number input created in the previous cell.
    """
    mo.md("Reactive! " * repetitions_input.value)
    return


@app.cell
def _(mo):
    """
    Explains the ``src``-import bootstrap pattern used by the template notebook.

    :param mo: module. marimo's public namespace.
    """
    mo.md(
        """
        ## The `src`-Import Bootstrap Pattern

        This repository's package root is `src/`, and every module in it is imported absolutely
        (`from src.utils.application_config import ApplicationConfig`). For that import to resolve, the
        repository root must be on `sys.path` - but a marimo notebook can be launched three different ways with
        three different current working directories:

        - `make marimo`, which `cd`s into `marimo/` before starting the editor.
        - The marimo UI launched directly (`uv run marimo edit marimo/template/template_notebook.py`), whose
          CWD is whatever the invoking shell happened to be in.
        - `uv run marimo edit ...` run from the repository root.

        `marimo/template/template_notebook.py`'s bootstrap cell solves this by walking up from its own
        `__file__` location - never from `Path.cwd()` - until it finds a directory containing a marker file
        (`pyproject.toml` or `.git`), then inserts that directory onto `sys.path`. This is the same marker-walk
        `src/utils/project_paths.py` uses internally (hand-rolled in the notebook cell, since `src` is not yet
        importable when the bootstrap cell runs). Because the search is anchored to the notebook file's own
        location on disk rather than the process's current directory, it resolves to the identical repository
        root regardless of how or from where the notebook was launched.

        Compare this to the Jupyter templates under `notebooks/template/`, which instead append
        `os.getcwd()`-relative `".."` / `"../.."` entries to `sys.path`. That only works if Jupyter happens to
        be started from a predictable directory - it silently breaks if the launch directory changes. The
        marimo bootstrap is strictly more robust: it is correct by construction rather than by convention.
        """
    )
    return


@app.cell
def _(mo):
    """
    Explains how the marimo workflow differs from the jupytext-paired Jupyter workflow.

    :param mo: module. marimo's public namespace.
    """
    mo.md(
        """
        ## How This Differs From the Jupytext-Paired Jupyter Workflow

        The `notebooks/` ecosystem pairs each notebook as two files kept in sync by jupytext: a `.py` file
        (`py:light` format, the one you actually edit - see `jupytext.toml`) and a generated `.ipynb` file that
        Jupyter/Notebook 7 actually executes. The `.py` file is source of truth for version control, but it is
        not itself runnable as a notebook - it needs jupytext to convert it back into the paired `.ipynb` before
        Jupyter can run it.

        The `marimo/` ecosystem has no such pairing, and needs none:

        - A marimo notebook **is** a plain `.py` file - no companion `.ipynb`, no conversion step, nothing to
          keep in sync. What you edit is exactly what runs.
        - Opening the file with `make marimo` / `marimo edit` parses that same `.py` file directly into the
          editor's cell graph; saving from the editor writes the identical `.py` file back out.
        - The file is importable as an ordinary Python module (`@app.function`/`@app.class_definition` cells are
          serialized top-level) and runnable as a script (`python template_notebook.py` executes every cell in
          topological order, as demonstrated by the `if __name__ == "__main__": app.run()` guard at the bottom
          of `template_notebook.py`).

        In short: where the Jupyter side treats `.py` as a *source representation* of a notebook that lives
        "for real" as an `.ipynb`, the marimo side treats `.py` as the notebook - full stop.
        """
    )
    return


if __name__ == "__main__":
    app.run()
