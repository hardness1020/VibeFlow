#!/usr/bin/env python3
"""
UserPromptSubmit hook: Inject active work items and branches into every prompt.

Reads docs/workflow-state.yaml and outputs a status line for each active work item.
Non-blocking: if anything fails, outputs nothing.

Output format:
[VibeFlow] Active: <slug> (Stage X, feat/<slug>)
"""

import json
import os
import subprocess
import sys

try:
    # Find project root
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        sys.exit(0)

    manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
    if not os.path.exists(manifest_path):
        sys.exit(0)

    # Get current branch
    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    ).stdout.strip()

    with open(manifest_path, "r") as f:
        manifest_content = f.read()

    # Parse active work items
    items = []
    in_workitems = False
    current_slug = None
    current_stage = None
    current_branch_field = None
    current_track = None

    for line in manifest_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == "workitems:":
            in_workitems = True
            continue
        if not in_workitems:
            continue

        # Detect work item key
        if line.startswith("  ") and not line.startswith("    ") and ":" in stripped:
            # Save previous item
            if current_slug and current_stage and current_stage != "DONE":
                branch = current_branch_field or f"feat/{current_slug}"
                items.append((current_slug, current_stage, branch, current_track))

            key = stripped.split(":")[0].strip()
            if key and not key.startswith("#"):
                current_slug = key
                current_stage = None
                current_branch_field = None
                current_track = None
            else:
                current_slug = None
            continue

        if current_slug and line.startswith("    ") and not line.startswith("      "):
            if stripped.startswith("stage:"):
                current_stage = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("branch:"):
                current_branch_field = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("track:"):
                current_track = stripped.split(":", 1)[1].strip().strip('"').strip("'")

    # Handle last item
    if current_slug and current_stage and current_stage != "DONE":
        branch = current_branch_field or f"feat/{current_slug}"
        items.append((current_slug, current_stage, branch, current_track))

    if not items:
        sys.exit(0)

    # Build status message
    lines = []
    for slug, stage, branch, track in items:
        marker = " <-- current" if branch == current_branch else ""
        track_info = f", {track}" if track else ""
        lines.append(f"[VibeFlow] Active: {slug} (Stage {stage}{track_info}, {branch}){marker}")

    # Output as user-prompt-submit-hook message
    print(json.dumps({"user_message": "\n".join(lines)}))

except Exception:
    # Fail silently — never disrupt the prompt
    pass
