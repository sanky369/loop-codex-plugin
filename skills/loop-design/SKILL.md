---
name: loop-design
description: Design a closed-loop Codex workflow for a recurring project task, using .loop/loop.yaml and writing a loop spec under .loop/specs/.
---

# Loop Design

Use this skill when the user asks to design a loop, turn a recurring task into a Loop workflow, or create a project-specific agent loop.

## Goal

Create a clear loop specification under `.loop/specs/<slug>.md` that Codex can execute manually or convert into an automation.

## Workflow

1. Read `.loop/loop.yaml`. If it does not exist, run or recommend `$loop-init` first.
2. Identify the recurring task. If the user's request is vague, choose the safest useful loop from the profile's `recommended_loops`.
3. Read `<plugin-root>/assets/loop-spec-template.md`.
4. Create `.loop/specs/<slug>.md` with:
   - purpose
   - trigger
   - goal contract
   - discovery phase
   - triage rules
   - execution rules
   - maker/checker subagent plan
   - connector requirements
   - worktree/isolation policy
   - verification gates
   - reporting format
   - state updates
   - comprehension update rules
   - stop/pause conditions
   - cost/safety limits
5. If the loop lacks a verifiable done condition, create or recommend `$loop-goal`.
6. If the loop can edit code unattended, create or recommend `$loop-agents`.
7. Prefer narrow loops with strong verification over broad autonomous loops.

## Design Principles

- Closed loop first: every action must feed into verification.
- Worktree isolation for changes unless the user explicitly wants the local checkout touched.
- Maker/checker split for unattended or risky loops.
- Connectors are for real discovery and reporting; do not invent external state if the connector is unavailable.
- Human approval for destructive, deploy, billing, credential, or send actions.
- State is append-only: record what happened in `.loop/runs.jsonl`.
- Comprehension is explicit: if the loop changes behavior or project direction, add a note to `.loop/COMPREHENSION.md`.
- If a success condition cannot be verified by commands or direct inspection, mark it as requiring human review.

## Output

Summarize the loop in plain language and link the created spec.
