#!/usr/bin/env python3
"""
PreToolUse hook: Advisory guard for git push commands.

Fires before Bash tool calls. Only activates when command contains 'git push'.
Checks current branch is valid feat/<slug> for active work item and warns if
checkpoint not passed for current stage.

Always allows (exit 0) — advisory only via reason field.

Input: JSON on stdin with tool_name, tool_input
Output: JSON on stdout with decision (always "allow") and optional reason
"""

import json
import os
import subprocess
import sys

# Stage -> checkpoint mapping (same as checkpoint-gate.py)
STAGE_CHECKPOINT = {
    "D": 1,
    "E": 2,
    "F": 3,
    "H": 4,
    "J": 5,
    "L": 6,
}

try:
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check Bash calls with git push
    if tool_name != "Bash" or "git push" not in tool_input.get("command", ""):
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    warnings = []

    # Find project root
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Get current branch
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    ).stdout.strip()

    if not branch.startswith("feat/"):
        warnings.append(f"Pushing from '{branch}' — not a feat/<slug> work item branch")
    else:
        slug = branch[len("feat/"):]

        # Read manifest
        manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                content = f.read()

            # Parse manifest for this slug
            in_workitems = False
            current_slug = None
            current_stage = None
            current_checkpoint = 0
            found = False

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
                        found = True
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

            if current_slug == slug:
                found = True

            if not found:
                warnings.append(f"Branch '{branch}' does not match any active work item")
            elif current_stage and current_stage in STAGE_CHECKPOINT:
                required = STAGE_CHECKPOINT[current_stage]
                if current_checkpoint < required:
                    warnings.append(
                        f"Stage {current_stage} requires Checkpoint #{required} "
                        f"before push (current: #{current_checkpoint})"
                    )

    if warnings:
        print(json.dumps({
            "decision": "allow",
            "reason": "[VibeFlow] Advisory: " + "; ".join(warnings)
        }))
    else:
        print(json.dumps({"decision": "allow"}))

except Exception:
    # Fail open
    print(json.dumps({"decision": "allow"}))

sys.exit(0)
