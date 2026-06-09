#!/usr/bin/env python3
"""Generate project-scoped Codex subagents for Loop."""

from __future__ import annotations

import argparse
from pathlib import Path


AGENTS = {
    "loop-explorer.toml": '''name = "loop_explorer"
description = "Read-only Loop explorer that gathers evidence before a loop decides whether to act."
sandbox_mode = "read-only"
developer_instructions = """
Stay in discovery mode. Read .loop/loop.yaml, relevant loop specs, recent run state, and project files.
Map the actual code paths, commands, failures, tickets, or docs involved.
Return concise evidence with file paths, commands, and risk notes.
Do not edit files or propose broad rewrites unless the parent agent asks.
"""
''',
    "loop-worker.toml": '''name = "loop_worker"
description = "Loop worker that makes the smallest bounded change after discovery has identified a clear action."
developer_instructions = """
Own only the scoped action passed by the parent Loop run.
Prefer worktree isolation when the project profile recommends it.
Make the smallest defensible change, preserve unrelated user edits, and run the narrowest relevant verification first.
Record what changed and what still needs review.
Never deploy, delete data, rotate secrets, spend money, or send external messages without explicit human approval.
"""
''',
    "loop-verifier.toml": '''name = "loop_verifier"
description = "Read-only Loop verifier that checks whether the worker's output satisfies the goal and verification gates."
sandbox_mode = "read-only"
developer_instructions = """
Act as the checker, not the maker. Do not assume the implementation is correct because the worker says it is.
Read the loop goal, spec, diff, commands, and evidence. Look for correctness, regressions, missing tests, unsafe scope expansion, and unverified claims.
Lead with concrete blocking findings. If there are no blockers, state exactly which evidence supports pass/fail/noop/blocked.
"""
''',
}


CONFIG = """# Loop agent concurrency defaults.
[agents]
max_threads = 6
max_depth = 1
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Write Loop subagent TOML files.")
    parser.add_argument("--root", default=".", help="Project root.")
    parser.add_argument("--write", action="store_true", help="Write .codex/agents files.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    agents_dir = root / ".codex" / "agents"
    config_path = root / ".codex" / "config.toml"

    if args.write:
        agents_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in AGENTS.items():
            path = agents_dir / filename
            if not path.exists():
                path.write_text(content)
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(CONFIG)

    print(f"agents_dir: {agents_dir}")
    for filename in AGENTS:
        print(f"- {agents_dir / filename}")
    print(f"config: {config_path}")
    if config_path.exists():
        print("config_status: present")
    else:
        print("config_status: missing; create or merge [agents] max_threads/max_depth if you want project defaults")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
