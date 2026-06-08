# Changelog

## Unreleased

- Matched the Claude Code `/loop` parsing precedence: leading interval token, then a trailing `every <N> <unit>` clause (only when a real time unit follows `every`, so `check every PR` stays prompt-only), then dynamic.
- Added interval-to-cron conversion with human cadence and divisor rounding notes (e.g. `every 7m` -> `*/6 * * * *`, `every 90m` -> `0 */2 * * *`, `30s` -> 1 minute), so created automations fire on a sane schedule.
- `$loop-watch` now runs one pass immediately before scheduling (mirroring `/loop` executing now), documents the parsing rules, the durable-vs-one-off mapping, and explicit pause/stop instructions.
- Added Claude-style `$loop-watch` prompt parsing for interval-plus-prompt, prompt-only, interval-only, and default watch forms.
- Added `.loop/loop.md` default prompt generation during `$loop-init`.
- Added `prompt`, `cadence`, `next_action`, and `pause_reason` fields to the append-only run ledger.
- Added `paused` and `completed` loop statuses for scheduled loop control.

## 0.1.0 - 2026-06-08

- Initial open-source release.
- Added Loop plugin manifest.
- Added `$loop-init`, `$loop-design`, `$loop-run`, `$loop-watch`, and `$loop-audit` skills.
- Added project probing and run ledger helper scripts.
- Added loop spec, verification, and safety templates.
