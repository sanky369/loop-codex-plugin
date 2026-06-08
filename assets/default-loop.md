# Default Loop Prompt

Run one maintenance pass for this project.

1. Read `.loop/loop.yaml`.
2. Inspect the latest `.loop/runs.jsonl` entries.
3. Identify the smallest useful next action already implied by the project state, user transcript, loop specs, failing checks, or stale docs.
4. Prefer read-only checks first.
5. If edits are needed, keep them narrow and run the required verification gates.
6. Record the pass in `.loop/runs.jsonl`.
7. Report what happened, evidence, and whether the loop should continue, pause, or wait for human input.

Do not start a new initiative outside the existing project direction. Do not deploy, delete, spend money, rotate secrets, send external messages, or make irreversible changes without explicit human approval.
