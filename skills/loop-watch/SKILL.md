---
name: loop-watch
description: Convert a Loop spec into a recurring Codex Automation prompt or set up the automation when automation tools are available.
---

# Loop Watch

Use this skill when the user asks to schedule, watch, babysit, monitor, or run a Loop workflow on a recurring cadence.

## Goal

Turn a saved loop spec into a maintainable recurring Codex Automation.

## Workflow

1. Read `.loop/loop.yaml` and the relevant `.loop/specs/<slug>.md`.
2. Draft an automation prompt that explicitly invokes `$loop-run` and names the loop spec.
3. Include:
   - schedule or cadence
   - project path
   - worktree preference
   - sandbox expectations
   - reporting destination
   - pause/stop conditions
4. If the `automation_update` tool is available, use it to create or update the automation.
5. If the tool is not available, save the draft prompt to `.loop/automations/<slug>.md` and tell the user it is ready to create from the Codex Automations pane.

## Defaults

- Prefer worktree isolation for Git repositories.
- Prefer read-only automations unless the loop's purpose requires edits.
- For edit-capable automations, require verification before reporting success.
- Use daily or hourly cadences first; avoid minute-level cadences unless the user asks.

## Automation Prompt Shape

The prompt should be self-contained:

```text
$loop-run
Project: <absolute path>
Loop spec: .loop/specs/<slug>.md
Run one pass only.
Use worktree isolation if changes are needed.
Record state in .loop/runs.jsonl.
Report findings with verification evidence.
```
