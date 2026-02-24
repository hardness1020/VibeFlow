#!/usr/bin/env python3
"""
Stage H (REFACTOR) Validation Script

Validates Stage H completion:
- Integration tests exist for I/O boundaries
- Stage H.4 test quality validation
- Code quality indicators

Usage:
    python validate_refactor.py [--json]

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


def find_integration_tests(project_root: Path) -> List[Path]:
    """Find integration test files."""
    integration_tests = []

    patterns = [
        "**/test_*integration*.py",
        "**/integration/*.py",
        "**/tests/integration/*.py",
        "**/test_*e2e*.py"
    ]

    for pattern in patterns:
        integration_tests.extend(project_root.glob(pattern))

    # Also check for @pytest.mark.integration in regular test files
    for test_file in project_root.glob("**/test_*.py"):
        if "__pycache__" in str(test_file):
            continue
        try:
            content = test_file.read_text()
            if "@pytest.mark.integration" in content or "pytest.mark.slow" in content:
                if test_file not in integration_tests:
                    integration_tests.append(test_file)
        except Exception:
            pass

    return list(set([f for f in integration_tests if "__pycache__" not in str(f)]))


def check_io_boundaries_tested(project_root: Path, integration_tests: List[Path]) -> Dict[str, Any]:
    """Check if I/O boundaries have integration tests."""
    result = {"valid": True, "issues": [], "warnings": [], "io_areas": {}}

    # Detect I/O areas in codebase
    io_indicators = {
        "api_endpoints": ["views.py", "routes.py", "api.py"],
        "database": ["models.py", "orm.py", "repository.py"],
        "external_apis": ["client.py", "service.py"],
        "file_operations": ["upload.py", "export.py", "pdf.py"]
    }

    for area, patterns in io_indicators.items():
        found = False
        for pattern in patterns:
            if list(project_root.glob(f"**/{pattern}")):
                found = True
                break
        result["io_areas"][area] = {"exists": found, "tested": False}

    # Check if integration tests exist
    if not integration_tests:
        for area, info in result["io_areas"].items():
            if info["exists"]:
                result["warnings"].append({
                    "message": f"No integration tests for {area.replace('_', ' ')}"
                })
    else:
        result["passed"] = len(integration_tests)

    return result


def check_test_organization(project_root: Path) -> Dict[str, Any]:
    """Check test organization quality."""
    result = {"violations": 0, "issues": [], "warnings": []}

    test_files = list(project_root.glob("**/test_*.py"))
    test_files = [f for f in test_files if "__pycache__" not in str(f)]

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()

            # Check naming pattern
            test_names = re.findall(r"def (test_\w+)", content)
            for name in test_names:
                parts = name.split("_")
                if len(parts) < 3:  # test_what_condition_expected
                    result["violations"] += 1
                    break

            # Check for docstrings
            if "def test_" in content and '"""' not in content:
                result["violations"] += 1

        except Exception:
            pass

    if result["violations"] > 5:
        result["warnings"].append({
            "message": f"{result['violations']} organization issues (naming, docstrings)"
        })

    return result


def check_test_usefulness(test_files: List[Path]) -> Dict[str, Any]:
    """Check test usefulness quality."""
    result = {"violations": 0, "issues": [], "warnings": []}

    assertions = 0
    tests = 0

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()
            test_count = len(re.findall(r"def test_\w+", content))
            assert_count = len(re.findall(r"assert|expect|should", content))

            tests += test_count
            assertions += assert_count
        except Exception:
            pass

    if tests > 0 and assertions / tests < 1:
        result["violations"] += 1
        result["warnings"].append({
            "message": "Low assertion count - tests may not be useful"
        })

    return result


def check_test_code_quality(test_files: List[Path]) -> Dict[str, Any]:
    """Check test code quality."""
    result = {"violations": 0, "major_violations": 0, "issues": [], "warnings": []}

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()

            # Major: unmocked external calls in apparent unit tests
            if "unit" in str(test_file).lower() or "@pytest.mark.unit" in content:
                external_patterns = ["requests.", "httpx.", "boto3."]
                for pattern in external_patterns:
                    if pattern in content and "mock" not in content.lower() and "patch" not in content.lower():
                        result["major_violations"] += 1
                        result["issues"].append({
                            "severity": "error",
                            "file": test_file.name,
                            "message": "Unit test may have unmocked external calls"
                        })
                        break

            # Minor: skipped tests without reason
            skipped = len(re.findall(r"@pytest\.mark\.skip(?!\(reason)", content))
            if skipped > 0:
                result["violations"] += 1

            # Minor: commented out tests
            commented = len(re.findall(r"#\s*def test_", content))
            if commented > 0:
                result["violations"] += 1

        except Exception:
            pass

    return result


