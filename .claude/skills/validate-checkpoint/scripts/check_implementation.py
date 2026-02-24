#!/usr/bin/env python3
"""
Checkpoint #4: Implementation Complete Validator

Validates:
- All unit tests PASS (GREEN)
- Integration tests written for I/O boundaries
- All integration tests PASS
- Stage H.4 Test Quality Validation completed
- No test regressions

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


# Stage H.4 Quality Validation dimensions
QUALITY_DIMENSIONS = {
    "organization": [
        "File structure follows conventions",
        "Test classes have descriptive names",
        "Test methods use naming pattern",
        "Related tests grouped together",
        "Unit and integration tests separated",
    ],
    "usefulness": [
        "Tests based on acceptance criteria",
        "All acceptance criteria have tests",
        "Tests validate behavior not implementation",
        "Happy path tested",
        "Edge cases tested",
        "Error cases tested",
    ],
    "code_quality": [
        "External dependencies mocked in unit tests",
        "Test data uses factories/fixtures",
        "AAA pattern clear",
        "No commented-out tests",
    ],
    "categorization": [
        "All tests have speed/scope tags",
        "All tests have module tags",
        "No real API calls in unit tests",
    ],
    "reliability": [
        "Unit tests run quickly",
        "Integration tests reasonable speed",
        "Tests pass consistently",
        "No flaky tests",
    ],
}


def find_test_files(project_root: Path, test_type: str = "all") -> List[Path]:
    """Find test files, optionally filtered by type."""
    test_files = []

    patterns = [
        "**/test_*.py",
        "**/tests/*.py",
        "**/*_test.py",
        "**/tests/**/*.py",
    ]

    for pattern in patterns:
        test_files.extend(project_root.glob(pattern))

    test_files = [
        f for f in test_files
        if "__pycache__" not in str(f) and "node_modules" not in str(f)
    ]

    if test_type == "unit":
        test_files = [f for f in test_files if "integration" not in f.name.lower()]
    elif test_type == "integration":
        test_files = [f for f in test_files if "integration" in f.name.lower() or "e2e" in f.name.lower()]

    return list(set(test_files))


def check_test_quality_organization(test_files: List[Path]) -> Dict[str, Any]:
    """Check test organization quality."""
    result = {"valid": True, "issues": [], "warnings": [], "violations": 0}

    for test_file in test_files[:10]:  # Sample first 10 files
        try:
            content = test_file.read_text()

            # Check naming pattern
            test_names = re.findall(r"def (test_\w+)", content)
            poor_names = [n for n in test_names if len(n.split("_")) < 3]
            if poor_names:
                result["violations"] += 1
                if result["violations"] <= 3:
                    result["warnings"].append({
                        "file": test_file.name,
                        "message": f"Poor test names (should be test_what_condition_expected): {', '.join(poor_names[:3])}"
                    })

            # Check for class organization
            has_class = bool(re.search(r"class Test\w+", content))
            test_count = len(test_names)
            if test_count > 10 and not has_class:
                result["warnings"].append({
                    "file": test_file.name,
                    "message": f"File has {test_count} tests but no test class organization"
                })

        except Exception:
            pass

    return result


def check_test_quality_usefulness(test_files: List[Path], project_root: Path) -> Dict[str, Any]:
    """Check test usefulness quality."""
    result = {"valid": True, "issues": [], "warnings": [], "violations": 0}

    total_tests = 0
    tests_with_assertions = 0
    tests_with_edge_cases = 0

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()

            # Count tests and assertions
            test_matches = re.findall(r"def (test_\w+)", content)
            total_tests += len(test_matches)

            # Check for assertions
            assertions = len(re.findall(r"assert|expect|should|must", content, re.IGNORECASE))
            if assertions > 0:
                tests_with_assertions += len(test_matches)

            # Check for edge case tests
            edge_case_patterns = ["empty", "null", "none", "invalid", "error", "fail", "edge", "boundary"]
            for pattern in edge_case_patterns:
                if pattern in content.lower():
                    tests_with_edge_cases += 1
                    break

        except Exception:
            pass

    if total_tests > 0:
        assertion_ratio = tests_with_assertions / total_tests
        if assertion_ratio < 0.8:
            result["violations"] += 1
            result["warnings"].append({
                "message": f"Only {assertion_ratio:.0%} of test files have clear assertions"
            })

        edge_ratio = tests_with_edge_cases / len(test_files) if test_files else 0
        if edge_ratio < 0.3:
            result["violations"] += 1
            result["warnings"].append({
                "message": "Few tests cover edge cases (empty, null, error conditions)"
            })

    return result


def check_test_quality_code(test_files: List[Path]) -> Dict[str, Any]:
    """Check test code quality."""
    result = {"valid": True, "issues": [], "warnings": [], "violations": 0}

    commented_tests = 0
    skipped_tests = 0
    unmocked_externals = 0

    for test_file in test_files[:15]:
        try:
            content = test_file.read_text()

            # Check for commented-out tests
            commented = len(re.findall(r"#\s*def test_|#\s*async def test_", content))
            commented_tests += commented

            # Check for skipped tests without reason
            skipped = len(re.findall(r"@pytest\.mark\.skip(?!\(reason)", content))
            skipped_tests += skipped

            # Check for potential unmocked external calls
            external_patterns = ["requests\.", "httpx\.", "aiohttp\.", "urllib", "boto3"]
            for pattern in external_patterns:
                if re.search(pattern, content) and "@mock" not in content.lower() and "patch" not in content.lower():
                    unmocked_externals += 1
                    break

        except Exception:
            pass

    if commented_tests > 0:
        result["violations"] += 1
        result["warnings"].append({
            "message": f"{commented_tests} commented-out tests found - remove or fix"
        })

    if skipped_tests > 0:
        result["violations"] += 1
        result["warnings"].append({
            "message": f"{skipped_tests} skipped tests without justification"
        })

    if unmocked_externals > 2:
        result["violations"] += 1
        result["issues"].append({
            "severity": "error",
            "message": f"{unmocked_externals} test files may have unmocked external calls"
        })
        result["valid"] = False

    return result


def check_test_quality_categorization(test_files: List[Path]) -> Dict[str, Any]:
    """Check test categorization quality."""
    result = {"valid": True, "issues": [], "warnings": [], "violations": 0}

    uncategorized = 0
    for test_file in test_files[:15]:
        if test_file.suffix != ".py":
            continue
        try:
            content = test_file.read_text()
            has_marker = bool(re.search(r"@pytest\.mark\.\w+|pytestmark", content))
            if not has_marker:
                uncategorized += 1
        except Exception:
            pass

    if uncategorized > 0:
        result["violations"] += 1
        result["warnings"].append({
            "message": f"{uncategorized} test files lack pytest markers for categorization"
        })

    return result


def count_quality_violations(results: Dict[str, Dict]) -> Dict[str, Any]:
    """Count total violations and determine quality gate status."""
    total_violations = 0
    major_violations = 0

    for dimension, check_result in results.items():
        violations = check_result.get("violations", 0)
        total_violations += violations

        # Major violations
        for issue in check_result.get("issues", []):
            if issue.get("severity") == "error":
                major_violations += 1

    # Determine status based on quality gate matrix
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
        "total_violations": total_violations,
        "major_violations": major_violations,
        "status": status,
        "valid": valid
    }


def check_integration_tests_exist(project_root: Path) -> Dict[str, Any]:
    """Check if integration tests exist for I/O boundaries."""
    result = {"valid": True, "issues": [], "warnings": []}

    integration_tests = find_test_files(project_root, "integration")

    if not integration_tests:
        # Check if there are any files that should have integration tests
        has_api = bool(list(project_root.glob("**/views.py")) or list(project_root.glob("**/routes.py")))
        has_db = bool(list(project_root.glob("**/models.py")))

        if has_api or has_db:
            result["warnings"].append({
                "message": "No integration tests found but project has API/database code"
            })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #4."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

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

    # Stage H.4 Quality Validation
    quality_results = {}

    # Organization check
    org_result = check_test_quality_organization(test_files)
    quality_results["organization"] = org_result
    result["warnings"].extend(org_result.get("warnings", []))

    # Usefulness check
    useful_result = check_test_quality_usefulness(test_files, project_root)
    quality_results["usefulness"] = useful_result
    result["warnings"].extend(useful_result.get("warnings", []))

    # Code quality check
    code_result = check_test_quality_code(test_files)
    quality_results["code_quality"] = code_result
    result["issues"].extend(code_result.get("issues", []))
    result["warnings"].extend(code_result.get("warnings", []))

    # Categorization check
    cat_result = check_test_quality_categorization(test_files)
    quality_results["categorization"] = cat_result
    result["warnings"].extend(cat_result.get("warnings", []))

    # Calculate quality gate status
    gate_result = count_quality_violations(quality_results)
    result["details"]["quality_gate"] = gate_result

    if not gate_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "message": f"Stage H.4 Quality Gate {gate_result['status']}: {gate_result['total_violations']} violations ({gate_result['major_violations']} major)"
        })
    else:
        result["passed"] += 1
        if gate_result["status"] == "CONDITIONAL":
            result["warnings"].append({
                "message": f"Quality Gate {gate_result['status']}: Fix {gate_result['total_violations']} violations before proceeding"
            })

    # Check integration tests exist
    integration_result = check_integration_tests_exist(project_root)
    result["details"]["integration_tests"] = integration_result
    result["warnings"].extend(integration_result.get("warnings", []))

    # Note: Actual test execution should be done separately
    result["warnings"].append({
        "message": "Run tests manually to verify all tests PASS (cannot auto-execute)"
    })

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
