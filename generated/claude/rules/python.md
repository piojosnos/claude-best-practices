---
paths:
  - "**/*.py"
---
<!-- GENERATED from rules/python.md; edit that file and regenerate -->

# Python

## Code style

- No monkey-patching: never replace a method, attribute or module-level object at runtime to change behavior. Use dependency injection or a config override instead.
- Explicit imports; never `from module import *`.
- Type hints on public function signatures. Small private helpers are exempt.
- No bare `except:`. Catch the specific exception; `except Exception` only at a top-level boundary that logs and reports.
- Use `pathlib.Path` for file and folder work.
- Module-level constants sit at the top of the module, in `UPPER_SNAKE_CASE`.
- Log through the `logging` module, with context in the message (record id, file name, counts). `print` is only for a CLI's real output.

## Module layout

- Put a banner before each logical section of a module, in the same shape as shell scripts: a rule line is `#`, a space and 80 hyphens (82 columns). The title says what the section holds. An optional why of at most two lines sits under the title, closed by a third rule line. Without a why, the title sits between two rules.

  ```python
  # --------------------------------------------------------------------------------
  # Checks of the state folders
  # --------------------------------------------------------------------------------
  # A root-owned folder here breaks the agent's next write.
  # --------------------------------------------------------------------------------
  ```

- A section groups related functions (one topic, one public function and its private helpers). A function does not get a titled banner; its name already says what it does.
- Separate every two functions and classes with the member rule of the general coding rule: `#`, a space and 80 hyphens on its own line, with no title. Keep the two blank lines PEP 8 wants before it and one blank line after it, before the `def`. This holds in tests and helpers too.

  ```python
      return run_command(command_name, action)


  # --------------------------------------------------------------------------------

  def main(argument_list: list[str]) -> int:
  ```
- The module header uses the same shape: the purpose is the title.
- A module with an entry point ends with a `Main / Entry Point` banner over the `if __name__ == "__main__":` block.

## Project layout

- Business logic lives in modules. The entry point (a declared script or an `if __name__ == "__main__":` block) stays thin and calls into them.
- Declare the Python version and the dependencies in `pyproject.toml` and lock them with `uv` (commit `uv.lock`). Run through `uv run`; no hand-made virtualenv and no `requirements.txt`.
- Config lives in JSON files; environment variables override per environment. Secrets come only from the environment.

## Databases

- Parameterized queries only. Never build SQL with string formatting.
- Create connections in one place (a DAO or service) and pass them in. Do not scatter `connect()` calls.

## Linting

- Run the linter inside the project's test gate script, so a finding fails the gate like a failing test.
- Configure it to match the code (line length, import style) and exclude generated code.

## Testing

- Use pytest. Shared setup (connections, cleanup, config overrides) lives in `conftest.py` fixtures, so test files hold the assertions.
- To change behavior in a test, prefer, in this order: a config override, a wrapper executable that stands in for a real one, dependency injection, then `unittest.mock.patch` for a true external boundary (network, clock). Use `patch` only as a context manager or decorator, never as a raw attribute assignment.
- A test removes its own data in teardown (`TRUNCATE` or `DELETE`) instead of relying on a transaction rollback.
- When the code runs on several operating systems, so do its tests. An OS check belongs only in OS plumbing (an executable wrapper), never in business logic.
