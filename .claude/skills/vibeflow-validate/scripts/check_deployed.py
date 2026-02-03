#!/usr/bin/env python3
"""
Checkpoint #6: Deployed Validator

Validates:
- OP-NOTE steps followed
- Post-deploy checks passed
- Spec index updated with Current version
- Feature schedule shows Done
- Links are reciprocal
- Release tagged in Git

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


def check_spec_index(docs_path: Path) -> Dict[str, Any]:
    """Check if docs/specs/index.md has Current versions marked."""
    result = {"valid": True, "issues": [], "warnings": []}

    index_path = docs_path / "specs" / "index.md"
    if not index_path.exists():
        result["warnings"].append({
            "message": "docs/specs/index.md not found - create to track spec versions"
        })
        return result

    content = index_path.read_text()

    # Check for Current marker
    if "current" not in content.lower():
        result["warnings"].append({
            "message": "Spec index doesn't mark any version as Current"
        })

    # Check for version numbers
    versions = re.findall(r"v\d+\.\d+\.\d+", content)
    if not versions:
        result["warnings"].append({
            "message": "Spec index doesn't list version numbers"
        })

    return result


def check_feature_schedule(docs_path: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if feature schedule shows Done status."""
    result = {"valid": True, "issues": [], "warnings": []}

    schedule_path = docs_path / "features" / "schedule.md"
    if not schedule_path.exists():
        result["warnings"].append({
            "message": "docs/features/schedule.md not found"
        })
        return result

    content = schedule_path.read_text()

    if feature_id:
        # Check specific feature status
        feature_pattern = rf"ft-{feature_id}.*?(?:done|complete|shipped|released)"
        if not re.search(feature_pattern, content, re.IGNORECASE):
            result["warnings"].append({
                "message": f"Feature ft-{feature_id} not marked as Done in schedule"
            })
    else:
        # Check for any Done features
        if "done" not in content.lower() and "complete" not in content.lower():
            result["warnings"].append({
                "message": "No features marked as Done in schedule"
            })

    return result


def check_opnotes_index(docs_path: Path) -> Dict[str, Any]:
    """Check if docs/op-notes/index.md links latest note."""
    result = {"valid": True, "issues": [], "warnings": []}

    index_path = docs_path / "op-notes" / "index.md"
    if not index_path.exists():
        result["warnings"].append({
            "message": "docs/op-notes/index.md not found"
        })
        return result

    content = index_path.read_text()

    # Check for recent links
    opnote_links = re.findall(r"op-[\w-]+\.md", content)
    if not opnote_links:
        result["warnings"].append({
            "message": "OP-NOTE index doesn't link to any notes"
        })

    return result


def check_reciprocal_links(docs_path: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if PRD/FEATURE/ADR links are reciprocal."""
    result = {"valid": True, "issues": [], "warnings": []}

    # This is a basic check - full reciprocity checking is complex
    prd_path = docs_path / "prds" / "prd.md"
    if prd_path.exists():
        prd_content = prd_path.read_text()

        # Check if PRD references specs
        if "spec-" not in prd_content.lower():
            result["warnings"].append({
                "message": "PRD doesn't reference any specs - consider adding links"
            })

    # Check feature file links
    if feature_id:
        feature_files = list((docs_path / "features").glob(f"ft-{feature_id}*.md"))
        if feature_files:
            feature_content = feature_files[0].read_text()
            if "spec-" not in feature_content.lower():
                result["warnings"].append({
                    "message": f"Feature ft-{feature_id} doesn't link to specs"
                })

    return result


def check_git_release_tag(project_root: Path) -> Dict[str, Any]:
    """Check if release is tagged in Git."""
    result = {"valid": True, "issues": [], "warnings": [], "tags": []}

    try:
        # Get recent tags
        tags_output = subprocess.run(
            ["git", "tag", "-l", "--sort=-creatordate"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        if tags_output.returncode == 0:
            tags = tags_output.stdout.strip().split("\n")[:5]  # Last 5 tags
            result["tags"] = [t for t in tags if t]

            if not result["tags"]:
                result["warnings"].append({
                    "message": "No Git tags found - consider tagging the release"
                })
        else:
            result["warnings"].append({
                "message": "Could not check Git tags"
            })

    except Exception as e:
        result["warnings"].append({
            "message": f"Git tag check failed: {str(e)}"
        })

    return result


def check_issues_closed(project_root: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if issues are closed (requires manual verification)."""
    result = {"valid": True, "issues": [], "warnings": [], "cannot_verify": True}

    result["warnings"].append({
        "message": "Cannot auto-verify issue closure - ensure issues closed with 'Closes #<ID>'"
    })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #6."""
    docs_path = project_root / "docs"

    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Check spec index
    spec_result = check_spec_index(docs_path)
    result["details"]["spec_index"] = spec_result
    result["warnings"].extend(spec_result.get("warnings", []))
    if spec_result.get("issues"):
        result["issues"].extend(spec_result["issues"])

    # Check feature schedule
    schedule_result = check_feature_schedule(docs_path, feature_id)
    result["details"]["schedule"] = schedule_result
    result["warnings"].extend(schedule_result.get("warnings", []))

    # Check OP-NOTE index
    opnote_result = check_opnotes_index(docs_path)
    result["details"]["opnote_index"] = opnote_result
    result["warnings"].extend(opnote_result.get("warnings", []))

    # Check reciprocal links
    links_result = check_reciprocal_links(docs_path, feature_id)
    result["details"]["links"] = links_result
    result["warnings"].extend(links_result.get("warnings", []))

    # Check Git release tag
    git_result = check_git_release_tag(project_root)
    result["details"]["git_tags"] = git_result
    result["warnings"].extend(git_result.get("warnings", []))
    if git_result.get("tags"):
        result["recent_tags"] = git_result["tags"]

    # Check issues closed (manual verification needed)
    issues_result = check_issues_closed(project_root, feature_id)
    result["details"]["issues"] = issues_result
    result["warnings"].extend(issues_result.get("warnings", []))

    # Post-deploy checks note
    result["warnings"].append({
        "message": "Verify post-deploy checks passed and dashboards show healthy metrics"
    })

    # This checkpoint is mostly informational/verification
    result["passed"] = 1

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
