# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Windows-first (also Linux/macOS) Python project template for data-oriented work. It ships a Singleton-based config + logger system, a TOML/env-var configuration layer, structured exceptions, an sklearn-style transformer base, Plotly visualisation helpers, Jupyter + Marimo notebook workflows, and a production process-supervision system (watchdog/checker). The package root is `src/` — all imports are absolute from it (`from src.utils.application_config import ApplicationConfig`).

For the template's purpose, scope, guiding principles, constraints, and roadmap, see [`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md) — the authoritative statement of *why* this project exists and what belongs in it.

## Tooling & commands

Everything runs through the **`Makefile`**, and all Python invocations use **`uv run --no-project`**. Dependencies are managed by `uv` — never hand-edit `uv.lock`; use `make add-lib library=<name>` / `make remove-lib library=<name>` (append `-win` variants for Windows-only deps, which go in the `windows` optional-dependency group).

Setup: `make create-venv` (or `create-venv-linux`) — installs Python 3.13, creates `.venv`, and generates the git-ignored working files (`make_config.mk`, `.env`, `configurations/python_personal.toml`, `notebooks/raw/playground_notebook.py`) from their templates. Then `make install-hooks` (`-linux`).

Quality checks (each has a `-no-clear` variant that skips the console clear — use those in non-interactive contexts):

- `make mypy` — mypy `--strict` on `src` and `tests`
- `make format-check` / `make format-fix` — ruff formatter
- `make lint-check` / `make lint-fix` — ruff linter (docstring rules `D` excluded here)
- `make docstring-check` / `make docstring-fix` — ruff docstring rules only
- `make test` / `make test-detailed` — pytest (quiet / verbose)
- `make security-check` — bandit + pip-audit (specific CVEs are ignored in the Makefile recipe)
- `make all` — mypy + format + lint + docstring + test (what to run before pushing)
- `make all-secure` — `all` plus security; **this is exactly what CI runs** (matrix: Python 3.13/3.14 on ubuntu)
- `make cover` — HTML coverage report into `coverage/`

### Single-file / single-test workflow

Per-file targets read `FILE_FOLDER` and `FILE_NAME` from `make_config.mk` (git-ignored; created from `make_config_template.mk`). They map to `src/<FILE_FOLDER>/<FILE_NAME>.py`, `tests/tests_<FILE_FOLDER>/test_<FILE_NAME>.py`, and an optional `.txt` doctest file. Edit `make_config.mk`, then run `make mypy-f`, `make lint-check-f`, `make test-f`, `make all-f`, etc. To run one test file directly: `uv run --no-project python -m pytest tests/tests_utils/test_leap_year.py`.

### Notebooks

- `make jupyter` — starts Notebook 7 (JupyterLab-based). `.py` ↔ `.ipynb` are paired via **jupytext** (`py:light` format, see `jupytext.toml`) — edit the `.py` files under `notebooks/`.
- `make marimo` — Marimo reactive notebooks (stored as pure `.py`, no jupytext). `make marimo-app notebook=<f.py>`, `make marimo-new notebook=<f.py>`, `make marimo-convert notebook=<path.ipynb>`.

## Architecture

### Configuration (Singleton + TOML + env vars)

Resolution chain: `.env` sets `ENV_CONFIG` (default `python_personal`) → names a `configurations/<name>.toml` file (TOML syntax) → parsed by the stdlib `tomllib` → loaded via `typedload` into the `ApplicationConfigData` NamedTuple tree (`src/utils/application_config_data.py`). `ApplicationConfig` (`src/utils/application_config.py`) is a **Singleton** (`src/utils/singleton_meta.py`); call `ApplicationConfig().get_data()`. `Envs` (`src/utils/envs.py`) is the only place env vars are read/written — go through it, don't touch `os.environ` directly. Config `.toml` files search several candidate paths so they resolve from both repo root and CWD (CI). There are three config profiles (`python_repo`, `python_personal`, `python_local`) and five logger profiles, all `.toml` now. Config profiles used to be HOCON parsed by the third-party `pyhocon`; see [ADR 0003](docs/adr/0003-toml-config-profiles.md) and [`docs/tutorials/CONF_TO_TOML.md`](docs/tutorials/CONF_TO_TOML.md) for the migration rationale and upgrade steps. `.conf` is retired from the repository entirely — see [ADR 0004](docs/adr/0004-logger-profiles-toml-dictconfig.md) for the Logger's own migration off it.

### Logging

`Logger` (`src/utils/logger.py`) is also a Singleton; its config is chosen by `ENV_LOGGER` naming a `logger_*.toml` file under `configurations/loggers/`, parsed by the stdlib `tomllib` and loaded via `logging.config.dictConfig`. It integrates a `Timer` and logs the active git branch on init. Logger profiles used to be stdlib INI loaded via `logging.config.fileConfig`; see [ADR 0004](docs/adr/0004-logger-profiles-toml-dictconfig.md) for the migration rationale.

### Exceptions (Strategy pattern)

Custom exceptions subclass `CustomException` (grouped in `src/exceptions/data_exception.py` and `development_exception.py`), each carrying an error code + description. Raise them through `ExceptionExecutioner(SomeException).log_and_raise("...")` — it logs then raises in a unified way.