def check_test_categorization(test_files: List[Path]) -> Dict[str, Any]:
    """Check test categorization."""
    result = {"violations": 0, "issues": [], "warnings": [], "uncategorized": 0}

    for test_file in test_files[:20]:
        try:
            content = test_file.read_text()
            has_marker = bool(re.search(r"@pytest\.mark\.\w+|pytestmark", content))
            if not has_marker:
                result["uncategorized"] += 1
        except Exception:
            pass

    if result["uncategorized"] > 3:
        result["violations"] += 1
        result["warnings"].append({
            "message": f"{result['uncategorized']} files lack test categorization"
        })

    return result


def calculate_quality_gate(results: Dict[str, Dict]) -> Dict[str, Any]:
    """Calculate quality gate status."""
    total_violations = 0
    major_violations = 0

    for name, check in results.items():
        total_violations += check.get("violations", 0)
        major_violations += check.get("major_violations", 0)

    if major_violations >= 2 or total_violations >= 6:
        status = "FAIL"
        valid = False
    elif major_violations == 1 or total_violations >= 3:
        status = "CONDITIONAL"
        valid = True
    else:
        status = "PASS"
        valid = True

    return {
        "status": status,
        "valid": valid,
        "total_violations": total_violations,
        "major_violations": major_violations
    }


def validate(project_root: Path, feature_id: str = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Stage H (REFACTOR)."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find test files
    test_files = list(project_root.glob("**/test_*.py"))
    test_files = [f for f in test_files if "__pycache__" not in str(f)]

    if not test_files:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "message": "No test files found"
        })
        return result

    # Find integration tests
    integration_tests = find_integration_tests(project_root)
    result["integration_test_count"] = len(integration_tests)

    # Check I/O boundaries
    io_result = check_io_boundaries_tested(project_root, integration_tests)
    result["details"]["io_boundaries"] = io_result
    result["warnings"].extend(io_result.get("warnings", []))

    # Stage H.4 Quality Validation
    quality_checks = {}

    # Organization
    org_result = check_test_organization(project_root)
    quality_checks["organization"] = org_result

    # Usefulness
    useful_result = check_test_usefulness(test_files)
    quality_checks["usefulness"] = useful_result

    # Code quality
    code_result = check_test_code_quality(test_files)
    quality_checks["code_quality"] = code_result
    result["issues"].extend(code_result.get("issues", []))

    # Categorization
    cat_result = check_test_categorization(test_files)
    quality_checks["categorization"] = cat_result

    result["details"]["quality_checks"] = quality_checks

    # Aggregate warnings
    for check in quality_checks.values():
        result["warnings"].extend(check.get("warnings", []))

    # Calculate quality gate
    gate_result = calculate_quality_gate(quality_checks)
    result["details"]["quality_gate"] = gate_result

    if not gate_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "message": f"H.4 Quality Gate {gate_result['status']}: {gate_result['total_violations']} violations"
        })
    else:
        result["passed"] += 1
        if gate_result["status"] == "CONDITIONAL":
            result["warnings"].append({
                "message": f"Quality Gate CONDITIONAL: {gate_result['total_violations']} violations"
            })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate Stage H (REFACTOR)")
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
        print(f"\nStage H (REFACTOR) Validation")
        print("=" * 50)
        print(f"Integration tests found: {result['integration_test_count']}")

        gate = result["details"].get("quality_gate", {})
        print(f"\nH.4 Quality Gate: {gate.get('status', 'UNKNOWN')}")
        print(f"  Total violations: {gate.get('total_violations', 0)}")
        print(f"  Major violations: {gate.get('major_violations', 0)}")

        if result["issues"]:
            print(f"\nIssues:")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue['message']}")

        if result["warnings"]:
            print(f"\nWarnings:")
            for warning in result["warnings"][:10]:
                print(f"  [WARN] {warning['message']}")

        status = "PASSED" if result["valid"] else "FAILED"
        print(f"\nResult: {status}")

    import sys
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
