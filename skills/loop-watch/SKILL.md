---
name: loop-watch
description: Create a Claude-style recurring Loop from interval and prompt input, or convert a Loop spec into a recurring Codex Automation.
---

# Loop Watch

Use this skill when the user asks to schedule, watch, babysit, monitor, or run a Loop workflow on a recurring cadence.

## Goal

Turn interval/prompt input into a maintainable recurring Codex Automation. This intentionally mirrors the Claude Code `/loop` shape, including running the task once immediately and then continuing on a cadence.

## Parsing (priority order)

The helper `scripts/loop_prompt.py` applies these rules; do not re-parse by hand.

1. **Leading interval token** — `5m <prompt>`, `2h <prompt>`, `30s <prompt>`. First token is the interval; the rest is the prompt. → fixed cadence.
2. **Trailing `every <N> <unit>` clause** — `check the deploy every 20m`, `run tests every 5 minutes`. The interval is stripped from the end; the rest is the prompt. Only matches when a real time unit follows `every`, so `check every PR` has **no** interval. → fixed cadence.
3. **No interval** — anything else. → dynamic cadence (Codex picks the next interval after each pass).

Forms that resolve the prompt from `.loop/loop.md` (or the built-in default) when none is given:

- interval only (`5m`, `every 2 hours`) → fixed cadence, default prompt.
- bare (no input) → dynamic cadence, default prompt.

## Workflow

1. Read `.loop/loop.yaml`.
2. Parse the user's watch request:

   ```bash
   python3 <plugin-root>/scripts/loop_prompt.py --root <project-root> --write <user interval/prompt text>
   ```

   The JSON result includes `rule`, `interval`, `cadence_mode`, `cron`, `cadence_human`, `cron_note`, `prompt`, and the rendered `automation_prompt`.
3. If `cron_note` is set, tell the user what cadence you rounded to and why before creating anything.
4. If the parsed prompt names an existing `.loop/specs/<slug>.md`, read it as extra guidance.
5. **Run one pass now** (mirrors `/loop` executing immediately): invoke `$loop-run` with the parsed prompt before scheduling, so the user sees a result this session and the first firing is not the first run. Skip the immediate run only if the user explicitly asked to "just schedule it."
6. Create the recurring automation:
   - For **fixed** cadence, use the `cron` (or `cadence_human`) from the parser.
   - For **dynamic** cadence, schedule a conservative default cadence and instruct the pass to choose the next sensible interval; if the automation system supports per-run rescheduling, have `$loop-run` update the next schedule at the end of each pass.
   - If the `automation_update` tool is available, use it. Otherwise save the rendered `automation_prompt` to `.loop/automations/<slug>.md` and tell the user it is ready to create from the Codex Automations pane.
7. Confirm back to the user: schedule (human + cron), the loop prompt, project path, worktree/sandbox expectations, reporting destination, and the pause/stop conditions.

## Durable vs one-off

Codex Automations are durable — they keep firing until disabled or deleted, which is the analogue of a cloud schedule. There is no separate ephemeral "this session only" loop:

- For a recurring loop, create an automation (above).
- For a single run right now with no schedule, use `$loop-run` directly instead of this skill.

## Stop / pause

Tell the user how to end the loop, and honor these in `$loop-run`:

- **Pause/stop:** disable or delete the automation in the Codex Automations pane (the analogue of cancelling a scheduled job). Record a final ledger entry with status `paused` or `completed`.
- **Auto-pause:** the loop pauses itself when a failure repeats three times, credentials/approval are required, the scope would expand beyond the spec, or a required check is unavailable.

## Defaults

- Prefer worktree isolation for Git repositories.
- Prefer read-only automations unless the loop's purpose requires edits.
- For edit-capable automations, require verification before reporting success.
- If the user supplied an interval, preserve it exactly unless it must be rounded for cron; then report the rounding.
- If the user supplied prompt only, pick the next sensible cadence after each pass rather than forcing a fixed schedule.
- If the user supplied neither interval nor prompt, use `.loop/loop.md`.

## Automation Prompt Shape

The rendered prompt is self-contained and already produced by the helper:

```text
$loop-run
Project: <absolute path>
Cadence mode: <fixed|dynamic>
Interval: <interval or choose next sensible interval>
Schedule: <human cadence> (cron `<expr>`)   # dynamic loops omit the cron
Loop prompt:
<prompt text>

Run one pass only.
Use `.loop/loop.yaml` for project commands, safety, and state.
If a matching `.loop/specs/<slug>.md` exists, use it as extra guidance; otherwise execute the prompt directly.
Record state in `.loop/runs.jsonl`.
Report findings with verification evidence.
Pause if approval, credentials, deployment, destructive changes, or repeated failures are required.
```
