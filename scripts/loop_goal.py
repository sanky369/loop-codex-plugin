#!/usr/bin/env python3
"""Create /goal-style completion contracts for Loop specs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "loop-goal"


def build_goal(title: str, condition: str, checks: list[str]) -> str:
    checks_text = "\n".join(f"- `{check}`" for check in checks) if checks else "- Human review required: no automated checks were supplied."
    return f"""# {title}

## Done Condition

{condition}

## Required Evidence

{checks_text}

## Maker / Checker Split

- Maker: implement or perform the bounded action.
- Checker: independently verify the done condition and evidence.
- The loop cannot mark `passed` unless the checker can cite evidence from this run.

## Stop Conditions

- Same failure repeats three times.
- Required command or connector is unavailable.
- Scope expands beyond this goal.
- Credentials, deployment, destructive action, billing, secrets, or external sending are required.
- The human engineer needs to understand or approve the change before continuing.

## Reporting

Record the result in `.loop/runs.jsonl` and add a short comprehension note to `.loop/COMPREHENSION.md` when code, behavior, data, or public docs changed.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Loop goal contract.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--check", action="append", default=[])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    goals_dir = root / ".loop" / "goals"
    slug = slugify(args.title)
    content = build_goal(args.title, args.condition, args.check)
    path = goals_dir / f"{slug}.md"

    if args.write:
        goals_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    print(content)
    print(f"path: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
