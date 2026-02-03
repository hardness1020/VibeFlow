#!/usr/bin/env python3
"""
Master checkpoint validator for VibeFlow workflow.

Orchestrates validation across all checkpoints and aggregates results.

Usage:
    python validate_checkpoint.py [checkpoint_number] [--feature-id ID] [--size-track TRACK]

Arguments:
    checkpoint_number: 1-6 (optional, auto-detects if not provided)
    --feature-id: Feature ID for context (e.g., 030)
    --size-track: micro|small|medium|large (affects required checks)

Exit codes:
    0 - All validations passed
    1 - Validation failed (blocking issues)
    2 - Warnings only (can proceed with caution)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Checkpoint definitions
CHECKPOINTS = {
    1: {"name": "Planning Complete", "after_stage": "D", "script": "check_planning.py"},
    2: {"name": "Design Complete", "after_stage": "E", "script": "check_design.py"},
    3: {"name": "Tests Complete", "after_stage": "F", "script": "check_tests.py"},
    4: {"name": "Implementation Complete", "after_stage": "H", "script": "check_implementation.py"},
    5: {"name": "Release Ready", "after_stage": "J", "script": "check_release.py"},
    6: {"name": "Deployed", "after_stage": "L", "script": "check_deployed.py"},
}


def find_project_root() -> Path:
    """Find the project root by looking for docs/ directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "docs").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def detect_current_checkpoint(project_root: Path, feature_id: Optional[str] = None) -> int:
    """
    Auto-detect which checkpoint should be validated based on existing artifacts.

    Returns the next checkpoint that needs to be passed.
    """
    docs = project_root / "docs"

    # Check for Checkpoint #6 (already deployed)
    op_notes_index = docs / "op-notes" / "index.md"
    if op_notes_index.exists():
        content = op_notes_index.read_text()
        if feature_id and f"ft-{feature_id}" in content.lower():
            # Feature appears in op-notes index, check if deployed
            return 6

    # Check for Checkpoint #5 (OP-NOTE exists)
    op_notes = docs / "op-notes"
    if op_notes.exists():
        for f in op_notes.glob("op-*.md"):
            if f.name != "index.md":
                return 5  # Has OP-NOTE, validate release ready

    # Check for Checkpoint #4 (tests should be passing)
    # This requires running tests, so we check for test files
    if feature_id:
        feature_file = docs / "features" / f"ft-{feature_id}*.md"
        if list(docs.glob(f"features/ft-{feature_id}*.md")):
            # Feature exists, check test status
            # For now, assume we should validate implementation
            return 4

    # Check for Checkpoint #3 (failing tests exist)
    # Would need to actually run tests to verify

    # Check for Checkpoint #2 (Feature spec exists)
    features = docs / "features"
    if features.exists() and list(features.glob("ft-*.md")):
        return 2

    # Check for Checkpoint #1 (Planning docs exist)
    if (docs / "prds" / "prd.md").exists():
        return 1

    # No artifacts found, start from beginning
    return 1


def run_checkpoint_validator(checkpoint: int, project_root: Path,
                              feature_id: Optional[str] = None,
                              size_track: str = "medium") -> Dict[str, Any]:
    """Run the specific checkpoint validator and return results."""
    if checkpoint not in CHECKPOINTS:
        return {
            "checkpoint": checkpoint,
            "name": "Unknown",
            "valid": False,
            "issues": [{"severity": "error", "message": f"Invalid checkpoint number: {checkpoint}"}],
            "warnings": [],
            "passed": 0,
            "failed": 1
        }

    cp_info = CHECKPOINTS[checkpoint]
    script_dir = Path(__file__).parent
    script_path = script_dir / cp_info["script"]

    # Import and run the specific validator
    # For now, return a template result - actual implementation in each script
    result = {
        "checkpoint": checkpoint,
        "name": cp_info["name"],
        "after_stage": cp_info["after_stage"],
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "project_root": str(project_root),
        "feature_id": feature_id,
        "size_track": size_track
    }

    # Try to import and run the checkpoint script
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"check_{checkpoint}", script_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'validate'):
                result = module.validate(project_root, feature_id, size_track)
                result["checkpoint"] = checkpoint
                result["name"] = cp_info["name"]
    except FileNotFoundError:
        result["warnings"].append({
            "message": f"Validator script not found: {script_path}"
        })
    except Exception as e:
        result["issues"].append({
            "severity": "error",
            "message": f"Error running validator: {str(e)}"
        })
        result["valid"] = False
        result["failed"] = 1

    # Calculate summary
    result["summary"] = generate_summary(result)

    return result


def generate_summary(result: Dict[str, Any]) -> str:
    """Generate a human-readable summary of validation results."""
    checkpoint = result.get("checkpoint", "?")
    name = result.get("name", "Unknown")
    valid = result.get("valid", False)
    issues = result.get("issues", [])
    warnings = result.get("warnings", [])
    passed = result.get("passed", 0)
    failed = result.get("failed", 0)

    error_count = len([i for i in issues if i.get("severity") == "error"])
    warning_count = len(warnings)

    if valid and not issues:
        return f"Checkpoint #{checkpoint} PASSED: {passed} checks passed"
    elif not issues and warnings:
        return f"Checkpoint #{checkpoint} PASSED with warnings: {warning_count} warnings"
    else:
        return f"Checkpoint #{checkpoint} NOT PASSED: {error_count} errors, {warning_count} warnings"


def main():
    parser = argparse.ArgumentParser(description="Validate VibeFlow workflow checkpoint")
    parser.add_argument("checkpoint", type=int, nargs="?", help="Checkpoint number (1-6)")
    parser.add_argument("--feature-id", "-f", help="Feature ID (e.g., 030)")
    parser.add_argument("--size-track", "-s", choices=["micro", "small", "medium", "large"],
                        default="medium", help="Size track for the change")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--project-root", "-p", help="Project root directory")

    args = parser.parse_args()

    # Find project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = find_project_root()

    # Auto-detect checkpoint if not provided
    checkpoint = args.checkpoint
    if checkpoint is None:
        checkpoint = detect_current_checkpoint(project_root, args.feature_id)
        if not args.json:
            print(f"Auto-detected checkpoint: #{checkpoint} ({CHECKPOINTS[checkpoint]['name']})")

    # Run validation
    result = run_checkpoint_validator(
        checkpoint,
        project_root,
        args.feature_id,
        args.size_track
    )

    # Output results
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"Checkpoint #{checkpoint}: {result['name']}")
        print(f"{'='*60}")

        if result["issues"]:
            print(f"\nIssues ({len(result['issues'])}):")
            for issue in result["issues"]:
                severity = issue.get("severity", "error").upper()
                file_info = f" [{issue.get('file', '')}]" if issue.get("file") else ""
                print(f"  [{severity}]{file_info} {issue.get('message', '')}")

        if result["warnings"]:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                file_info = f" [{warning.get('file', '')}]" if warning.get("file") else ""
                print(f"  [WARN]{file_info} {warning.get('message', '')}")

        print(f"\n{result['summary']}")

    # Exit code
    if not result["valid"]:
        sys.exit(1)
    elif result["warnings"]:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
