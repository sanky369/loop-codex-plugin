# Loop Spec Template

## Purpose

What recurring work this loop owns.

## Trigger

Manual, schedule, webhook, or project event.

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

## Triage

How the loop decides whether work is actionable.

## Execution

How the loop acts, including worktree and file boundaries.

Each scheduled firing runs one pass only:

`Prompt -> Plan -> Act -> Observe -> Verify -> Record -> Decide continue/pause`

## Verification Gates

Commands and evidence required before success can be reported.

## Reporting

What the loop reports back to the user or project system.

## State

What gets appended to `.loop/runs.jsonl`.

Include prompt, cadence, checks, evidence, next action, and pause reason when applicable.

## Stop Conditions

When to pause and ask for human input.

## Cost And Safety Limits

Cadence, token, external action, and permission limits.
