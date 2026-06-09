# Loop Engineering Checklist

Use this before scheduling any loop.

- Automation: Does it have a cadence, one-pass boundary, and pause path?
- Worktree: Are edits isolated when parallel work or unattended changes are possible?
- Skills: Is project knowledge in `.loop/loop.yaml`, `.loop/loop.md`, or a project skill?
- Connectors: Are GitHub, Linear, CI, deploy, or messaging assumptions backed by real installed/authenticated tools?
- Subagents: Is there a maker/checker split for risky or edit-capable loops?
- State: Does the loop update `.loop/runs.jsonl` plus next/comprehension notes when relevant?
- Goal: Is the done condition verifiable?
- Cost: Is the cadence worth the token spend?
- Human judgment: Does the engineer still understand what changed?
