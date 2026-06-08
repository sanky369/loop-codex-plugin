---
name: loop-watch
description: Create a Claude-style recurring Loop from interval and prompt input, or convert a Loop spec into a recurring Codex Automation.
---

# Loop Watch

Use this skill when the user asks to schedule, watch, babysit, monitor, or run a Loop workflow on a recurring cadence.

## Goal

Turn interval/prompt input into a maintainable recurring Codex Automation. This intentionally mirrors the common `/loop` shape:

- interval + prompt: fixed schedule
- prompt only: dynamic cadence chosen by Codex after each pass
- interval only: fixed schedule using `.loop/loop.md`
- bare: dynamic cadence using `.loop/loop.md`

## Workflow

1. Read `.loop/loop.yaml`.
2. Parse the user's watch request with:

   ```bash
   python3 <plugin-root>/scripts/loop_prompt.py --root <project-root> --write <user interval/prompt text>
   ```

3. If the parsed prompt names an existing `.loop/specs/<slug>.md`, read it as extra guidance.
4. Draft an automation prompt that explicitly invokes `$loop-run`, includes the parsed prompt, and runs one pass only.
5. Include:
   - schedule or cadence
   - original loop prompt
   - project path
   - worktree preference
   - sandbox expectations
   - reporting destination
   - pause/stop conditions
6. If the `automation_update` tool is available, use it to create or update the automation.
7. If the tool is not available, save the draft prompt to `.loop/automations/<slug>.md` and tell the user it is ready to create from the Codex Automations pane.

## Defaults

- Prefer worktree isolation for Git repositories.
- Prefer read-only automations unless the loop's purpose requires edits.
- For edit-capable automations, require verification before reporting success.
- If the user supplied an interval, preserve it exactly unless it is unsafe.
- If the user supplied prompt only, pick the next sensible cadence after each pass rather than forcing a fixed schedule.
- If the user supplied neither interval nor prompt, use `.loop/loop.md`.

## Automation Prompt Shape

The prompt should be self-contained:

```text
$loop-run
Project: <absolute path>
Cadence mode: <fixed|dynamic>
Interval: <interval or choose next sensible interval>
Loop prompt:
<prompt text>

Run one pass only.
Use worktree isolation if changes are needed.
Record state in .loop/runs.jsonl.
Report findings with verification evidence.
Pause if approval, credentials, deployment, destructive changes, or repeated failures are required.
```
