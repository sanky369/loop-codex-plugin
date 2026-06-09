---
name: loop-agents
description: Generate project-scoped Codex subagents for Loop, including explorer, worker, and verifier roles that split maker from checker.
---

# Loop Agents

Use this skill when the user asks to add subagents, create maker/checker agents, improve loop verification, or make Loop safer for unattended runs.

## Goal

Create project-level Codex subagents under `.codex/agents/`:

- `loop_explorer`: read-only discovery and evidence gathering
- `loop_worker`: scoped implementation/action agent
- `loop_verifier`: read-only checker that independently verifies the goal

This implements the Loop Engineering maker/checker split: the agent that changes the project should not be the only agent judging whether the loop is done.

## Workflow

1. Read `.loop/loop.yaml`. If missing, run or recommend `$loop-init`.
2. Run:

   ```bash
   python3 <plugin-root>/scripts/loop_agents.py --root <project-root> --write
   ```

3. If `.codex/config.toml` already existed, inspect it before recommending any manual merge. Do not overwrite existing project agent settings.
4. Report the generated files and explain when to use each agent.
5. Recommend using `loop_verifier` for:
   - scheduled edit-capable automations
   - security-sensitive changes
   - PR babysitting loops
   - loops with weak automated tests
   - any loop that claims `passed`

## Safety

Do not make these agents broader than necessary. The explorer and verifier must stay read-only. The worker must stay bounded by the parent loop spec or goal.
