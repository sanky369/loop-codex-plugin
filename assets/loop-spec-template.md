# Loop Spec Template

## Purpose

What recurring work this loop owns.

## Trigger

Manual, schedule, webhook, or project event.

## Goal Contract

Link to `.loop/goals/<goal>.md`, or define the exact done condition here.

For Claude-style watch loops, specify whether this is:

- interval + prompt
- prompt only with dynamic cadence
- interval only using `.loop/loop.md`
- bare default loop using `.loop/loop.md`

## Scope

Included:

- 

Excluded:

- 

## Discovery

How the loop finds work.

Connectors required:

- 

## Triage

How the loop decides whether work is actionable.

## Execution

How the loop acts, including worktree and file boundaries.

Worktree policy:

- 

Subagent plan:

- Explorer:
- Worker:
- Verifier:

Each scheduled firing runs one pass only:

`Prompt -> Plan -> Act -> Observe -> Verify -> Record -> Decide continue/pause`

## Verification Gates

Commands and evidence required before success can be reported.

The maker cannot be the only checker. Name the independent verifier or human review path.

## Reporting

What the loop reports back to the user or project system.

## State

What gets appended to `.loop/runs.jsonl`.

Also update:

- `.loop/NEXT.md`
- `.loop/DECISIONS.md`
- `.loop/COMPREHENSION.md`

Include prompt, cadence, checks, evidence, next action, and pause reason when applicable.

## Stop Conditions

When to pause and ask for human input.

## Cost And Safety Limits

Cadence, token, external action, and permission limits.

## Comprehension Notes

What the human engineer needs to understand before accepting or continuing the loop's output.
