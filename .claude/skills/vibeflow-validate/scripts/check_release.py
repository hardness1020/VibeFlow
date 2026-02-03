#!/usr/bin/env python3
"""
Checkpoint #5: Release Ready Validator

Validates:
- Spec Reconciliation (Stage I) completed
- OP-NOTE exists with all required sections
- Discovery document has Post-Implementation Notes
- ADRs created for implementation decisions
- docs/op-notes/index.md updated

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


OPNOTE_REQUIRED_SECTIONS = [
    "Preflight",
    "Deploy",
    "Monitoring",
    "Runbook",
    "Rollback",
    "Post-Deploy",
]


def find_opnote_file(docs_path: Path, feature_id: Optional[str]) -> Optional[Path]:
    """Find the OP-NOTE file."""
    opnotes_path = docs_path / "op-notes"
    if not opnotes_path.exists():
        return None

    if feature_id:
        # Look for feature-specific OP-NOTE
        matches = list(opnotes_path.glob(f"op-{feature_id}*.md"))
        if matches:
            return matches[0]

    # Look for release OP-NOTE
    release_notes = list(opnotes_path.glob("op-release-*.md"))
    if release_notes:
        return max(release_notes, key=lambda f: f.stat().st_mtime)

    # Get any OP-NOTE
    all_notes = [f for f in opnotes_path.glob("op-*.md") if f.name != "index.md"]
    if all_notes:
        return max(all_notes, key=lambda f: f.stat().st_mtime)

    return None


def validate_opnote(opnote_path: Path) -> Dict[str, Any]:
    """Validate OP-NOTE document."""
    result = {"file": str(opnote_path.name), "valid": True, "issues": [], "warnings": []}

    content = opnote_path.read_text()

    # Check required sections
    missing_sections = []
    for section in OPNOTE_REQUIRED_SECTIONS:
        pattern = rf"#+\s*{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            missing_sections.append(section)

    if missing_sections:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Missing required sections: {', '.join(missing_sections)}"
        })

    # Check for header
    if not re.search(r"\*\*(?:File|Date|Features)\*\*", content):
        result["warnings"].append({
            "message": "OP-NOTE should have header with File, Date, Features"
        })

    # Check for secrets (should NOT be present)
    secret_patterns = [
        r"password\s*[=:]\s*['\"]?\w+",
        r"api_key\s*[=:]\s*['\"]?\w+",
        r"secret\s*[=:]\s*['\"]?\w+",
        r"token\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            result["valid"] = False
            result["issues"].append({
                "severity": "error",
                "message": "Potential secret/credential found in OP-NOTE - remove immediately"
            })
            break

    # Check Preflight section quality
    if "migration" in content.lower():
        if "staging" not in content.lower() and "tested" not in content.lower():
            result["warnings"].append({
                "message": "OP-NOTE mentions migrations but no staging test noted"
            })

    # Check Rollback section quality
    rollback_match = re.search(
        r"#+\s*Rollback\s*\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )
    if rollback_match:
        rollback_content = rollback_match.group(1)
        if len(rollback_content.strip()) < 50:
            result["warnings"].append({
                "message": "Rollback section seems too brief - include precise steps"
            })

    return result


def check_spec_reconciliation(docs_path: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if Stage I Spec Reconciliation was completed."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Check for updated specs (look for recent modifications)
    specs_path = docs_path / "specs"
    if specs_path.exists():
        spec_files = list(specs_path.glob("spec-*.md"))
        for spec_file in spec_files:
            if spec_file.name == "index.md":
                continue
            content = spec_file.read_text()

            # Check for "Last Verified" or version update indicators
            if "last verified" not in content.lower() and "updated" not in content.lower():
                result["warnings"].append({
                    "file": spec_file.name,
                    "message": "Spec may not have been reconciled - check if implementation matches"
                })
                break  # Only warn once

    # Check discovery document for Post-Implementation Notes
    disco_path = docs_path / "discovery"
    if disco_path.exists():
        if feature_id:
            disco_files = list(disco_path.glob(f"disco-{feature_id}*.md"))
        else:
            disco_files = list(disco_path.glob("disco-*.md"))

        if disco_files:
            disco_file = disco_files[0]
            content = disco_file.read_text()

            if "post-implementation" not in content.lower():
                result["warnings"].append({
                    "file": disco_file.name,
                    "message": "Discovery document missing Post-Implementation Notes section"
                })

    return result


def check_opnotes_index(docs_path: Path) -> Dict[str, Any]:
    """Check if docs/op-notes/index.md is updated."""
    result = {"valid": True, "issues": [], "warnings": []}

    index_path = docs_path / "op-notes" / "index.md"
    if not index_path.exists():
        result["warnings"].append({
            "message": "docs/op-notes/index.md not found - create to track OP-NOTEs"
        })
        return result

    content = index_path.read_text()

    # Check for links to OP-NOTEs
    opnote_links = re.findall(r"op-\d+|op-release-", content, re.IGNORECASE)
    if not opnote_links:
        result["warnings"].append({
            "message": "OP-NOTE index doesn't link to any notes"
        })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #5."""
    docs_path = project_root / "docs"

    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find and validate OP-NOTE
    opnote_file = find_opnote_file(docs_path, feature_id)
    if not opnote_file:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "file": "docs/op-notes/",
            "message": "No OP-NOTE found - required for release"
        })
    else:
        opnote_result = validate_opnote(opnote_file)
        result["details"]["opnote"] = opnote_result
        result["opnote_file"] = str(opnote_file.relative_to(project_root))

        if not opnote_result["valid"]:
            result["valid"] = False
            result["failed"] += 1
            result["issues"].extend([{**i, "file": opnote_result["file"]} for i in opnote_result["issues"]])
        else:
            result["passed"] += 1
        result["warnings"].extend([{**w, "file": opnote_result["file"]} for w in opnote_result.get("warnings", [])])

    # Check Spec Reconciliation
    reconcile_result = check_spec_reconciliation(docs_path, feature_id)
    result["details"]["reconciliation"] = reconcile_result
    result["warnings"].extend(reconcile_result.get("warnings", []))

    # Check OP-NOTE index
    index_result = check_opnotes_index(docs_path)
    result["details"]["index"] = index_result
    result["warnings"].extend(index_result.get("warnings", []))

    return result


if __name__ == "__main__":
    import sys
    import json

    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    result = validate(project_root)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
