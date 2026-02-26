#!/usr/bin/env python3
"""
UserPromptSubmit hook: Block advance/close prompts when checkpoint validation fails.

Intercepts user prompts that contain "advance" or "close" and validates that
the checkpoint gate is satisfied before allowing the manage-work skill to process them.

Fails open: on any error, allows the prompt.

Input: JSON on stdin with user_message (the user's prompt text)
Output: JSON on stdout with decision (allow/block) and reason
"""

import json
import os
import subprocess
import sys

# Stage -> checkpoint mapping (checkpoint required BEFORE advancing past this stage)
STAGE_CHECKPOINT = {
    "D": 1,  # Planning Complete
    "E": 2,  # Design Complete
    "F": 3,  # Tests Complete
    "H": 4,  # Implementation Complete
    "J": 5,  # Release Ready
    "L": 6,  # Deployed
}

try:
    hook_input = json.loads(sys.stdin.read())
    user_message = hook_input.get("user_message", "")

    # Fast-path: if prompt doesn't contain "advance" or "close", allow immediately
    message_lower = user_message.lower()
    if "advance" not in message_lower and "close" not in message_lower:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Find project root
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
    if not os.path.exists(manifest_path):
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Determine if this looks like a manage-work advance or close command
    is_advance = "advance" in message_lower
    is_close = "close" in message_lower

    # Try to extract a work item ID from the message
    # Look for patterns like "advance 030", "close add-feature", etc.
    words = user_message.split()
    work_item_id = None
    for i, word in enumerate(words):
        if word.lower() in ("advance", "close") and i + 1 < len(words):
            candidate = words[i + 1].strip('"').strip("'")
            # Skip if it looks like a flag or unrelated word
            if not candidate.startswith("-"):
                work_item_id = candidate
                break

    if not work_item_id:
        # Can't determine which work item — allow and let the skill handle it
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Read manifest to find current stage
    with open(manifest_path, "r") as f:
        content = f.read()

    in_workitems = False
    current_slug = None
    current_stage = None
    current_checkpoint = 0
    current_id = None
    matched_stage = None
    matched_checkpoint = None
    matched_slug = None

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
            # Check previous item
            if current_slug:
                if current_slug == work_item_id or str(current_id) == work_item_id:
                    matched_stage = current_stage
                    matched_checkpoint = current_checkpoint
                    matched_slug = current_slug

            key = stripped.split(":")[0].strip()
            if key and not key.startswith("#"):
                current_slug = key
                current_stage = None
                current_checkpoint = 0
                current_id = None
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
            elif stripped.startswith("id:"):
                current_id = stripped.split(":", 1)[1].strip().strip('"').strip("'")

    # Check last item
    if current_slug:
        if current_slug == work_item_id or str(current_id) == work_item_id:
            matched_stage = current_stage
            matched_checkpoint = current_checkpoint
            matched_slug = current_slug

    if not matched_stage:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # For close command: require checkpoint #4 (stage H or later)
    if is_close:
        if matched_checkpoint < 4:
            print(json.dumps({
                "decision": "block",
                "reason": f"[VibeFlow] Cannot close '{matched_slug}' — Checkpoint #4 (Implementation Complete) not passed. Current checkpoint: #{matched_checkpoint}. Complete stages through H first."
            }))
            sys.exit(0)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # For advance: check if current stage requires a checkpoint
    if is_advance and matched_stage in STAGE_CHECKPOINT:
        required_cp = STAGE_CHECKPOINT[matched_stage]
        if matched_checkpoint < required_cp:
            # Try running the validator
            validator_path = os.path.join(
                project_root, ".claude", "skills", "validate-checkpoint",
                "scripts", "validate_checkpoint.py"
            )
            if not os.path.exists(validator_path):
                hook_dir = os.path.dirname(os.path.abspath(__file__))
                validator_path = os.path.normpath(os.path.join(
                    hook_dir, "..", "skills", "validate-checkpoint",
                    "scripts", "validate_checkpoint.py"
                ))

            if os.path.exists(validator_path):
                result = subprocess.run(
                    ["python3", validator_path, str(required_cp), "--json",
                     "--project-root", project_root],
                    capture_output=True, text=True, timeout=30,
                    cwd=project_root
                )

                if result.returncode == 1:
                    # Validation failed
                    try:
                        validation_result = json.loads(result.stdout)
                        summary = validation_result.get("summary", "Validation failed")
                    except (json.JSONDecodeError, ValueError):
                        summary = "Checkpoint validation failed"

                    print(json.dumps({
                        "decision": "block",
                        "reason": f"[VibeFlow] Cannot advance '{matched_slug}' past Stage {matched_stage} — {summary}. Run '/validate-checkpoint {required_cp}' for details."
                    }))
                    sys.exit(0)

    print(json.dumps({"decision": "allow"}))

except Exception:
    # Fail open
    print(json.dumps({"decision": "allow"}))
