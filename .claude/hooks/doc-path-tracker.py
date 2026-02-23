#!/usr/bin/env python3
"""
Stop hook: Warn about missing doc paths in workflow-state.yaml.

Scans git status for all changed files matching doc patterns, then checks
if the active work item's docs.* fields in docs/workflow-state.yaml are
set correctly. Prints advisory warnings for any missing or mismatched paths.

This hook is READ-ONLY — it never modifies any files.

Pattern -> field mapping:
  docs/prds/prd*.md           -> docs.prd      (scalar)
  docs/discovery/disco-*.md   -> docs.discovery (scalar)
  docs/specs/spec-*.md        -> docs.specs[]   (list)
  docs/adrs/adr-*.md          -> docs.adrs[]    (list)
  docs/features/ft-*.md       -> docs.feature   (scalar)
  docs/op-notes/op-*.md       -> docs.opnote    (scalar)

Fails open: prints warning on error, always exits 0.

Input: JSON on stdin with stop_reason (ignored)
Output: Informational warnings on stdout (never blocks)
"""

import json
import os
import re
import subprocess
import sys


# Pattern -> (field_name, is_list)
DOC_PATTERNS = [
    (r"docs/prds/prd.*\.md$",          "prd",       False),
    (r"docs/discovery/disco-.*\.md$",   "discovery", False),
    (r"docs/specs/spec-.*\.md$",        "specs",     True),
    (r"docs/adrs/adr-.*\.md$",          "adrs",      True),
    (r"docs/features/ft-.*\.md$",       "feature",   False),
    (r"docs/op-notes/op-.*\.md$",       "opnote",    False),
]


def get_project_root():
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip()


def get_current_branch(project_root):
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    )
    return result.stdout.strip()


def get_changed_files(project_root):
    """Get all changed files from git status --porcelain."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=5,
        cwd=project_root
    )
    if not result.stdout.strip():
        return []
    return [line.split()[-1] for line in result.stdout.strip().split("\n") if line.strip()]


def match_doc_pattern(rel_path):
    """Return (field_name, is_list) if path matches a doc pattern, else None."""
    normalized = rel_path.replace("\\", "/")
    for pattern, field, is_list in DOC_PATTERNS:
        if re.search(pattern, normalized):
            return field, is_list
    return None


def find_active_workitem_for_branch(lines, current_branch):
    """Find the work item slug whose branch matches current_branch.

    Returns (slug, start_line_index) or (None, None).
    """
    in_workitems = False
    current_slug = None
    current_slug_start = None
    current_stage = None
    current_branch_field = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == "workitems:":
            in_workitems = True
            continue
        if not in_workitems:
            continue

        # Detect work item key (2-space indent, not 4)
        if line.startswith("  ") and not line.startswith("    ") and ":" in stripped:
            # Check previous item
            if current_slug:
                branch = current_branch_field or f"feat/{current_slug}"
                if branch == current_branch and current_stage != "DONE":
                    return current_slug, current_slug_start

            key = stripped.split(":")[0].strip()
            if key and not key.startswith("#"):
                current_slug = key
                current_slug_start = i
                current_stage = None
                current_branch_field = None
            else:
                current_slug = None
                current_slug_start = None
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
            return current_slug, current_slug_start

    return None, None


def read_docs_fields(lines, slug_start):
    """Read the docs section for a work item and return current field values.

    Returns dict: {field_name: value} for scalar fields,
    and {field_name: [values]} for list fields.
    """
    docs_fields = {}

    # Find the 'docs:' line within this work item's block
    i = slug_start + 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Stop if we hit another work item key (2-space indent, not 4)
        if line.startswith("  ") and not line.startswith("    ") and stripped and ":" in stripped and not stripped.startswith("#"):
            break

        if line.startswith("    ") and not line.startswith("      ") and stripped == "docs:":
            i += 1
            break
        i += 1
    else:
        return docs_fields

    # Parse fields under docs: (6-space indent)
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Stop if we leave the docs block
        if not line.startswith("      ") and stripped:
            if line.startswith("    ") or (line.startswith("  ") and not line.startswith("    ")):
                break

        if line.startswith("      ") and not line.startswith("        ") and ":" in stripped:
            field_name = stripped.split(":")[0].strip()
            field_value = stripped.split(":", 1)[1].strip()

            if field_name in ("specs", "adrs"):
                # List field - collect items
                existing = []
                j = i + 1
                while j < len(lines):
                    list_line = lines[j]
                    list_stripped = list_line.strip()
                    if list_line.startswith("        - "):
                        val = list_stripped.lstrip("- ").strip().strip('"').strip("'")
                        existing.append(val)
                        j += 1
                    else:
                        break
                docs_fields[field_name] = existing
            else:
                # Scalar field
                val = field_value.strip('"').strip("'")
                docs_fields[field_name] = val

        i += 1

    return docs_fields


try:
    # Drain stdin (Stop hook sends JSON but we don't need it)
    sys.stdin.read()

    # Get project root
    project_root = get_project_root()
    if not project_root:
        sys.exit(0)

    # Discover all changed doc files via git status
    changed_files = get_changed_files(project_root)
    if not changed_files:
        sys.exit(0)

    # Match changed files against doc patterns
    doc_files = []
    for f in changed_files:
        match = match_doc_pattern(f)
        if match:
            doc_files.append((f, match[0], match[1]))

    if not doc_files:
        sys.exit(0)

    # Read manifest
    manifest_path = os.path.join(project_root, "docs", "workflow-state.yaml")
    if not os.path.exists(manifest_path):
        sys.exit(0)

    with open(manifest_path, "r") as f:
        content = f.read()

    lines = content.split("\n")

    # Find active work item for current branch
    current_branch = get_current_branch(project_root)
    if not current_branch:
        sys.exit(0)

    slug, slug_start = find_active_workitem_for_branch(lines, current_branch)
    if not slug:
        sys.exit(0)

    # Read current docs field values
    docs_fields = read_docs_fields(lines, slug_start)
    if not docs_fields:
        print(f"[VibeFlow] Warning: No docs section found for work item '{slug}'")
        sys.exit(0)

    # Check each matched doc file against manifest
    warnings = []
    for rel_path, field_name, is_list in doc_files:
        if field_name not in docs_fields:
            warnings.append(f"[VibeFlow] Warning: docs.{field_name} field not found in manifest for '{slug}' — expected '{rel_path}'")
            continue

        current_value = docs_fields[field_name]

        if is_list:
            if rel_path not in current_value:
                warnings.append(f"[VibeFlow] Warning: docs.{field_name} should contain '{rel_path}' but it is missing from manifest")
        else:
            if current_value in ("null", "", "~") or current_value != rel_path:
                warnings.append(f"[VibeFlow] Warning: docs.{field_name} should be '{rel_path}' but is '{current_value}' in manifest")

    for w in warnings:
        print(w)

except Exception as e:
    # Fail open - never block due to script errors
    print(f"[VibeFlow] Warning: doc-path-tracker error: {e}")
    sys.exit(0)
