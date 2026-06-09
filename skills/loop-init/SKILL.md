---
name: loop-init
description: Initialize Loop for any software project by inspecting the repo, detecting stack commands, and writing a project-specific .loop/loop.yaml profile.
---

# Loop Init

Use this skill when the user asks to set up Loop, initialize loop engineering for a repo, or make Codex understand a project's recurring workflow needs.

## Goal

Create a project-specific Loop profile at `.loop/loop.yaml`, a default bare-loop prompt at `.loop/loop.md`, and starter memory files under `.loop/`. These files are the durable contract other Loop skills read before designing, running, watching, or auditing loops.

## Workflow

1. Confirm the current working directory is the project root. If it is clearly a subdirectory, inspect upward for `.git`, package manifests, or app config and choose the most likely repo root.
2. Run the helper from this skill's plugin root:

   ```bash
   python3 <plugin-root>/scripts/project_probe.py --root <project-root> --write
   ```

3. Read the generated `.loop/loop.yaml`, `.loop/loop.md`, `.loop/NEXT.md`, `.loop/DECISIONS.md`, and `.loop/COMPREHENSION.md`.
4. If important commands are missing, inspect common project files and fill in conservative defaults.
5. Report:
   - project type and stack
   - detected check commands
   - recommended first 2-3 loops
   - any setup gaps or unsafe assumptions

## Profile Requirements

The profile should include:

- `project.root`
- `project.git`
- `project.package_managers`
- `project.frameworks`
- `commands.install`
- `commands.lint`
- `commands.test`
- `commands.build`
- `commands.dev`
- `verification.required`
- `safety.write_boundaries`
- `state.run_ledger`
- `state.default_prompt`
- `recommended_loops`
- `runtime.loop_shape`
- `primitives.automations`
- `primitives.worktrees`
- `primitives.skills`
- `primitives.connectors`
- `primitives.subagents`
- `primitives.state`

## Follow-on Setup

After initialization, recommend:

- `$loop-goal` for the first verifiable done condition.
- `$loop-agents` if the project will run edit-capable loops or unattended automations.
- `$loop-design` for the first narrow recurring workflow.

## Safety

Do not create recurring automations from this skill. This skill only creates the project profile and default loop prompt.

If the repo has uncommitted changes, note that future loop runs should prefer worktree isolation.
