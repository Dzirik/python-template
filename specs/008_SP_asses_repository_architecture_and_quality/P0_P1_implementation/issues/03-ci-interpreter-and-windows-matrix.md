# CI: interpreter selection + Windows matrix

> **Status:** `ready-for-agent`

## Parent

[`../BRAINSTORM.md`](../BRAINSTORM.md) — P0+P1 implementation. Report items: P0#1 (CI
interpreter selection), P1 D5 (Windows CI job). Decisions E and F.

## What to build

Make CI actually verify what the vision requires — both Python versions **and** both
platforms — before the repo goes to a remote. Today the `3.14` matrix leg would silently run
`3.13` (the committed `.python-version` outranks `setup-python` for `uv sync`), there is no
Windows runner, and the coverage-artifact upload step is dead.

1. **`.github/workflows/ci.yml`**
   - Matrix: `os: [ubuntu-latest, windows-latest]` × `python-version: ["3.13", "3.14"]`;
     `runs-on: ${{ matrix.os }}`.
   - Drop `actions/setup-python`. Pass `python-version: ${{ matrix.python-version }}` to
     `astral-sh/setup-uv` (sets `UV_PYTHON`, which outranks `.python-version`).
   - Windows-only step: `choco install make`; run the checks with `shell: bash` so
     `make all-secure` executes **identically** on both platforms (preserving the
     local/CI-parity property).
   - Replace `uv sync --extra dev` with the group-aware install for the new workflow
     (`uv sync`, which installs `default-groups`); or rely on `make all-secure`'s plain
     `uv run` auto-sync.
   - Set `EXPECTED_PYTHON: ${{ matrix.python-version }}` in the job env (consumed by the test
     below).
   - **Delete** the dead `Upload coverage reports` step (nothing produces `coverage/`; the
     coverage gate is dropped per D8).
2. **`tests/tests_utils/test_python_version_consistency.py`** — add a test that asserts the
   **running interpreter** matches the intended version, gated on the `EXPECTED_PYTHON` env
   var so it skips locally and runs in CI. This closes the real gap: the existing 12 tests
   check file *contents*, never `sys.version_info`.

```python
@pytest.mark.skipif("EXPECTED_PYTHON" not in os.environ, reason="asserts the running interpreter only in CI")
def test_running_interpreter_matches_ci_matrix() -> None:
    expected = os.environ["EXPECTED_PYTHON"]
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert actual == expected
```

## Scope

- **OWNS:** `.github/workflows/ci.yml`,
  `tests/tests_utils/test_python_version_consistency.py`.

## Acceptance criteria

- [ ] CI runs 4 jobs (ubuntu+windows × 3.13+3.14); each installs the interpreter matching its
      matrix leg (verified by the new test, not just file contents).
- [ ] Windows jobs run `make all-secure` via `choco install make` + `shell: bash`, identical to
      ubuntu.
- [ ] `actions/setup-python` is gone; interpreter comes from `setup-uv`.
- [ ] The dead coverage-artifact step is removed.
- [ ] The new interpreter test skips locally (no `EXPECTED_PYTHON`) and asserts in CI.

## Blocked by

- **Issue 01** — a clean checkout must pass the suite (CI runs no config-generation step).
- **Issue 02** — CI invokes the new uv-native workflow / `make all-secure`.
