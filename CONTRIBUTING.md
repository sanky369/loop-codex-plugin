# Contributing

Thanks for helping improve Loop.

## Development Checks

Before opening a pull request, run:

```bash
python3 -m py_compile scripts/project_probe.py scripts/loop_state.py
```

If you have Codex's plugin validator available, also run:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

## Design Principles

- Prefer closed loops with explicit verification.
- Keep loop specs narrow and auditable.
- Do not add automation behavior that can deploy, delete data, change billing, rotate secrets, or send messages without human approval.
- Keep persistent state simple and inspectable.
- Improve project detection conservatively.

## Pull Request Notes

Please include:

- what changed
- why it matters
- how you tested it
- any safety or permission implications
