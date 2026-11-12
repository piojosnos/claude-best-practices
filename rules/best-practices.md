# Where the practices live

- The standing rules and skills are one git clone at `/home/sandbox/workspace/best-practices`. `~/.claude/rules` and the bundle skills in `~/.claude/skills` are links into it.
- To answer a question about the practices, read the files in that clone.
- To change one, edit the file in the clone by its real path, never through `~/.claude/rules` or `~/.claude/skills`. Work on a new branch cut from the updated `main` and commit it.
- Keep practices general. A rule states a principle that holds across projects; it names no project, repo, host setup or tool of the project that prompted it. Project detail goes in that project's CLAUDE.md or planning docs.
- Push only with the user's explicit go, then open a PR against `main` of the bundle repo with `gh pr create`. The user merges it. The git workflow rule has the branch names and the push and merge gates.
- A change reaches another sandbox only after its PR is merged and that sandbox runs `git pull` in its clone. A pull that adds or removes a skill shows after a restart, or after running `/etc/sbx/start.d/10-best-practices`.
- If the clone is missing, say so and point the user to `sbx-gh-login`, then `sbx-bundle-clone`.
