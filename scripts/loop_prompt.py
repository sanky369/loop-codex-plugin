#!/usr/bin/env python3
"""Parse Claude-style Loop watch input and render an automation prompt.

Mirrors the Claude Code ``/loop`` parsing shape:

1. Leading interval token (``5m foo``) -> fixed cadence.
2. Trailing ``... every <N> <unit>`` clause (``foo every 20m``) -> fixed cadence,
   only when what follows ``every`` is an actual time expression.
3. Otherwise -> dynamic cadence (Codex picks the next interval after each pass).

Intervals are also converted to a cron expression and a human cadence so the
``loop-watch`` skill can create a Codex Automation that fires on schedule.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


# unit word/abbreviation -> canonical single-char unit
UNIT_TO_CHAR = {
    "s": "s", "sec": "s", "secs": "s", "second": "s", "seconds": "s",
    "m": "m", "min": "m", "mins": "m", "minute": "m", "minutes": "m",
    "h": "h", "hr": "h", "hrs": "h", "hour": "h", "hours": "h",
    "d": "d", "day": "d", "days": "d",
}

# A single token like "5m", "30s", "5min", "2hours" (number immediately followed by a unit).
SINGLE_TOKEN_RE = re.compile(r"^(\d+)\s*([a-zA-Z]+)$")
# Trailing "... every <N> <unit>" clause.
TRAILING_EVERY_RE = re.compile(r"^(.*?)\s+every\s+(\d+)\s*([a-zA-Z]+)\s*$", re.I)

# Cron-friendly divisors for even spacing.
MINUTE_DIVISORS = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30]
HOUR_DIVISORS = [1, 2, 3, 4, 6, 8, 12]


BUILTIN_PROMPT = """Run one maintenance pass for this project.

Read .loop/loop.yaml and .loop/runs.jsonl. Pick the smallest useful next action
already implied by project state, loop specs, failing checks, stale docs, or the
current transcript. Prefer read-only checks first. If edits are needed, keep
them narrow and run verification gates. Record the pass in .loop/runs.jsonl.
Report evidence and whether the loop should continue, pause, or wait for human
input. Do not deploy, delete, spend money, rotate secrets, send external
messages, or make irreversible changes without explicit human approval."""


def normalize_unit(word: str) -> str | None:
    return UNIT_TO_CHAR.get(word.lower())


def parse_token(token: str) -> tuple[int, str] | None:
    """Parse a single interval token like '5m' or '5minutes' -> (5, 'm')."""
    match = SINGLE_TOKEN_RE.match(token.strip())
    if not match:
        return None
    unit = normalize_unit(match.group(2))
    if not unit:
        return None
    return int(match.group(1)), unit


def canonical_interval(value: int, unit: str) -> str:
    return f"{value}{unit}"


def nearest(value: int, allowed: list[int]) -> int:
    return min(allowed, key=lambda candidate: (abs(candidate - value), candidate))


def human_minutes(n: int) -> str:
    return "every minute" if n == 1 else f"every {n} minutes"


def human_hours(n: int) -> str:
    return "hourly" if n == 1 else f"every {n} hours"


def human_days(n: int) -> str:
    return "daily" if n == 1 else f"every {n} days"


def to_schedule(value: int, unit: str) -> dict[str, str | None]:
    """Convert an interval into a cron expression and human cadence.

    Mirrors the Claude /loop conversion table, rounding to cron-friendly
    divisors and reporting what was rounded.
    """
    note: str | None = None

    if unit == "s":
        minutes = max(1, math.ceil(value / 60))
        note = f"cron granularity is 1 minute, so {value}s is treated as {minutes}m"
        value, unit = minutes, "m"

    if unit == "m":
        if value >= 60:
            hours = max(1, round(value / 60))
            chosen = nearest(hours, HOUR_DIVISORS)
            if chosen != value / 60:
                note = f"rounded {value}m to every {chosen}h so it divides the day evenly"
            return {"cron": f"0 */{chosen} * * *", "cadence_human": human_hours(chosen), "cron_note": note}
        chosen = nearest(value, MINUTE_DIVISORS)
        if chosen != value:
            note = f"rounded {value}m to every {chosen}m for even cron spacing"
        return {"cron": f"*/{chosen} * * * *", "cadence_human": human_minutes(chosen), "cron_note": note}

    if unit == "h":
        if value >= 24:
            days = max(1, round(value / 24))
            note = f"rounded {value}h to every {days}d"
            return {"cron": f"0 0 */{days} * *", "cadence_human": human_days(days), "cron_note": note}
        chosen = nearest(value, HOUR_DIVISORS)
        if chosen != value:
            note = f"rounded {value}h to every {chosen}h so it divides the day evenly"
        return {"cron": f"0 */{chosen} * * *", "cadence_human": human_hours(chosen), "cron_note": note}

    # days
    return {"cron": f"0 0 */{value} * *", "cadence_human": human_days(value), "cron_note": note}


def parse_request(text: str) -> dict[str, object]:
    """Return interval/unit/prompt/rule for a raw watch request."""
    stripped = text.strip()
    if not stripped:
        return {"value": None, "unit": None, "interval": "", "prompt": "", "rule": "none"}

    # Rule 1: leading interval token.
    head, _, tail = stripped.partition(" ")
    leading = parse_token(head)
    if leading:
        value, unit = leading
        return {
            "value": value,
            "unit": unit,
            "interval": canonical_interval(value, unit),
            "prompt": tail.strip(),
            "rule": "leading-interval",
        }

    # Rule 2: trailing "every <N> <unit>" clause, only if a time unit follows.
    match = TRAILING_EVERY_RE.match(stripped)
    if match:
        unit = normalize_unit(match.group(3))
        if unit:
            value = int(match.group(2))
            return {
                "value": value,
                "unit": unit,
                "interval": canonical_interval(value, unit),
                "prompt": match.group(1).strip(),
                "rule": "trailing-every",
            }

    # Rule 3: no interval -> dynamic.
    return {"value": None, "unit": None, "interval": "", "prompt": stripped, "rule": "none"}


def load_default_prompt(root: Path) -> str:
    local = root / ".loop" / "loop.md"
    if local.exists():
        return local.read_text().strip()
    return BUILTIN_PROMPT


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "default"


def build(root: Path, raw: str) -> dict[str, object]:
    parsed = parse_request(raw)
    interval = str(parsed["interval"])
    prompt = str(parsed["prompt"])
    cadence_mode = "fixed" if interval else "dynamic"

    used_default = False
    if not prompt:
        prompt = load_default_prompt(root)
        used_default = True

    schedule: dict[str, str | None] = {"cron": None, "cadence_human": None, "cron_note": None}
    if interval and parsed["value"] is not None and parsed["unit"] is not None:
        schedule = to_schedule(int(parsed["value"]), str(parsed["unit"]))

    title_basis = raw.strip() or "default-loop"
    if used_default and interval:
        title_basis = f"{interval} default loop"
    elif used_default:
        title_basis = "default loop"
    slug = slugify(title_basis)

    if cadence_mode == "fixed":
        schedule_line = f"Schedule: {schedule['cadence_human']} (cron `{schedule['cron']}`)"
        interval_line = f"Interval: {interval}"
    else:
        schedule_line = "Schedule: dynamic — choose the next sensible interval after each pass"
        interval_line = "Interval: choose next sensible interval after each pass"

    automation_prompt = f"""$loop-run
