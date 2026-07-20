# Test-suite quality: logger assertions + exceptions parametrization

## Parent

[`../PRD.md`](../PRD.md) — P3 implementation (polish), Item 7 (test-suite half). Covers user
stories 16, 17.

## What to build

Raise two existing test files to the house bar without changing any production behavior.

- **Logger level tests get real assertions.** Replace the assertion-free smoke tests (each
  currently just calls a level method under a "should not raise" comment) with `capsys`/`caplog`
  assertions proving each level method actually emits at the expected level. Follow the
  session-autouse `conftest.py` fixture (`ENV_LOGGER=logger_console`).
- **`test_exceptions.py` parametrized.** Fold the thirteen near-identical exception-description
  tests into one parametrized test over `(exception class, error code, description fragment)`.
  Keep the distinct `ExceptionExecutioner` behavior tests (raise-type, custom-description,
  traceback-via-`exception()`) as they are.

Scope boundary: touches only `test_logger.py` and `test_exceptions.py`. Production `logger.py`
is not modified here (its docstrings belong to the typo sweep).

## Acceptance criteria

- [ ] Each logger level test asserts observable output (via `capsys`/`caplog`) at the expected level, not merely absence of an exception.
- [ ] The thirteen exception-description tests are replaced by one parametrized test with equivalent coverage (every exception's code + description fragment still asserted).
- [ ] The existing `ExceptionExecutioner` behavior tests remain and pass.
- [ ] Test count/coverage of the exception and logger surfaces is not reduced.
- [ ] `make all-secure` is green.

## Blocked by

None - can start immediately.
