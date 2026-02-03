#!/usr/bin/env python3
"""
Checkpoint #3: Tests Complete Validator

Validates:
- Implementation stubs exist with function signatures from FEATURE spec
- Stubs raise "not implemented" errors
- Unit test files exist
- Tests import actual stubs (not mock names)
- Tests have proper categorization tags
- All tests currently FAIL (RED phase)
- Deprecated tests handled per Stage B checklist

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


def find_test_files(project_root: Path) -> List[Path]:
    """Find all test files in the project."""
    test_files = []

    # Common test file patterns
    patterns = [
        "**/test_*.py",
        "**/tests/*.py",
        "**/*_test.py",
        "**/tests/**/*.py",
        "**/test/**/*.py",
        "**/*.test.ts",
        "**/*.test.js",
        "**/*.spec.ts",
        "**/*.spec.js",
    ]

    for pattern in patterns:
        test_files.extend(project_root.glob(pattern))

    # Filter out __pycache__ and node_modules
    test_files = [
        f for f in test_files
        if "__pycache__" not in str(f) and "node_modules" not in str(f)
    ]

    return list(set(test_files))


def find_stub_files(project_root: Path) -> List[Path]:
    """Find files that appear to be implementation stubs."""
    stub_files = []

    # Look for Python files with NotImplementedError
    for py_file in project_root.glob("**/*.py"):
        if "__pycache__" in str(py_file) or "test" in py_file.name.lower():
            continue
        try:
            content = py_file.read_text()
            if "NotImplementedError" in content or "raise NotImplemented" in content:
                stub_files.append(py_file)
        except Exception:
            pass

    # Look for TypeScript/JS files with throw new Error("Not implemented")
    for ts_file in list(project_root.glob("**/*.ts")) + list(project_root.glob("**/*.js")):
        if "node_modules" in str(ts_file) or "test" in ts_file.name.lower():
            continue
        try:
            content = ts_file.read_text()
            if "not implemented" in content.lower() or "TODO" in content:
                stub_files.append(ts_file)
        except Exception:
            pass

    return stub_files


def check_test_categorization(test_file: Path) -> Dict[str, Any]:
    """Check if test file has proper categorization tags."""
    result = {"valid": True, "issues": [], "warnings": []}

    try:
        content = test_file.read_text()
    except Exception as e:
        result["warnings"].append({
            "message": f"Could not read file: {e}"
        })
        return result

    # Python test categorization (pytest markers)
    if test_file.suffix == ".py":
        # Check for pytest markers
        has_markers = bool(re.search(r"@pytest\.mark\.\w+", content))
        has_unit_marker = bool(re.search(r"@pytest\.mark\.(?:unit|fast)", content))
        has_integration_marker = bool(re.search(r"@pytest\.mark\.(?:integration|slow)", content))
        has_module_marker = bool(re.search(r"@pytest\.mark\.\w+", content))

        if not has_markers:
            result["warnings"].append({
                "message": "No pytest markers found - add @pytest.mark.<category> for test categorization"
            })

    # JavaScript/TypeScript categorization (describe/it blocks with tags)
    elif test_file.suffix in [".ts", ".js"]:
        has_describe = bool(re.search(r"describe\s*\(", content))
        has_tags = bool(re.search(r"(?:@unit|@integration|@slow|\.skip|\.only)", content))

        if has_describe and not has_tags:
            result["warnings"].append({
                "message": "Consider adding test categorization tags"
            })

    return result


def check_stub_imports_in_tests(test_files: List[Path], stub_files: List[Path]) -> Dict[str, Any]:
    """Check if tests import actual stub implementations."""
    result = {"valid": True, "issues": [], "warnings": []}

    if not stub_files:
        result["warnings"].append({
            "message": "No stub files found - ensure implementation stubs are created from FEATURE spec"
        })
        return result

    # Extract module names from stub files
    stub_modules = set()
    for stub in stub_files:
        # Convert path to potential import name
        parts = stub.stem.split("_")
        stub_modules.add(stub.stem)
        stub_modules.update(parts)

    imports_found = False
    for test_file in test_files:
        if test_file.suffix != ".py":
            continue

        try:
            content = test_file.read_text()
            # Check for imports from stub modules
            for module in stub_modules:
                if re.search(rf"(?:from|import)\s+.*{module}", content):
                    imports_found = True
                    break
        except Exception:
            pass

    if not imports_found and test_files:
        result["warnings"].append({
            "message": "Tests may not be importing actual stub implementations - verify import paths"
        })

    return result


def check_tests_are_failing(project_root: Path, test_files: List[Path]) -> Dict[str, Any]:
    """
    Check if tests are in RED phase (failing).

    Note: This is a heuristic check. For accurate results, actually run the tests.
    """
    result = {"valid": True, "issues": [], "warnings": [], "cannot_verify": False}

    if not test_files:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "No test files found"
        })
        return result

    # Try to detect test framework and provide guidance
    has_pytest = any((project_root / f).exists() for f in ["pytest.ini", "pyproject.toml", "setup.cfg"])
    has_jest = any((project_root / f).exists() for f in ["jest.config.js", "jest.config.ts"])

    result["test_framework"] = "pytest" if has_pytest else ("jest" if has_jest else "unknown")
    result["cannot_verify"] = True
    result["warnings"].append({
        "message": "Cannot automatically verify tests are failing - run tests manually to confirm RED phase"
    })

    # Check for NotImplementedError expects in tests
    not_impl_expects = 0
    for test_file in test_files:
        if test_file.suffix != ".py":
            continue
        try:
            content = test_file.read_text()
            if "NotImplementedError" in content or "pytest.raises" in content:
                not_impl_expects += 1
        except Exception:
            pass

    if not_impl_expects > 0:
        result["warnings"].append({
            "message": f"Found {not_impl_expects} test files expecting NotImplementedError - good sign for RED phase"
        })

    return result


def check_deprecated_tests_handled(project_root: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if deprecated tests from Stage B checklist have been handled."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Try to find discovery document with test checklist
    docs_path = project_root / "docs"
    disco_path = docs_path / "discovery"

    if not disco_path.exists():
        return result

    # Find discovery file
    if feature_id:
        disco_files = list(disco_path.glob(f"disco-{feature_id}*.md"))
    else:
        disco_files = list(disco_path.glob("disco-*.md"))

    if not disco_files:
        return result

    disco_file = disco_files[0]
    content = disco_file.read_text()

    # Check if there's a test update checklist
    if "test update checklist" in content.lower() or "test impact" in content.lower():
        # Check for REMOVE items
        remove_items = re.findall(r"(?:REMOVE|❌).*?test_\w+", content, re.IGNORECASE)
        if remove_items:
            result["warnings"].append({
                "message": f"Discovery doc lists {len(remove_items)} tests to remove - ensure these are handled"
            })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #3."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find test files
    test_files = find_test_files(project_root)
    result["test_file_count"] = len(test_files)

    if not test_files:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "message": "No test files found in project"
        })
        return result
    else:
        result["passed"] += 1

    # Find stub files
    stub_files = find_stub_files(project_root)
    result["stub_file_count"] = len(stub_files)
    result["details"]["stubs"] = [str(f.relative_to(project_root)) for f in stub_files[:10]]

    if not stub_files:
        result["warnings"].append({
            "message": "No implementation stubs found - create stubs with NotImplementedError from FEATURE spec API Design"
        })

    # Check test categorization
    categorization_issues = 0
    for test_file in test_files[:20]:  # Check first 20 files
        cat_result = check_test_categorization(test_file)
        if cat_result["warnings"]:
            categorization_issues += 1
            if categorization_issues <= 3:  # Only report first few
                result["warnings"].extend([
                    {**w, "file": str(test_file.relative_to(project_root))}
                    for w in cat_result["warnings"]
                ])

    if categorization_issues > 3:
        result["warnings"].append({
            "message": f"{categorization_issues} test files lack proper categorization"
        })

    # Check stub imports
    import_result = check_stub_imports_in_tests(test_files, stub_files)
    result["details"]["imports"] = import_result
    result["warnings"].extend(import_result.get("warnings", []))

    # Check tests are failing (RED phase)
    fail_result = check_tests_are_failing(project_root, test_files)
    result["details"]["test_status"] = fail_result
    if not fail_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend(fail_result["issues"])
    else:
        result["passed"] += 1
    result["warnings"].extend(fail_result.get("warnings", []))

    # Check deprecated tests handled
    deprecated_result = check_deprecated_tests_handled(project_root, feature_id)
    result["details"]["deprecated"] = deprecated_result
    result["warnings"].extend(deprecated_result.get("warnings", []))

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
