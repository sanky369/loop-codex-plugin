---
name: loop-audit
description: Audit Loop profiles, specs, and run history for weak verification, repeated failures, unsafe automation scope, and cost risks.
---

# Loop Audit

Use this skill when the user asks whether a loop is safe, useful, too broad, expensive, stuck, or worth automating.

## Goal

Review Loop's local state and return concrete findings ordered by risk.

## Workflow

1. Read `.loop/loop.yaml`.
2. List `.loop/specs/*.md`.
3. List `.loop/goals/*.md`, `.codex/agents/*.toml`, and `.loop/automations/*.md`.
4. Summarize `.loop/runs.jsonl`:

   ```bash
   python3 <plugin-root>/scripts/loop_state.py summary --root <project-root>
   ```

5. Inspect recent failed or blocked runs when available.
6. Report findings first:
   - weak or missing verification gates
   - missing `/goal`-style done conditions
   - missing maker/checker split for edit-capable scheduled loops
   - loops with vague success criteria
   - repeated failures or retry churn
   - unsafe write/deploy/send permissions
   - stale project profile assumptions
   - cost or cadence problems
   - connector assumptions that are not backed by an installed/authenticated connector
   - missing worktree isolation where parallel edits are likely
   - missing `.loop/loop.md` default prompt
   - missing `.loop/NEXT.md`, `.loop/DECISIONS.md`, or `.loop/COMPREHENSION.md`
   - automations that do more than one pass per firing
   - recurring prompts that lack pause conditions
   - comprehension debt: changes made by loops without a human-readable explanation
7. Recommend specific edits to loop specs, goals, agents, or profile.

## Review Standard

Treat this like a code review for an automation harness. The most severe issue is a loop that can make changes without a verifiable definition of done and an independent verifier.
