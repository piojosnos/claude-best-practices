# Debugging

## Diagnose before you fix

- Read the whole error message and understand what it says before changing anything.
- Form a hypothesis from the evidence, then fix. Do not guess, push and wait for a pipeline to tell you.
- After two fixes that did not work, stop patching. Step back, find the root cause, and rethink the approach.

## Scripts that run remotely or in CI

- A script that runs on another machine (a deploy script, a remote command, machine setup) writes its log to a file on that machine, in a well-known place with a timestamped name. CI job output can be truncated or lost.
- A script that drives remote commands also logs locally: its own actions and the output it receives.
- When such a script fails, read the logs on the target machine first, then form the hypothesis.
