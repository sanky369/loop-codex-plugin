---
name: loop-run
description: Execute one manual pass of a Loop spec in the current Codex thread, with discovery, triage, action, verification, reporting, and run ledger update.
---

# Loop Run

Use this skill when the user asks to run a Loop workflow once, test a loop, babysit a PR once, triage CI once, or manually execute a saved loop spec.

## Goal

Run exactly one loop pass unless the user explicitly asks for iteration. A loop pass is:

`Prompt -> Plan -> Act -> Observe -> Verify -> Record -> Decide continue/pause`

## Workflow

1. Read `.loop/loop.yaml`.
2. Select the loop input:
   - If the user names one, read `.loop/specs/<name>.md`.
   - If the loop spec references `.loop/goals/<name>.md`, read the goal contract.
   - If there is only one spec, use it.
   - If the user provides a prompt, treat that as the loop prompt and use specs only as guidance.
   - If no prompt/spec exists, read `.loop/loop.md`.
   - If `.loop/loop.md` is missing, use the built-in maintenance prompt from `<plugin-root>/assets/default-loop.md`.
3. Before making edits, state the loop prompt, bounded action, goal/done condition, and verification gate.
4. Execute discovery and triage first. If there is nothing actionable, skip edits and record a no-op run.
5. For code changes:
   - prefer the project's existing commands and patterns
   - keep the change narrow
   - do not bypass verification gates
   - use worktree isolation when the profile/spec requires it
6. For risky or unattended edit-capable loops, use the maker/checker split:
   - explorer gathers evidence
   - worker makes the bounded change
   - verifier checks the goal and evidence independently
7. Run the verification commands from the loop spec, goal contract, and `.loop/loop.yaml`.
8. If behavior, architecture, public docs, or project direction changed, append a comprehension note:

   ```bash
   python3 <plugin-root>/scripts/loop_state.py note --root <project-root> --file COMPREHENSION.md --heading "<loop-slug>" --body "<what changed and what the human should understand>"
   ```

9. Record the result:

   ```bash
   python3 <plugin-root>/scripts/loop_state.py append --root <project-root> --loop <loop-slug> --status <passed|failed|noop|blocked|paused> --summary "<summary>" --prompt "<prompt>" --cadence "<cadence>" --next-action "<next action>"
   ```

10. Report the outcome, commands run, evidence, files changed, next recommendation, and whether the loop should continue, pause, or wait for human input.

## Stop Conditions

Stop and report instead of continuing when:

- verification fails three times for the same reason
- the loop needs credentials, deployment, payment, or external send actions
- the required check is flaky or unavailable
- the next action would expand the scope beyond the loop spec
- the prompt is too vague to choose a safe smallest next action
- the verifier cannot independently confirm the done condition
- the human engineer would lose important understanding if the loop continued without review

## Safety

Never claim a loop passed unless the verification evidence exists in this run.
