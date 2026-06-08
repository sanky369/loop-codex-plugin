#!/usr/bin/env python3
"""Append and summarize Loop run state."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ledger_path(root: Path) -> Path:
    return root / ".loop" / "runs.jsonl"


def read_runs(root: Path) -> list[dict[str, Any]]:
    path = ledger_path(root)
    if not path.exists():
        return []
    runs: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            runs.append({"status": "invalid", "summary": line})
    return runs


def append_run(
    root: Path,
    loop: str,
    status: str,
    summary: str,
    evidence: list[str],
    prompt: str | None,
    cadence: str | None,
    next_action: str | None,
    pause_reason: str | None,
) -> None:
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "loop": loop,
        "status": status,
        "summary": summary,
        "evidence": evidence,
    }
    if prompt:
        entry["prompt"] = prompt
    if cadence:
        entry["cadence"] = cadence
    if next_action:
        entry["next_action"] = next_action
    if pause_reason:
        entry["pause_reason"] = pause_reason
    with path.open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(json.dumps(entry, indent=2))


def print_summary(root: Path) -> None:
    runs = read_runs(root)
    by_status = Counter(str(run.get("status", "unknown")) for run in runs)
    by_loop: dict[str, Counter[str]] = defaultdict(Counter)
    for run in runs:
        by_loop[str(run.get("loop", "unknown"))][str(run.get("status", "unknown"))] += 1

    print(f"ledger: {ledger_path(root)}")
    print(f"total_runs: {len(runs)}")
    print("status_counts:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print("loop_counts:")
    for loop, counts in sorted(by_loop.items()):
        joined = ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
        print(f"  {loop}: {joined}")
    if runs:
        print("recent:")
        for run in runs[-5:]:
            print(f"  - {run.get('timestamp')} {run.get('loop')} {run.get('status')}: {run.get('summary')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Loop state.")
    sub = parser.add_subparsers(dest="command", required=True)

    append = sub.add_parser("append")
    append.add_argument("--root", default=".")
    append.add_argument("--loop", required=True)
    append.add_argument("--status", required=True, choices=["passed", "failed", "noop", "blocked", "completed", "paused"])
    append.add_argument("--summary", required=True)
    append.add_argument("--evidence", action="append", default=[])
    append.add_argument("--prompt")
    append.add_argument("--cadence")
    append.add_argument("--next-action")
    append.add_argument("--pause-reason")

    summary = sub.add_parser("summary")
    summary.add_argument("--root", default=".")

    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if args.command == "append":
        append_run(
            root,
            args.loop,
            args.status,
            args.summary,
            args.evidence,
            args.prompt,
            args.cadence,
            args.next_action,
            args.pause_reason,
        )
    elif args.command == "summary":
        print_summary(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
