#!/usr/bin/env python3
"""
UserPromptSubmit hook: Block prompts unless current git branch matches an active work item.

Enforces:
- No work on main/master branch (must register a work item first)
- No work on branches that don't match an active work item's feat/<slug>
- Allows manage-work/register commands on main (so users can create work items)
- Allows when no manifest exists (initial project setup)

Fails open: on any error, allows the action (never blocks due to script bugs).

Input: JSON on stdin with user_prompt
Output: JSON on stdout with decision (allow/block) and reason
"""

import json
import os
import subprocess
import sys

try:
    # Parse hook input
    hook_input = json.loads(sys.stdin.read())
    user_prompt = hook_input.get("user_prompt", "").lower()

    # Allow manage-work commands on any branch (needed to register/manage work items)
    workitem_keywords = ["manage-work", "register", "clarify-demand"]
    if any(kw in user_prompt for kw in workitem_keywords):
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Find project root
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        # Not in a git repo — allow
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Get current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    )
    current_branch = result.stdout.strip()

    # Check manifest
    manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
    if not os.path.exists(manifest_path):
        # No manifest yet — allow (user may be setting up the project)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Parse manifest (simple YAML parsing without external deps)
    with open(manifest_path, "r") as f:
        manifest_content = f.read()

    # Extract active work items from manifest
    active_branches = set()
    in_workitems = False
    current_slug = None
    current_stage = None
    current_branch_field = None
    current_has_branch = False

    for line in manifest_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == "workitems:":
            in_workitems = True
            continue
        if not in_workitems:
            continue

        # Detect work item key (top-level under workitems, 2-space indent)
        if line.startswith("  ") and not line.startswith("    ") and ":" in stripped:
            # Save previous item
            if current_slug and current_stage != "DONE":
                branch = current_branch_field or f"feat/{current_slug}"
                active_branches.add(branch)

            key = stripped.split(":")[0].strip()
            if key and not key.startswith("#"):
                current_slug = key
                current_stage = None
                current_branch_field = None
            else:
                current_slug = None
            continue

        # Detect stage and branch fields
        if current_slug and line.startswith("    ") and not line.startswith("      "):
            if stripped.startswith("stage:"):
                current_stage = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("branch:"):
                current_branch_field = stripped.split(":", 1)[1].strip().strip('"').strip("'")

    # Handle last item
    if current_slug and current_stage != "DONE":
        branch = current_branch_field or f"feat/{current_slug}"
        active_branches.add(branch)

    if not active_branches:
        # No active work items — allow (manifest might be empty or all DONE)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Block on main/master when active work items exist
    if current_branch in ("main", "master"):
        active_list = ", ".join(sorted(active_branches))
        print(json.dumps({
            "decision": "block",
            "reason": f"[VibeFlow] Work blocked on '{current_branch}'. Switch to an active work item branch ({active_list}) or register a new one: /manage-work register \"<description>\" <ID> <track>"
        }))
        sys.exit(0)

    # Check if branch matches an active work item
    if current_branch in active_branches:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Branch doesn't match any active work item
    active_list = ", ".join(sorted(active_branches))
    print(json.dumps({
        "decision": "block",
        "reason": f"[VibeFlow] Branch '{current_branch}' does not match any active work item. Active branches: {active_list}. Switch to a work item branch or register a new one."
    }))

except Exception as e:
    # Fail open — never block due to script errors
    print(json.dumps({"decision": "allow"}))
