---
paths:
  - "**/*.py"
---

# Python

## Code style

- No monkey-patching: never replace a method, attribute or module-level object at runtime to change behavior. Use dependency injection or a config override instead.
- Explicit imports; never `from module import *`.
- Type hints on public function signatures. Small private helpers are exempt.
- No bare `except:`. Catch the specific exception; `except Exception` only at a top-level boundary that logs and reports.
- Use `pathlib.Path` for file and folder work.
- Module-level constants sit at the top of the module, in `UPPER_SNAKE_CASE`.
- Log through the `logging` module, with context in the message (record id, file name, counts). `print` is only for a CLI's real output.

## Project layout

- Business logic lives in modules. The entry point (a declared script or an `if __name__ == "__main__":` block) stays thin and calls into them.
- Declare the Python version and the dependencies in `pyproject.toml` and lock them with `uv` (commit `uv.lock`). Run through `uv run`; no hand-made virtualenv and no `requirements.txt`.
- Config lives in JSON files; environment variables override per environment. Secrets come only from the environment.

## Databases

- Parameterized queries only. Never build SQL with string formatting.
- Create connections in one place (a DAO or service) and pass them in. Do not scatter `connect()` calls.

## Testing

- Use pytest. Shared setup (connections, cleanup, config overrides) lives in `conftest.py` fixtures, so test files hold the assertions.
- To change behavior in a test, prefer, in this order: a config override, a wrapper executable that stands in for a real one, dependency injection, then `unittest.mock.patch` for a true external boundary (network, clock). Use `patch` only as a context manager or decorator, never as a raw attribute assignment.
- A test removes its own data in teardown (`TRUNCATE` or `DELETE`) instead of relying on a transaction rollback.
- When the code runs on several operating systems, so do its tests. An OS check belongs only in OS plumbing (an executable wrapper), never in business logic.
