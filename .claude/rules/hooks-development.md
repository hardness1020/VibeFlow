---
paths:
  - ".claude/hooks/**"
---

# Hook Development Conventions

When creating or modifying hooks in `.claude/hooks/`, follow these conventions.

## Core Principles

- **Read-only:** Hooks MUST NOT mutate any file. All manifest updates happen in skills.
- **Fail-open:** On any error (missing files, parse failures, exceptions), hooks must allow the action to proceed. Never block on an error.
- **No external dependencies:** Use only Python standard library. No pip packages.

## Input/Output Format

- **Input:** JSON on stdin with fields depending on hook type:
  - `UserPromptSubmit`: `{ "prompt": "..." }`
  - `PreToolUse`: `{ "tool_name": "...", "tool_input": {...} }`
  - `Stop`: `{ "stop_hook_active": true }`
- **Output:** JSON on stdout:
  - Allow: `{ "decision": "allow" }`
  - Block: `{ "decision": "block", "reason": "..." }`

## Exit Codes

- `0` — Action allowed (with JSON output)
- `2` — Action blocked (with JSON output including reason)
- Any other code — Treated as error, action is allowed (fail-open)

## Structure

```python
#!/usr/bin/env python3
"""
<HookType> hook: <one-line description>.
Exit 0 + allow/block JSON. Fail-open on errors.
"""
import json, sys

try:
    hook_input = json.loads(sys.stdin.read())
    # ... validation logic ...
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)
except Exception:
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)
```

## Registration

Hooks are registered in `.claude/settings.json` under the appropriate event key (`UserPromptSubmit`, `PreToolUse`, `Stop`). Always use `$CLAUDE_PROJECT_DIR` for paths.
