# Changelog

## Unreleased

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
