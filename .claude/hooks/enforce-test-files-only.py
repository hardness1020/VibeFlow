#!/usr/bin/env python3
"""
PreToolUse hook: Restrict Write/Edit to test files and stubs only.
Used by test-writer agent to enforce test-only file access.

Allowed patterns:
  - test_*, *_test.*, *.test.*, *.spec.*
  - tests/ directory, stubs/ directory
  - conftest.py

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

# Patterns that identify test/stub files
TEST_PATTERNS = [
    r"(^|/)test_[^/]+$",           # test_foo.py
    r"(^|/)[^/]+_test\.[^/]+$",    # foo_test.py
    r"(^|/)[^/]+\.test\.[^/]+$",   # foo.test.ts
    r"(^|/)[^/]+\.spec\.[^/]+$",   # foo.spec.ts
    r"(^|/)tests/",                 # tests/ directory
    r"(^|/)stubs/",                 # stubs/ directory
    r"(^|/)conftest\.py$",          # conftest.py
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

    # Check if path matches any test/stub pattern
    allowed = any(re.search(p, rel_path) for p in TEST_PATTERNS)

    if allowed:
        print(json.dumps({"decision": "allow"}))
    else:
        print(json.dumps({
            "decision": "block",
            "reason": f"[VibeFlow] test-writer agent can only write to test/stub files. Blocked: {rel_path}"
        }))

except Exception:
    # Fail open
    print(json.dumps({"decision": "allow"}))

sys.exit(0)