### Transformers & MetaClass

`BaseTransformer` (`src/transformations/base_transformer.py`) defines an sklearn-style `fit`/`predict`/`fit_predict`/`inverse` interface plus `get_params`/`restore_from_params`. It extends `MetaClass` (`src/utils/meta_class.py`), the common base giving every class a `ClassInfo` (type + name + descriptions) for unified monitoring/logging. Transformers do **not** validate input data shape — that is the child class's responsibility.

### Production supervision (`src/scripts_production/`)

`watchdog.py` supervises worker subprocesses (restart on crash/freeze), driven by `configurations/watchdog_*.toml` loaded through `WatchdogConfig`. `heartbeat.py` optionally pings healthchecks.io (URLs from `HEALTHCHECK_PING_URL` in `.env`). `checker.py` is the monitored-worker example. See `docs/tutorials/PERSISTENT_RUN.md` and `docs/tutorials/CHECKER_SCHEDULER_SET_UP.md`.

## Code style (STRICT — match existing files exactly)

`make all` gates every push and CI runs `make all-secure`, so new code must pass mypy `--strict`, ruff format, ruff lint, and the ruff docstring rules. Beyond passing the tools, **mirror the house style already present in every `src/` file** — new code should be indistinguishable from existing code.

### Typing (mypy `--strict`)

- **Fully annotate everything**: every function/method parameter and return type, including `-> None`. No bare/implicit `Any` from missing annotations.
- Use **modern built-in generics and union syntax** (`target-version = py311`): `list[str]`, `dict[str, Any]`, `X | None` — **never** `List`, `Dict`, `Optional[X]`, or `Union[...]`.
- **Annotate instance attributes in `__init__`** even when assigned later, e.g. `self._do_attribute: TimeAttributes` / `self._dt_attr_names: list[str] = []`.
- Type numpy arrays as `ndarray[Any, dtype[Any]]`; declare a local's type before a conditional assignment when needed (`x: ndarray[Any, dtype[Any]]`).
- Use **`NamedTuple` subclasses** for structured/immutable data (config trees, descriptions) — see `application_config_data.py`, `meta_class.py`. Not dataclasses or dicts.

### Docstrings (ruff `D`, numpy convention)

Every module, class, and function/method (public **and** private) has a triple-quoted docstring. The house format is a custom reST/Sphinx style, **not** numpy-section style:

```python
def convert_datetime_to_string_date(now: datetime | None = None, sep: str = "-") -> str:
    """
    Converts now to string format yyyy-dd-yy-hh-mm-ss<-micro>.
    :param now: datetime. Date in datetime format. Default value is datetime.now().
    :param sep: str. Separator in between time data. Default is "-".
    :return: str.
    """
```

- Docstring text **starts on the line after `"""`** (D213), and the closing `"""` is on its own line — even for one-liners (D200 is disabled to allow this multi-line form uniformly).
- Summary line is **descriptive, not imperative** (D401 disabled): "Converts…", "Gets…", "Fits." — not "Convert…".
- Document params as `:param <name>: <Type>. <description>.` and returns as `:return: <Type>. <description>.` — repeat the type in the text even though it's annotated. This is the established pattern; keep it.

### Naming, imports, structure

- PEP8 naming enforced by ruff `N`: `PascalCase` classes, `snake_case` functions/vars, `UPPER_SNAKE` constants. Prefix non-public attributes/methods with a single `_`.
- Imports: **absolute from the `src.` root** (`from src.utils.application_config import ApplicationConfig`), isort-ordered (ruff `I`). Prefer importing specific names (`from numpy import array, concatenate, ndarray`).
- Many modules end with an `if __name__ == "__main__":` demo/self-test block — follow that for new runnable modules.
- ruff line length is **120**; formatter uses **double quotes**, space indent.

### Suppressions (targeted only — never blanket)

Suppress a specific rule on the specific line, with the code, and (for security) a reason: `# noqa: ARG002`, `# type: ignore[call-arg]`, `# nosec B404`, or scoped `# pylint: disable=...` / `# pylint: enable=...` pairs. Do not add file-wide `# noqa` or loosen the config to make code pass.

## Conventions & gotchas

- **Tests set `ENV_RUNNING_UNIT_TESTS=True` and force `ENV_LOGGER=logger_console`** (see `tests/conftest.py`, session autouse). When that flag is set, `ExceptionExecutioner` skips logging — keep this in mind when testing error paths. Because config/logger are Singletons, set env vars via `Envs` *before* first instantiation.
- Test tree mirrors `src/` with a `tests_` prefix (`src/utils/` → `tests/tests_utils/`). Tests are parametrized pytest; some modules also carry `.txt` doctest files run by pytest. The `lint`/`docstring` targets apply ruff to `tests` too — tests follow the same style rules as `src`.
- Git hooks: **pre-commit blocks commits to `main`/`master`/`develop`** (work on a feature branch); pre-push runs security checks. Bypass only with `--no-verify` when truly necessary.
- Coverage gate: `fail_under = 25` in `pyproject.toml`.
- The `Makefile` uses tabs — do not let an editor convert them to spaces (there's a warning banner at the top of the file).
