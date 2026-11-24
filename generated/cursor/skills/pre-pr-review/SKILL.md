---
name: pre-pr-review
description: "Self-review the current branch's diff against the loaded rules before opening a PR or pushing a review-round fix. Reports every finding with file and line, then fixes them on the user's go. Run manually with /pre-pr-review."
disable-model-invocation: true
---
<!-- GENERATED from skills/pre-pr-review/SKILL.md; edit that file and regenerate -->

# Pre-PR self-review

Run this on your own diff before opening a PR, and again before pushing each
review-round fix. A reviewer should spend time on design questions, not on issues
the author could have caught.

It reviews and reports; it changes nothing until the user says go. It never pushes.

## Arguments

- `/pre-pr-review`: review the current branch against its PR base (or `main` when
  there is no PR yet).
- `/pre-pr-review <base>`: review against the named base branch.

## Step 1: Resolve the diff

```bash
gh pr view --json baseRefName --jq .baseRefName   # the base, if a PR exists
git fetch --quiet origin
git diff --stat "origin/$BASE...HEAD"
```

Read the full diff file by file. Every check below runs on it.

## Step 2: Rules pass

- Check each changed file against the loaded rules: the general coding rules, the
  language file, the testing rules, prose style for docs and comments.
- Library before hand-roll: for any new helper longer than a few lines, look for the
  standard library or a dependency already on the build path that does the job.
- Strip narrative, banner and "what changed" comments. Keep only the comments that
  say something the code cannot.

## Step 3: Names

- For every new or renamed type, function, field and constant, ask: would a reader
  who did not write it know what it is from the name alone?
- Follow the project's naming conventions (suffixes, prefixes, casing). A name that
  needs a review thread to explain is the wrong name.

## Step 4: Renames and removals are complete

- For every rename in the diff, search the whole repo for the old name and every
  derived form: camelCase, CONSTANT_CASE, string values, file names, test names,
  comments and docs. The rename is done only when that search comes back empty.
- A rename includes string values consumed elsewhere (template variables, JSON keys,
  config keys). Check the consumers changed too, and that the consuming side still
  works (render it, load it).

## Step 5: Aliases and duplicate values

- For every new constant or alias whose value equals an existing one, check every
  usage of the existing one. If any code compares by value or branches on it, the
  alias couples the two by coincidence; flag it.

## Step 6: Behavior kept

- A check that moved (to another layer, or into one output mode) must not fire in
  fewer places than before. Confirm it still runs everywhere the old one did.
- A deleted TODO or TEMP note is fine only when the work it describes is done;
  otherwise it stays as a tracked `TODO(<phase/ticket>)`.

## Step 7: Tests

- Apply the testing rules to every test the diff touches.
- When the diff changes a shared message or format, re-read every assertion that
  matches on it; a `contains` check can turn into one that passes on any failure.
- Run the project's build and full test suite with its own scripts. When the change
  touches output the automated tests do not cover, run the real generation path too.

## Step 8: Commits

- For each commit on the branch, `git show --stat <commit>`: the expected files and
  line counts are there.
- After a `git mv` or `git rm`, the old path must not have been passed to `git add`:
  the bad pathspec aborts the whole add, and the commit lands with the move but none
  of the edits.

## Step 9: Report

List every finding as `path:line: problem`, grouped by step, with the command output
that proves each "nothing found" (grep counts, test summary). Then stop and wait.

- Never report "clean", "complete" or "no other cases" without that proof.
- On the user's go, fix the findings as atomic commits on the same branch, then rerun
  the affected steps.
