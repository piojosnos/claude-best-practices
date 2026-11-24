---
name: update-practice
description: Change, add or remove a rule or a skill of the best-practices repo. Edits the master, regenerates the agent copies, runs the checks, commits on a new branch and opens the PR after the user's push go. Use when the user says "change the rule", "add a practice", "remove the skill", "update the practices", or asks to record a new standing practice.
---

# Update a practice

The user only says what to change. This skill edits the master, regenerates the agent
copies, checks them, commits on a new branch and opens the PR once the user gives the
push go. It never edits `generated/` by hand, never pushes without the go and never
merges.

## Steps

1. Find the clone. Resolve this skill file's link (for example with `realpath`) and
   take the repository root with `git rev-parse --show-toplevel`. Work there. If the
   clone cannot be found, say so and stop.

2. Start clean and current. The worktree must be clean; if it is not, show what is
   changed and ask. Run `git fetch origin`, then create `chore/<desc>` (or `feat/` or
   `fix/`) from `origin/main`.

3. Edit the master by its real path.
   - A rule is `rules/<name>.md`: plain Markdown. A frontmatter is optional and holds
     one key, `paths`, a list of quoted globs with no comma inside a glob. No
     frontmatter means the rule is always loaded.
   - A skill is `skills/<name>/SKILL.md` with `name` (equal to the folder name) and
     `description`, plus the optional boolean `disable-model-invocation`. Extra files
     sit next to it.
   - Adding a practice means a new master; removing one means deleting its master.
   - Keep the text agent-neutral and general, and follow the prose rules.

4. Regenerate: `uv run --locked python -m practices.generate`.

5. Check: `uv run --locked python -m practices.check` and `uv run --locked pytest -q`.
   Fix the master, never the output, until both pass.

6. Commit the master and its generated output together. Stage explicit paths (the
   master and `generated`), never `git add -A`. Use a conventional message with no AI
   attribution.

7. State the branch and ask for the push go. On the go, push it and open the PR with
   `gh pr create --base main --head <branch>`. The user merges; never merge.

8. Say that other clones get the change after the merge and a pull of `main`.
