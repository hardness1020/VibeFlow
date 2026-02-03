#!/usr/bin/env python3
"""
Stage G (GREEN) Validation Script

Validates that implementation is ready:
- Stubs are implemented (no more NotImplementedError)
- Tests are expected to pass
- No contract change indicators without SPEC updates

Usage:
    python validate_green.py [--json]

Note: This script cannot actually run tests - that must be done manually.

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any


def check_stubs_implemented(project_root: Path) -> Dict[str, Any]:
    """Check if stubs have been implemented (NotImplementedError removed)."""
    result = {"valid": True, "issues": [], "warnings": [], "unimplemented": []}

    for py_file in project_root.glob("**/*.py"):
        if "__pycache__" in str(py_file) or "test" in py_file.name.lower():
            continue
        try:
            content = py_file.read_text()
            # Find remaining NotImplementedError
            matches = re.findall(r"raise NotImplementedError.*", content)
            if matches:
                result["unimplemented"].append({
                    "file": str(py_file.relative_to(project_root)),
                    "count": len(matches)
                })
        except Exception:
            pass

    if result["unimplemented"]:
        result["warnings"].append({
            "message": f"{len(result['unimplemented'])} files still have NotImplementedError"
        })
        for item in result["unimplemented"][:3]:
            result["warnings"].append({
                "message": f"  - {item['file']}: {item['count']} stubs"
            })

    return result


def check_contract_changes(project_root: Path) -> Dict[str, Any]:
    """Check for potential contract changes that need SPEC updates."""
    result = {"valid": True, "issues": [], "warnings": []}

    docs_path = project_root / "docs"
    specs_path = docs_path / "specs"

    if not specs_path.exists():
        return result

    # Check for recent spec modifications vs code modifications
    spec_files = list(specs_path.glob("spec-*.md"))
    code_files = list(project_root.glob("**/*.py"))
    code_files = [f for f in code_files if "__pycache__" not in str(f)]

    # This is a heuristic - can't truly detect contract changes
    result["warnings"].append({
        "message": "Verify no contract changes occurred without SPEC updates"
    })

    # Check for TODO comments that might indicate pending changes
    todo_count = 0
    for py_file in code_files[:50]:
        try:
            content = py_file.read_text()
            todos = re.findall(r"#\s*TODO.*contract|#\s*TODO.*spec|#\s*FIXME.*api", content, re.IGNORECASE)
            todo_count += len(todos)
        except Exception:
            pass

    if todo_count > 0:
        result["warnings"].append({
            "message": f"Found {todo_count} TODOs mentioning contracts/specs - review for G.1"
        })

    return result


def check_tests_ready(project_root: Path) -> Dict[str, Any]:
    """Check if tests are ready to pass (basic heuristics)."""
    result = {"valid": True, "issues": [], "warnings": []}

    test_files = []
    for pattern in ["**/test_*.py", "**/tests/*.py"]:
        test_files.extend(project_root.glob(pattern))
    test_files = [f for f in set(test_files) if "__pycache__" not in str(f)]

    if not test_files:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "No test files found"
        })
        return result

    # Check for skip markers that shouldn't be there
    skip_count = 0
    for test_file in test_files[:20]:
        try:
            content = test_file.read_text()
            skips = len(re.findall(r"@pytest\.mark\.skip|@skip|\.skip\(", content))
            skip_count += skips
        except Exception:
            pass

    if skip_count > 0:
        result["warnings"].append({
            "message": f"Found {skip_count} skipped tests - ensure these are intentional"
        })

    return result


def validate(project_root: Path, feature_id: str = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Stage G (GREEN)."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Check stubs implemented
    stub_result = check_stubs_implemented(project_root)
    result["details"]["stubs"] = stub_result
    result["warnings"].extend(stub_result.get("warnings", []))

    # Check for contract changes
    contract_result = check_contract_changes(project_root)
    result["details"]["contracts"] = contract_result
    result["warnings"].extend(contract_result.get("warnings", []))

    # Check tests ready
    test_result = check_tests_ready(project_root)
    result["details"]["tests"] = test_result
    if not test_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend(test_result["issues"])
    else:
        result["passed"] += 1
    result["warnings"].extend(test_result.get("warnings", []))

    # Critical reminder
    result["warnings"].append({
        "message": "Run all unit tests to verify GREEN phase - this script cannot execute tests"
    })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate Stage G (GREEN phase)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--project-root", "-p", help="Project root directory")

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    result = validate(project_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nStage G (GREEN) Validation")
        print("=" * 50)

        if result["details"].get("stubs", {}).get("unimplemented"):
            print(f"Unimplemented stubs: {len(result['details']['stubs']['unimplemented'])}")
        else:
            print("All stubs appear implemented")

        if result["issues"]:
            print(f"\nIssues:")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue['message']}")

        if result["warnings"]:
            print(f"\nWarnings:")
            for warning in result["warnings"]:
                print(f"  [WARN] {warning['message']}")

        status = "PASSED" if result["valid"] else "FAILED"
        print(f"\nResult: {status}")

    import sys
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
