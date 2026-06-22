# Changelog

## Unreleased

## 0.2.2 - 2026-06-22

- Added a 16:9 README banner image for GitHub.
- Registered the banner as a plugin screenshot asset.
- Kept the square logo for Codex plugin metadata instead of rendering it huge in the README.

## 0.2.1 - 2026-06-09

- Added a custom Loop logo and composer icon.
- Added plugin `brandColor`, `logo`, and `composerIcon` metadata.

## 0.2.0 - 2026-06-09

- Added `$loop-agents` to generate project-scoped Codex subagents: explorer, worker, and verifier.
- Added `$loop-goal` to create `/goal`-style completion contracts under `.loop/goals/`.
- Expanded `$loop-init` to create `.loop/NEXT.md`, `.loop/DECISIONS.md`, and `.loop/COMPREHENSION.md`.
- Expanded project profiles around the five Loop Engineering primitives: automations, worktrees, skills, connectors, subagents, and state.
- Added connector signal detection for MCP, Codex config, GitHub, CI, deploy platforms, and Linear-style files.
- Added maker/checker, goal, connector, worktree, cost, and comprehension checks to loop design/run/watch/audit guidance.
- Added `loop_agents.py`, `loop_goal.py`, goal and loop-engineering checklist templates.
- Added markdown state append support to `loop_state.py`.

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