Project: {root}
Cadence mode: {cadence_mode}
{interval_line}
{schedule_line}
Loop prompt:
{prompt}

Run one pass only.
Use `.loop/loop.yaml` for project commands, safety, and state.
If a matching `.loop/specs/<slug>.md` or `.loop/goals/<slug>.md` exists, use it as extra guidance; otherwise execute the prompt directly.
For edit-capable loops, use the maker/checker split when `.codex/agents/loop-verifier.toml` exists.
Record state in `.loop/runs.jsonl` with loop, status, prompt, cadence, checks, evidence, next action, and pause reason when relevant.
Update `.loop/NEXT.md` and `.loop/COMPREHENSION.md` when the pass creates follow-up work or changes behavior, architecture, docs, or project direction.
Report findings with verification evidence.
Pause instead of continuing if the same failure repeats three times, credentials are missing, the scope expands, or human approval is required.
"""

    return {
        "slug": slug,
        "rule": parsed["rule"],
        "interval": interval,
        "cadence_mode": cadence_mode,
        "cron": schedule["cron"],
        "cadence_human": schedule["cadence_human"],
        "cron_note": schedule["cron_note"],
        "prompt": prompt,
        "used_default_prompt": used_default,
        "automation_prompt": automation_prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Loop watch input.")
    parser.add_argument("--root", default=".")
    parser.add_argument("text", nargs="*", help="Loop interval and/or prompt.")
    parser.add_argument("--write", action="store_true", help="Write .loop/automations/<slug>.md.")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    text_parts = args.text
    if text_parts and text_parts[0] == "parse":
        text_parts = text_parts[1:]
    result = build(root, " ".join(text_parts))
    if args.write:
        out_dir = root / ".loop" / "automations"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{result['slug']}.md"
        out_path.write_text(str(result["automation_prompt"]))
        result["path"] = str(out_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
