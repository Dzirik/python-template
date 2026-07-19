# Move `SPECIAL_LOGGER_FILE_NAME` → `logger.py` as an independent literal

> **Status:** `ready-for-agent`

## Parent

[`specs/006_resolve_global_and_venv_constants/BRAINSTORM.md`](../BRAINSTORM.md) — *Resolve global & venv constants*

## What to build

Co-locate the error-path fallback log filename with its only consumer, `logger.py`, and correct a false-duplication misconception. `SPECIAL_LOGGER_FILE_NAME` is used solely by `logger.py:_log_bad_file()` — the fallback destination for a single error line written when the *selected* logger profile file is missing.

This is **not** a third copy of the default logger profile name. Its value (`"logger_file_limit_console.log"`) only coincidentally shares a prefix with `DEFAULT_LOGGER`; it does not match any real profile's output (`logger_file_limit_console.toml` actually writes to `python_log_file_limit_console.log`). The in-code comment claiming it "should be the same as in config files for logger" is false today. It must therefore stay an **independent literal** — deriving it from `DEFAULT_LOGGER` (e.g. `f"{DEFAULT_LOGGER}.log"`) would invent a false coupling whereby changing the default profile silently renames the fallback file.

End-to-end behaviour after this slice: `SPECIAL_LOGGER_FILE_NAME` is defined in `logger.py` with its current value unchanged; `_log_bad_file()` writes to the same path as before.

Scope:

- **`logger.py`** — define `SPECIAL_LOGGER_FILE_NAME = "logger_file_limit_console.log"` as a module constant (value unchanged), replacing the import from `global_constants`. **Do not** derive it from `DEFAULT_LOGGER`. Drop the false "should be the same as in config files for logger" comment and add a one-line comment stating its real role: the error-path fallback log destination used when a selected logger profile is missing.
- **`global_constants.py`** — remove the `SPECIAL_LOGGER_FILE_NAME` line (and its now-orphaned "Special variables" comment block).

## Acceptance criteria

- [ ] `logger.py` defines `SPECIAL_LOGGER_FILE_NAME` locally with the unchanged value and no longer imports it from `global_constants`.
- [ ] The constant is a plain literal — not derived from `DEFAULT_LOGGER` or any other value.
- [ ] The false "should match config files" comment is gone; a comment explaining the error-path fallback role is present.
- [ ] `_log_bad_file()` behaviour and the fallback file path are unchanged.
- [ ] `global_constants.py` no longer defines `SPECIAL_LOGGER_FILE_NAME`.
- [ ] `make all-secure` green on Python 3.11 / 3.12 / 3.13.

## Blocked by

- None - can start immediately.
