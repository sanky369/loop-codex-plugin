---
name: loop-run
description: Execute one manual pass of a Loop spec in the current Codex thread, with discovery, triage, action, verification, reporting, and run ledger update.
---

# Loop Run

Use this skill when the user asks to run a Loop workflow once, test a loop, babysit a PR once, triage CI once, or manually execute a saved loop spec.

## Goal

Run exactly one loop pass unless the user explicitly asks for iteration. A loop pass is:

`Discover -> Triage -> Act -> Verify -> Report -> Record State`

## Workflow

1. Read `.loop/loop.yaml`.
2. Select the loop spec:
   - If the user names one, read `.loop/specs/<name>.md`.
   - If there is only one spec, use it.
   - If none exists, run or recommend `$loop-design`.
3. Before making edits, state what work the loop is about to do.
4. Execute discovery and triage first. If there is nothing actionable, skip edits and record a no-op run.
5. For code changes:
   - prefer the project's existing commands and patterns
   - keep the change narrow
   - do not bypass verification gates
6. Run the verification commands from the loop spec and `.loop/loop.yaml`.
7. Record the result:

   ```bash
   python3 <plugin-root>/scripts/loop_state.py append --root <project-root> --loop <loop-slug> --status <passed|failed|noop|blocked> --summary "<summary>"
   ```

8. Report the outcome, commands run, evidence, files changed, and next recommendation.

## Stop Conditions

Stop and report instead of continuing when:

- verification fails three times for the same reason
- the loop needs credentials, deployment, payment, or external send actions
- the required check is flaky or unavailable
- the next action would expand the scope beyond the loop spec

## Safety

Never claim a loop passed unless the verification evidence exists in this run.
