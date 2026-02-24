#!/usr/bin/env python3
"""
Stop hook: Non-blocking reminder if manifest needs updating.

Checks if the current work item's artifacts suggest the stage should be
advanced in the manifest. Outputs a reminder message if so.

Never blocks — always exits 0.
"""

import json
import os
import subprocess
import sys

# Stage → expected artifacts mapping
STAGE_ARTIFACTS = {
    "A": ["docs/prds/prd.md"],
    "B": ["docs/discovery/"],
    "C": ["docs/specs/"],
    "D": ["docs/adrs/"],
    "E": ["docs/features/"],
    "J": ["docs/op-notes/"],
}

try:
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        sys.exit(0)

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    ).stdout.strip()

    manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
    if not os.path.exists(manifest_path):
        sys.exit(0)

    with open(manifest_path, "r") as f:
        content = f.read()

    # Find work item matching current branch
    in_workitems = False
    current_slug = None
    current_stage = None
    current_branch_field = None
    matched_slug = None
    matched_stage = None

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
            if current_slug:
                branch = current_branch_field or f"feat/{current_slug}"
                if branch == current_branch and current_stage != "DONE":
                    matched_slug = current_slug
                    matched_stage = current_stage

            key = stripped.split(":")[0].strip()
            if key and not key.startswith("#"):
                current_slug = key
                current_stage = None
                current_branch_field = None
            else:
                current_slug = None
            continue

        if current_slug and line.startswith("    ") and not line.startswith("      "):
            if stripped.startswith("stage:"):
                current_stage = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("branch:"):
                current_branch_field = stripped.split(":", 1)[1].strip().strip('"').strip("'")

    # Check last item
    if current_slug:
        branch = current_branch_field or f"feat/{current_slug}"
        if branch == current_branch and current_stage != "DONE":
            matched_slug = current_slug
            matched_stage = current_stage

    if not matched_slug or not matched_stage:
        sys.exit(0)

    # Check if artifacts for the NEXT stage exist (suggesting advancement)
    stage_order = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    try:
        current_idx = stage_order.index(matched_stage)
    except ValueError:
        sys.exit(0)

    if current_idx + 1 >= len(stage_order):
        sys.exit(0)

    next_stage = stage_order[current_idx + 1]

    # Check if current stage artifacts exist
    if matched_stage in STAGE_ARTIFACTS:
        for artifact_pattern in STAGE_ARTIFACTS[matched_stage]:
            artifact_path = os.path.join(project_root, artifact_pattern)
            if artifact_pattern.endswith("/"):
                # Directory — check if any files exist
                if os.path.isdir(artifact_path) and os.listdir(artifact_path):
                    print(f"[VibeFlow] Reminder: '{matched_slug}' is at Stage {matched_stage} but artifacts for this stage exist. Consider advancing: /workitem advance {matched_slug}")
                    break
            else:
                if os.path.exists(artifact_path):
                    print(f"[VibeFlow] Reminder: '{matched_slug}' is at Stage {matched_stage} but artifacts for this stage exist. Consider advancing: /workitem advance {matched_slug}")
                    break

except Exception:
    pass
