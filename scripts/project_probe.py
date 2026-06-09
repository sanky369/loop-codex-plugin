#!/usr/bin/env python3
"""Probe a project and write a conservative Loop profile."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def exists(root: Path, *names: str) -> list[str]:
    return [name for name in names if (root / name).exists()]


def detect_package_managers(root: Path) -> list[str]:
    managers: list[str] = []
    if (root / "pnpm-lock.yaml").exists():
        managers.append("pnpm")
    if (root / "yarn.lock").exists():
        managers.append("yarn")
    if (root / "package-lock.json").exists():
        managers.append("npm")
    if (root / "uv.lock").exists():
        managers.append("uv")
    if (root / "poetry.lock").exists():
        managers.append("poetry")
    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        managers.append("python")
    if (root / "Cargo.toml").exists():
        managers.append("cargo")
    if (root / "go.mod").exists():
        managers.append("go")
    return managers


def detect_frameworks(root: Path, package_json: dict[str, Any]) -> list[str]:
    frameworks: set[str] = set()
    deps: dict[str, Any] = {}
    for key in ("dependencies", "devDependencies"):
        value = package_json.get(key)
        if isinstance(value, dict):
            deps.update(value)

    package_names = set(deps)
    markers = {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue",
        "svelte": "Svelte",
        "astro": "Astro",
        "vite": "Vite",
        "express": "Express",
        "fastify": "Fastify",
        "tailwindcss": "Tailwind CSS",
        "typescript": "TypeScript",
        "playwright": "Playwright",
        "@playwright/test": "Playwright",
        "vitest": "Vitest",
        "jest": "Jest",
    }
    for package, label in markers.items():
        if package in package_names:
            frameworks.add(label)

    if (root / "pyproject.toml").exists():
        frameworks.add("Python")
    if (root / "Cargo.toml").exists():
        frameworks.add("Rust")
    if (root / "go.mod").exists():
        frameworks.add("Go")
    if (root / "ios").exists() or list(root.glob("*.xcodeproj")):
        frameworks.add("Apple")
    return sorted(frameworks)


def script_command(manager: str, script: str) -> str:
    if manager == "pnpm":
        return f"pnpm {script}"
    if manager == "yarn":
        return f"yarn {script}"
    return f"npm run {script}"


def detect_commands(root: Path, managers: list[str], package_json: dict[str, Any]) -> dict[str, list[str]]:
    commands: dict[str, list[str]] = {
        "install": [],
        "lint": [],
        "test": [],
        "build": [],
        "dev": [],
    }

    js_manager = next((m for m in managers if m in {"pnpm", "yarn", "npm"}), None)
    if js_manager:
        if js_manager == "pnpm":
            commands["install"].append("pnpm install")
        elif js_manager == "yarn":
            commands["install"].append("yarn install")
        else:
            commands["install"].append("npm install")

        scripts = package_json.get("scripts", {})
        if isinstance(scripts, dict):
            for key in ("lint", "test", "build", "dev"):
                if key in scripts:
                    commands[key].append(script_command(js_manager, key))
            if "typecheck" in scripts:
                commands["test"].append(script_command(js_manager, "typecheck"))

    if "python" in managers or "uv" in managers or "poetry" in managers:
        if (root / "requirements.txt").exists():
            commands["install"].append("python3 -m pip install -r requirements.txt")
        if (root / "pyproject.toml").exists():
            commands["test"].append("python3 -m pytest")
        elif (root / "tests").exists():
            commands["test"].append("python3 -m unittest discover")

    if "cargo" in managers:
        commands["build"].append("cargo build")
        commands["test"].append("cargo test")
    if "go" in managers:
        commands["test"].append("go test ./...")
        commands["build"].append("go build ./...")

    return commands


def git_info(root: Path) -> dict[str, Any]:
    remote = ""
    branch = ""
    if (root / ".git").exists():
        try:
            remote = subprocess.run(
                ["git", "-C", str(root), "remote", "get-url", "origin"],
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except Exception:
            remote = ""
        try:
            branch = subprocess.run(
                ["git", "-C", str(root), "branch", "--show-current"],
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except Exception:
            branch = ""
    return {
        "enabled": (root / ".git").exists(),
        "ignore_present": (root / ".gitignore").exists(),
        "origin": remote,
        "branch": branch,
    }


def detect_connectors(root: Path) -> dict[str, Any]:
    """Detect project signals for external tools a loop may need."""
    files = exists(root, ".mcp.json", ".app.json", ".codex/config.toml", ".codex/agents")
    inferred: list[str] = []
    if (root / ".github").exists():
        inferred.append("github")
    if (root / ".github" / "workflows").exists():
        inferred.append("github-actions")
    if (root / "linear.json").exists() or (root / ".linear").exists():
        inferred.append("linear")
    if (root / "vercel.json").exists():
        inferred.append("vercel")
    if (root / "netlify.toml").exists():
        inferred.append("netlify")
    if (root / "wrangler.toml").exists():
        inferred.append("cloudflare")
    return {
        "config_files": files,
        "inferred": inferred,
        "notes": "Use connectors for discovery/reporting only when the user has installed and authenticated the relevant Codex app or MCP server.",
    }


def recommended_loops(frameworks: list[str], commands: dict[str, list[str]]) -> list[dict[str, str]]:
    loops = [
        {
            "name": "ci-triage",
            "purpose": "Discover failing checks, propose narrow fixes, and verify with the smallest relevant command.",
        },
        {
            "name": "pr-babysitter",
            "purpose": "Watch PR comments and failing checks, prepare bounded fixes in isolation, and report what needs human review.",
        },
        {
            "name": "docs-drift",
            "purpose": "Compare docs against current commands and project structure, then patch stale instructions.",
        },
    ]
    if any(item in frameworks for item in ("React", "Next.js", "Vue", "Svelte", "Astro", "Vite")):
        loops.append(
            {
                "name": "frontend-qa",
                "purpose": "Run a UI-focused implementation or bugfix pass with browser/screenshot verification.",
            }
        )
    if commands.get("test"):
        loops.append(
            {
                "name": "test-repair",
                "purpose": "Find a failing test, repair the cause, and rerun the relevant test command.",
            }
        )
    return loops[:5]


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    if not text:
        return '""'
    if any(ch in text for ch in ":#[]{}&,*?|-<>=!%@\\\"'") or text.strip() != text:
        return json.dumps(text)
    return text


def write_yaml(data: Any, indent: int = 0) -> str:
    spaces = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{spaces}{key}:")
                lines.append(write_yaml(value, indent + 2))
            else:
                lines.append(f"{spaces}{key}: {yaml_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        if not data:
            return f"{spaces}[]"
        lines = []
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{spaces}-")
                lines.append(write_yaml(item, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{spaces}-")
                lines.append(write_yaml(item, indent + 2))
            else:
                lines.append(f"{spaces}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{spaces}{yaml_scalar(data)}"


def build_profile(root: Path) -> dict[str, Any]:
    package_json = read_json(root / "package.json")
    managers = detect_package_managers(root)
    frameworks = detect_frameworks(root, package_json)
    commands = detect_commands(root, managers, package_json)
    git = git_info(root)
    connectors = detect_connectors(root)

    profile = {
        "project": {
            "root": str(root),
            "git": git,
            "package_managers": managers,
            "frameworks": frameworks,
            "important_files": exists(
                root,
                "package.json",
                "pyproject.toml",
                "requirements.txt",
                "Cargo.toml",
                "go.mod",
                "README.md",
                "AGENTS.md",
                "CLAUDE.md",
                ".codex/config.toml",
            ),
        },
        "primitives": {
            "automations": {
                "job": "discovery and triage on a schedule",
                "codex": "Codex Automations can call $loop-watch or $loop-run and report actionable runs to the user.",
            },
            "worktrees": {
                "job": "isolate parallel features and loop edits",
                "preferred": bool(git["enabled"]),
                "branch_prefix": "loop/",
            },
            "skills": {
                "job": "codify project knowledge",
                "project_profile": ".loop/loop.yaml",
                "default_prompt": ".loop/loop.md",
            },
            "connectors": connectors,
            "subagents": {
                "job": "split maker from checker",
                "project_agents_dir": ".codex/agents",
                "recommended": ["loop_explorer", "loop_worker", "loop_verifier"],
            },
            "state": {
                "job": "remember what happened outside a single conversation",
                "files": [".loop/runs.jsonl", ".loop/NEXT.md", ".loop/DECISIONS.md", ".loop/COMPREHENSION.md"],
            },
        },
        "commands": commands,
        "verification": {
            "required": [cmd for key in ("lint", "test", "build") for cmd in commands.get(key, [])],
            "notes": "Prefer the smallest relevant check first, then broaden before reporting success.",
            "goal_contract": ".loop/goals",
            "maker_checker_split": "The agent that makes a change should not be the only judge of whether the loop is done.",
        },
        "safety": {
            "default_mode": "read-only discovery before edits",
            "prefer_worktrees": bool(git["enabled"]),
            "cost_budget": {
                "default_cadence": "daily unless the user asks for faster",
                "subagents": "use verifier subagents for risky or unattended edits, not every tiny read-only pass",
            },
            "write_boundaries": [
                "Do not deploy, delete data, change billing, rotate secrets, or send external messages without explicit human approval.",
                "Keep loop edits scoped to the selected loop spec.",
            ],
        },
        "state": {
            "run_ledger": ".loop/runs.jsonl",
            "spec_dir": ".loop/specs",
            "goals_dir": ".loop/goals",
            "default_prompt": ".loop/loop.md",
            "automation_dir": ".loop/automations",
            "next_tasks": ".loop/NEXT.md",
            "decisions": ".loop/DECISIONS.md",
            "comprehension": ".loop/COMPREHENSION.md",
        },
        "runtime": {
            "loop_shape": "prompt -> plan -> act -> observe -> verify -> record -> decide continue/pause",
            "watch_forms": [
                "interval + prompt",
                "prompt only",
                "interval only",
                "bare default prompt",
            ],
            "one_pass_per_firing": True,
        },
        "recommended_loops": recommended_loops(frameworks, commands),
    }
    return profile


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe a project for Loop.")
    parser.add_argument("--root", default=os.getcwd(), help="Project root to inspect.")
    parser.add_argument("--write", action="store_true", help="Write .loop/loop.yaml.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of YAML.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    profile = build_profile(root)

    if args.write:
        loop_dir = root / ".loop"
        (loop_dir / "specs").mkdir(parents=True, exist_ok=True)
        (loop_dir / "goals").mkdir(parents=True, exist_ok=True)
        (loop_dir / "automations").mkdir(parents=True, exist_ok=True)
        default_prompt = loop_dir / "loop.md"
        if not default_prompt.exists():
            default_prompt.write_text(
                "Run one maintenance pass for this project.\n\n"
                "Read `.loop/loop.yaml`, inspect recent `.loop/runs.jsonl` entries, "
                "choose the smallest useful next action already implied by project state, "
                "prefer read-only checks first, verify any edits, record the result, and "
                "report whether to continue, pause, or wait for human input.\n\n"
                "Do not start unrelated initiatives. Do not deploy, delete, spend money, "
                "rotate secrets, send external messages, or make irreversible changes "
                "without explicit human approval.\n"
            )
        starter_files = {
            "NEXT.md": "# Loop Next\n\n- [ ] Design the first narrow loop with `$loop-design`.\n- [ ] Add a verifiable goal with `$loop-goal`.\n- [ ] Generate maker/checker agents with `$loop-agents` if loops will edit code.\n",
            "DECISIONS.md": "# Loop Decisions\n\nRecord durable loop design decisions here.\n",
            "COMPREHENSION.md": "# Loop Comprehension\n\nUse this file to summarize what loop runs changed and what the human engineer should understand before accepting the output.\n",
        }
        for name, content in starter_files.items():
            path = loop_dir / name
            if not path.exists():
                path.write_text(content)
        output = "# Generated by Loop. Edit as project knowledge improves.\n" + write_yaml(profile) + "\n"
        (loop_dir / "loop.yaml").write_text(output)

    if args.json:
        print(json.dumps(profile, indent=2))
    else:
        print(write_yaml(profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
