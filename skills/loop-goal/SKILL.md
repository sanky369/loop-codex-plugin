---
name: loop-goal
description: Create a /goal-style Loop completion contract with a verifiable done condition, required evidence, and maker/checker stop rules.
---

# Loop Goal

Use this skill when the user asks for a done condition, goal, stop condition, success criteria, run-until-done contract, or stronger verification for a loop.

## Goal

Create a goal contract under `.loop/goals/<slug>.md`. This is the Loop equivalent of a `/goal`: it says what must become true before the loop can mark itself done.

## Workflow

1. Read `.loop/loop.yaml`. If missing, run or recommend `$loop-init`.
2. Identify the goal:
   - outcome that must become true
   - commands or inspections that prove it
   - what requires human review
3. Run:

   ```bash
   python3 <plugin-root>/scripts/loop_goal.py --root <project-root> --title "<goal title>" --condition "<done condition>" --check "<command or evidence>" --write
   ```

   Repeat `--check` for each required command or evidence item.
4. Link the created goal from the relevant `.loop/specs/<slug>.md` if one exists.
5. Tell the user whether the goal is automation-safe or human-review-only.

## Good Goal Examples

- "All tests in `tests/auth` pass and lint is clean."
- "The deploy status is healthy, the latest commit matches the expected SHA, and no error spike appears in logs."
- "README setup instructions match the package manager and the documented commands work on a clean install."

## Bad Goal Examples

- "Make it better."
- "Fix all bugs."
- "Improve quality."

Push back on vague goals. A Loop goal must be checkable.
