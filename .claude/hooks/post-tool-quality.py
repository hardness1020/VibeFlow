#!/usr/bin/env python3
"""
PostToolUse hook: Advisory quality checks after tool calls.

Path 1 — Write/Edit on source files: Scan content for debug patterns
  (console.log, debugger, breakpoint, etc.) and warn if found.

Path 2 — Bash with 'git push': Check branch matches active work item
  and warn if checkpoint not passed for current stage.

Input: JSON on stdin with tool_name, tool_input, tool_output
Output: Plain text advisory feedback (non-blocking)
Always exits 0 (advisory only).
"""

import json
import os
import re
import subprocess
import sys

# Source file extensions to check for debug patterns
SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".rb", ".cpp", ".c",
}

# Debug patterns to detect
DEBUG_PATTERNS = [
    (r"\bconsole\.log\b", "console.log"),
    (r"\bconsole\.debug\b", "console.debug"),
    (r"\bdebugger\b", "debugger statement"),
    (r'\bprint\s*\(\s*["\']debug', "debug print"),
    (r"\bpdb\.set_trace\(\)", "pdb.set_trace()"),
    (r"\bbreakpoint\(\)", "breakpoint()"),
    (r"\bDEBUG\s*=\s*True\b", "DEBUG = True"),
]

# Stage -> checkpoint mapping (same as checkpoint-gate.py)
STAGE_CHECKPOINT = {
    "D": 1,
    "E": 2,
    "F": 3,
    "H": 4,
    "J": 5,
    "L": 6,
}


def check_debug_patterns(file_path, content):
    """Check source file content for debug patterns."""
    _, ext = os.path.splitext(file_path)
    if ext not in SOURCE_EXTENSIONS:
        return []

    # Skip doc files
    if file_path.endswith(".md"):
        return []

    findings = []
    for pattern, label in DEBUG_PATTERNS:
        if re.search(pattern, content):
            findings.append(label)
    return findings


def check_git_push():
    """Check if branch/checkpoint status allows push."""
    warnings = []
    try:
        project_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()

        if not project_root:
            return warnings

        # Get current branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
            cwd=project_root
        ).stdout.strip()

        # Check if branch is feat/<slug>
        if not branch.startswith("feat/"):
            warnings.append(f"Pushing from '{branch}' which is not a feat/<slug> branch")
            return warnings

        slug = branch[len("feat/"):]

        # Read manifest
        manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
        if not os.path.exists(manifest_path):
            return warnings

        with open(manifest_path, "r") as f:
            content = f.read()

        # Parse manifest for this work item
        in_workitems = False
        current_slug = None
        current_stage = None
        current_checkpoint = 0

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped == "workitems:":
                in_workitems = True
                continue
            if not in_workitems:
                continue

            if line.startswith("  ") and not line.startswith("    ") and ":" in stripped:
                if current_slug == slug:
                    break
                key = stripped.split(":")[0].strip()
                if key and not key.startswith("#"):
                    current_slug = key
                    current_stage = None
                    current_checkpoint = 0
                else:
                    current_slug = None
                continue

            if current_slug and line.startswith("    ") and not line.startswith("      "):
                if stripped.startswith("stage:"):
                    current_stage = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                elif stripped.startswith("checkpoint:"):
                    try:
                        current_checkpoint = int(stripped.split(":", 1)[1].strip())
                    except ValueError:
                        current_checkpoint = 0

        if current_slug == slug and current_stage:
            if current_stage in STAGE_CHECKPOINT:
                required = STAGE_CHECKPOINT[current_stage]
                if current_checkpoint < required:
                    warnings.append(
                        f"Stage {current_stage} requires Checkpoint #{required} "
                        f"(current: #{current_checkpoint})"
                    )

    except Exception:
        pass

    return warnings


try:
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    messages = []

    # Path 1: Check Write/Edit for debug patterns
    if tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        if file_path and content:
            findings = check_debug_patterns(file_path, content)
            if findings:
                messages.append(
                    f"[VibeFlow] Debug artifacts detected in {os.path.basename(file_path)}: "
                    f"{', '.join(findings)}. Remember to remove before committing."
                )

    # Path 2: Check Bash with git push
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if "git push" in command:
            warnings = check_git_push()
            if warnings:
                messages.append(
                    "[VibeFlow] Push advisory: " + "; ".join(warnings)
                )

    if messages:
        print("\n".join(messages))

except Exception:
    # Fail open
    pass

sys.exit(0)
