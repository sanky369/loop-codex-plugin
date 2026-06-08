# Loop Safety Policy Template

## Default Mode

Start read-only. Allow edits only after the loop has a narrow scope and verification gates.

## Always Require Human Approval

- deleting data
- deployment or rollback
- billing or payment changes
- credential, token, or secret changes
- sending external messages
- changing security policy

## Prefer Worktrees For

- code edits
- dependency updates
- generated files
- long-running automation

## Pause Conditions

- same failure repeats three times
- verification cannot run
- loop scope expands unexpectedly
- external service permissions are missing
- local checkout has unrelated user changes in affected files
