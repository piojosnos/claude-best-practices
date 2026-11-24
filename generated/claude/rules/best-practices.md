<!-- GENERATED from rules/best-practices.md; edit that file and regenerate -->

# Where the practices live

- The standing rules and skills are one git clone of the best-practices repo. The rules and skills an agent reads are links into that clone; follow one (for example `readlink ~/.claude/rules`) to find it.
- To answer a question about the practices, read the files in that clone.
- To change one, edit the file in the clone by its real path, never through a link such as `~/.claude/rules` or `~/.claude/skills`. Work on a new branch cut from the updated `main` and commit it.
- Write a rule as the instruction itself. Add a `Why:` line only when it changes how the rule is applied in a case the rule does not spell out; a why that restates the rule only costs context.
- Keep practices general. A rule states a principle that holds across projects; it names no project, repo, host setup or tool of the project that prompted it. Project detail goes in that project's CLAUDE.md or planning docs.
- Push only with the user's explicit go, then open a PR against `main` of the best-practices repo with `gh pr create`. The user merges it. The git workflow rule has the branch names and the push and merge gates.
- A change reaches another clone only after its PR is merged and that clone runs `git pull`. A pull that adds or removes a skill shows once the links are refreshed.
- If the clone is missing, say so.
