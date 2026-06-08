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
   - discovery phase
   - triage rules
   - execution rules
   - verification gates
   - reporting format
   - state updates
   - stop/pause conditions
   - cost/safety limits
5. Prefer narrow loops with strong verification over broad autonomous loops.

## Design Principles

- Closed loop first: every action must feed into verification.
- Worktree isolation for changes unless the user explicitly wants the local checkout touched.
- Human approval for destructive, deploy, billing, credential, or send actions.
- State is append-only: record what happened in `.loop/runs.jsonl`.
- If a success condition cannot be verified by commands or direct inspection, mark it as requiring human review.

## Output

Summarize the loop in plain language and link the created spec.
