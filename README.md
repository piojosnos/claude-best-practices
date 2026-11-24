# best-practices

Standing rules and skills for AI coding agents, shared across projects.

```text
rules/                 rule masters (conventions: prose style, git workflow, languages)
skills/                skill masters (reusable agent workflows)
templates/<agent>/     how each agent's files are laid out
practices/             the generator (Python)
generated/<agent>/     what each agent loads; nobody edits it by hand
tests/                 pytest checks of the generator and of generated/
```

Edit the masters. The generator renders them into `generated/`, which is committed.

## Master formats

| Master | Format | Claude gets | Cursor gets |
|--------|--------|-------------|-------------|
| Rule | `rules/<name>.md`, optional `paths` frontmatter | `.md` with `paths` | `.mdc` with `globs` and `alwaysApply` |
| Skill | `skills/<name>/SKILL.md` | the same file | the same file |

A rule without frontmatter is always loaded. Every generated file starts with a header that names its master.

## Commands

Run from the clone root:

```text
uv run --locked python -m practices.generate   # render the masters into generated/
uv run --locked python -m practices.gate       # the gate: ruff, the drift check, then pytest
```

The gate stops at the first failing step. `uv run --locked python -m practices.check` fails if `generated/` differs from the masters, and `uv run --locked pytest -q` runs the tests; both also run alone.

`uv` keeps its environment in `.venv/`, which git ignores. A checkout shared by two operating systems should run the commands on one of them only.

## License

Licensed under the Mozilla Public License 2.0 (MPL-2.0). See [LICENSE](LICENSE).
