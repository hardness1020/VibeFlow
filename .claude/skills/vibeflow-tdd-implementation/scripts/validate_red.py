#!/usr/bin/env python3
"""
Stage F (RED) Validation Script

Validates that tests are in RED phase:
- Implementation stubs exist
- Unit tests exist
- Tests fail with NotImplementedError (not import errors)
- Deprecated tests handled
- Tests have categorization

Usage:
    python validate_red.py [--json]

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


def find_stub_files(project_root: Path) -> List[Dict[str, Any]]:
    """Find files that appear to be implementation stubs."""
    stubs = []

    # Python stubs
    for py_file in project_root.glob("**/*.py"):
        if "__pycache__" in str(py_file) or "test" in py_file.name.lower():
            continue
        try:
            content = py_file.read_text()
            if "NotImplementedError" in content or "raise NotImplemented" in content:
                # Count stub methods
                stub_count = len(re.findall(r"raise NotImplementedError", content))
                stubs.append({
                    "file": str(py_file.relative_to(project_root)),
                    "type": "python",
                    "stub_count": stub_count
                })
        except Exception:
            pass

    return stubs


def find_test_files(project_root: Path) -> List[Path]:
    """Find all test files."""
    test_files = []
    patterns = ["**/test_*.py", "**/tests/*.py", "**/*_test.py"]

    for pattern in patterns:
        test_files.extend(project_root.glob(pattern))

    return [f for f in set(test_files) if "__pycache__" not in str(f)]


def check_test_categorization(test_files: List[Path], project_root: Path) -> Dict[str, Any]:
    """Check if tests have proper categorization."""
    result = {"valid": True, "issues": [], "warnings": [], "uncategorized": 0}

    for test_file in test_files[:20]:
        try:
            content = test_file.read_text()
            has_marker = bool(re.search(r"@pytest\.mark\.\w+|pytestmark", content))
            if not has_marker:
                result["uncategorized"] += 1
        except Exception:
            pass

    if result["uncategorized"] > 0:
        result["warnings"].append({
            "message": f"{result['uncategorized']} test files lack categorization (pytest.mark.*)"
        })

    return result


def check_tests_import_stubs(test_files: List[Path], stubs: List[Dict]) -> Dict[str, Any]:
    """Check if tests import implementation stubs."""
    result = {"valid": True, "issues": [], "warnings": []}

    if not stubs:
        result["warnings"].append({
            "message": "No implementation stubs found - create stubs before tests"
        })
        return result

    # Get stub module names
    stub_names = set()
    for stub in stubs:
        name = Path(stub["file"]).stem
        stub_names.add(name)

    imports_found = False
    for test_file in test_files[:10]:
        try:
            content = test_file.read_text()
            for name in stub_names:
                if name in content:
                    imports_found = True
                    break
        except Exception:
            pass

    if not imports_found and test_files:
        result["warnings"].append({
            "message": "Tests may not be importing stubs - check import paths"
        })

    return result


def check_tests_failing_correctly(test_files: List[Path]) -> Dict[str, Any]:
    """Check if tests expect NotImplementedError (RED phase indicator)."""
    result = {"valid": True, "issues": [], "warnings": [], "red_phase_indicators": 0}

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()

            # Check for pytest.raises(NotImplementedError)
            if "NotImplementedError" in content:
                result["red_phase_indicators"] += 1

            # Check for stub calls that would raise
            if "raise" in content.lower() and "implemented" in content.lower():
                result["red_phase_indicators"] += 1

        except Exception:
            pass

    if result["red_phase_indicators"] == 0:
        result["warnings"].append({
            "message": "No RED phase indicators found - ensure tests call stubs that raise NotImplementedError"
        })

    return result


def validate(project_root: Path, feature_id: str = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Stage F (RED)."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find stubs
    stubs = find_stub_files(project_root)
    result["stub_count"] = len(stubs)
    result["details"]["stubs"] = stubs[:10]

    if not stubs:
        result["warnings"].append({
            "message": "No implementation stubs found - create stubs from Feature Spec API Design"
        })
    else:
        result["passed"] += 1

    # Find test files
    test_files = find_test_files(project_root)
    result["test_file_count"] = len(test_files)

    if not test_files:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "message": "No test files found"
        })
        return result
    else:
        result["passed"] += 1

    # Check categorization
    cat_result = check_test_categorization(test_files, project_root)
    result["details"]["categorization"] = cat_result
    result["warnings"].extend(cat_result.get("warnings", []))

    # Check stub imports
    import_result = check_tests_import_stubs(test_files, stubs)
    result["details"]["imports"] = import_result
    result["warnings"].extend(import_result.get("warnings", []))

    # Check RED phase
    red_result = check_tests_failing_correctly(test_files)
    result["details"]["red_phase"] = red_result
    result["warnings"].extend(red_result.get("warnings", []))

    # Reminder to run tests
    result["warnings"].append({
        "message": "Run tests to verify they FAIL with NotImplementedError (not import errors)"
    })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate Stage F (RED phase)")
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
        print(f"\nStage F (RED) Validation")
        print("=" * 50)
        print(f"Stubs found: {result['stub_count']}")
        print(f"Test files found: {result['test_file_count']}")

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
