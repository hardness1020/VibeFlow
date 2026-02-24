#!/usr/bin/env python3
"""
PreToolUse hook: Restrict Write/Edit to source files only (no tests, no docs).
Used by implementer agent to enforce source-only file access.

Blocked patterns:
  - test_*, *_test.*, *.test.*, *.spec.*
  - tests/ directory, conftest.py
  - docs/ directory

Exit 0 + {"decision": "allow"} = allow
Exit 0 + {"decision": "block", "reason": "..."} = block
Fail-open on errors.

Input: JSON on stdin with tool_name, tool_input
Output: JSON on stdout with decision
"""

import json
import os
import re
import subprocess
import sys

# Patterns that identify test/doc files (blocked for implementer)
BLOCKED_PATTERNS = [
    r"(^|/)test_[^/]+$",           # test_foo.py
    r"(^|/)[^/]+_test\.[^/]+$",    # foo_test.py
    r"(^|/)[^/]+\.test\.[^/]+$",   # foo.test.ts
    r"(^|/)[^/]+\.spec\.[^/]+$",   # foo.spec.ts
    r"(^|/)tests/",                 # tests/ directory
    r"(^|/)conftest\.py$",          # conftest.py
    r"^docs/",                      # docs/ directory
]

try:
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check Write/Edit tool calls
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Resolve to project-relative path
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    abs_path = os.path.abspath(file_path)
    if abs_path.startswith(project_root):
        rel_path = os.path.relpath(abs_path, project_root).replace(os.sep, "/")
    else:
        rel_path = file_path.replace(os.sep, "/")

    # Check if path matches any blocked pattern
    blocked = any(re.search(p, rel_path) for p in BLOCKED_PATTERNS)

    if blocked:
        print(json.dumps({
            "decision": "block",
            "reason": f"[VibeFlow] implementer agent cannot write to test/doc files. Blocked: {rel_path}"
        }))
    else:
        print(json.dumps({"decision": "allow"}))

except Exception:
    # Fail open
    print(json.dumps({"decision": "allow"}))

sys.exit(0)
