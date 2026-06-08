#!/usr/bin/env python3
"""Parse Claude-style Loop watch input and render an automation prompt."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


INTERVAL_RE = re.compile(r"^\d+\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days)$", re.I)


BUILTIN_PROMPT = """Run one maintenance pass for this project.

Read .loop/loop.yaml and .loop/runs.jsonl. Pick the smallest useful next action
already implied by project state, loop specs, failing checks, stale docs, or the
current transcript. Prefer read-only checks first. If edits are needed, keep
them narrow and run verification gates. Record the pass in .loop/runs.jsonl.
Report evidence and whether the loop should continue, pause, or wait for human
input. Do not deploy, delete, spend money, rotate secrets, send external
messages, or make irreversible changes without explicit human approval."""


def split_interval(text: str) -> tuple[str | None, str]:
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return None, ""
    if INTERVAL_RE.match(parts[0]):
        return parts[0], parts[1] if len(parts) > 1 else ""
    return None, text.strip()


def load_default_prompt(root: Path) -> str:
    local = root / ".loop" / "loop.md"
    if local.exists():
        return local.read_text().strip()
    return BUILTIN_PROMPT


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "default"


def build(root: Path, raw: str) -> dict[str, str | bool]:
    interval, prompt = split_interval(raw)
    used_default = False
    cadence_mode = "dynamic"
    if interval:
        cadence_mode = "fixed"
    if not prompt:
        prompt = load_default_prompt(root)
        used_default = True
    title_basis = raw.strip() or "default-loop"
    if used_default and interval:
        title_basis = f"{interval} default loop"
    elif used_default:
        title_basis = "default loop"
    slug = slugify(title_basis)
    automation_prompt = f"""$loop-run
Project: {root}
Cadence mode: {cadence_mode}
Interval: {interval or "choose next sensible interval after each pass"}
Loop prompt:
{prompt}

Run one pass only.
Use `.loop/loop.yaml` for project commands, safety, and state.
If a matching `.loop/specs/<slug>.md` exists, use it as extra guidance; otherwise execute the prompt directly.
Record state in `.loop/runs.jsonl` with loop, status, prompt, cadence, checks, evidence, next action, and pause reason when relevant.
Report findings with verification evidence.
Pause instead of continuing if the same failure repeats three times, credentials are missing, the scope expands, or human approval is required.
"""
    return {
        "slug": slug,
        "interval": interval or "",
        "cadence_mode": cadence_mode,
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
