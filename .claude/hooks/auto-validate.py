#!/usr/bin/env python3
"""
Stop hook: Batch-validate all changed doc files at end of turn.
Replaces per-edit PostToolUse validation with one consolidated pass.

Scans git status for changed doc files, runs the matching validation
script for each, and outputs a consolidated report. Deduplicates so
each validator runs at most once even if multiple matching files changed.

Input: JSON on stdin with stop_reason (ignored)
Output: Plain text feedback (non-blocking)
"""

import json
import os
import re
import subprocess
import sys

# Pattern → (validator script, doc type label)
DOC_PATTERNS = [
    (r"^docs/prds/prd.*\.md$", "check_planning.py", "PRD"),
    (r"^docs/discovery/disco-.*\.md$", "check_planning.py", "Discovery"),
    (r"^docs/specs/spec-.*\.md$", "check_planning.py", "Tech Spec"),
    (r"^docs/adrs/adr-.*\.md$", "check_planning.py", "ADR"),
    (r"^docs/features/ft-.*\.md$", "check_design.py", "Feature Spec"),
    (r"^docs/op-notes/op-.*\.md$", "check_release.py", "OP-NOTE"),
]

try:
    # Consume stdin (ignored)
    sys.stdin.read()

    # Find project root
    project_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip()

    if not project_root:
        sys.exit(0)

    scripts_dir = os.path.join(
        project_root, ".claude", "skills", "vibeflow-validate", "scripts"
    )

    # Collect changed files (modified + staged + untracked)
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    )
    if not result.stdout.strip():
        sys.exit(0)

    changed_files = []
    for line in result.stdout.strip().split("\n"):
        if line:
            # porcelain format: XY filename  (or XY -> renamed)
            parts = line.split()
            if parts:
                changed_files.append(parts[-1])

    # Match files to validators, deduplicating by (script, doc_type)
    validators_to_run = {}  # (script, doc_type) → True
    for filepath in changed_files:
        # Normalize to forward slashes for pattern matching
        normalized = filepath.replace(os.sep, "/")
        for pattern, script, doc_type in DOC_PATTERNS:
            if re.match(pattern, normalized):
                validators_to_run[(script, doc_type)] = True
                break

    if not validators_to_run:
        sys.exit(0)

    # Run each unique validator once and collect results
    report_lines = []
    for (script, doc_type) in sorted(validators_to_run.keys(), key=lambda x: x[1]):
        script_path = os.path.join(scripts_dir, script)
        if not os.path.isfile(script_path):
            continue

        try:
            val_result = subprocess.run(
                ["python3", script_path, "--json", "--project-root", project_root],
                capture_output=True, text=True, timeout=15,
                cwd=project_root
            )
            if not val_result.stdout.strip():
                continue

            data = json.loads(val_result.stdout)
            issues = len(data.get("issues", []))
            warnings = len(data.get("warnings", []))

            if issues == 0 and warnings == 0:
                report_lines.append(f"  {doc_type}: PASS")
            elif issues == 0:
                report_lines.append(f"  {doc_type}: PASS ({warnings} warnings)")
            else:
                report_lines.append(f"  {doc_type}: {issues} issues, {warnings} warnings")
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            continue

    if report_lines:
        print("[VibeFlow] Doc validation:")
        print("\n".join(report_lines))

except Exception:
    # Fail open — never block due to script errors
    pass

sys.exit(0)
