#!/usr/bin/env python3
"""
Test Coverage Check Script

Reports test coverage information and gaps.

Usage:
    python check_coverage.py [--json]

Note: This script provides guidance on coverage checking.
      Actual coverage must be run with pytest --cov or similar.

Exit codes:
    0 - Success
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any


def find_testable_modules(project_root: Path) -> Dict[str, Any]:
    """Find Python modules that should have test coverage."""
    modules = []

    # Find Python files that aren't tests or config
    exclude_patterns = [
        "test_*.py",
        "*_test.py",
        "conftest.py",
        "__init__.py",
        "settings.py",
        "config.py",
        "manage.py",
        "wsgi.py",
        "asgi.py",
    ]

    for py_file in project_root.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue
        if "migrations" in str(py_file):
            continue
        if "tests" in str(py_file) or "test" == py_file.parent.name:
            continue

        should_exclude = False
        for pattern in exclude_patterns:
            if py_file.match(pattern):
                should_exclude = True
                break

        if not should_exclude:
            modules.append(str(py_file.relative_to(project_root)))

    return {"modules": modules, "count": len(modules)}


def find_test_files(project_root: Path) -> Dict[str, Any]:
    """Find test files."""
    test_files = []

    patterns = ["**/test_*.py", "**/tests/*.py", "**/*_test.py"]
    for pattern in patterns:
        for f in project_root.glob(pattern):
            if "__pycache__" not in str(f):
                test_files.append(str(f.relative_to(project_root)))

    return {"files": list(set(test_files)), "count": len(set(test_files))}


def suggest_coverage_commands(project_root: Path) -> Dict[str, Any]:
    """Suggest commands to run coverage."""
    commands = []

    # Check for pytest
    has_pytest = (
        (project_root / "pytest.ini").exists() or
        (project_root / "pyproject.toml").exists() or
        (project_root / "setup.cfg").exists()
    )

    if has_pytest:
        commands.append({
            "name": "Run coverage with pytest",
            "command": "pytest --cov=. --cov-report=term-missing",
            "description": "Runs all tests with coverage report"
        })
        commands.append({
            "name": "Run coverage for specific module",
            "command": "pytest --cov=<module> tests/test_<module>.py",
            "description": "Coverage for specific module"
        })
        commands.append({
            "name": "Generate HTML report",
            "command": "pytest --cov=. --cov-report=html",
            "description": "Creates htmlcov/ directory with detailed report"
        })
    else:
        commands.append({
            "name": "Install pytest-cov",
            "command": "pip install pytest pytest-cov",
            "description": "Install coverage tools"
        })

    return {"commands": commands}


def estimate_coverage_gaps(project_root: Path) -> Dict[str, Any]:
    """Estimate potential coverage gaps based on file analysis."""
    gaps = []

    # Check for services without tests
    service_files = list(project_root.glob("**/services/**/*.py"))
    service_files = [f for f in service_files if "__pycache__" not in str(f) and "__init__" not in f.name]

    for service_file in service_files[:10]:
        service_name = service_file.stem
        # Look for corresponding test file
        test_patterns = [
            f"**/test_{service_name}.py",
            f"**/tests/test_{service_name}.py",
            f"**/{service_name}_test.py"
        ]

        has_test = False
        for pattern in test_patterns:
            if list(project_root.glob(pattern)):
                has_test = True
                break

        if not has_test:
            gaps.append({
                "file": str(service_file.relative_to(project_root)),
                "reason": "No corresponding test file found",
                "priority": "high"
            })

    # Check for views/routes without tests
    view_files = list(project_root.glob("**/views.py")) + list(project_root.glob("**/routes.py"))
    for view_file in view_files[:5]:
        parent = view_file.parent.name
        test_patterns = [f"**/test_{parent}*.py", f"**/tests/test_api*.py"]

        has_test = False
        for pattern in test_patterns:
            if list(project_root.glob(pattern)):
                has_test = True
                break

        if not has_test:
            gaps.append({
                "file": str(view_file.relative_to(project_root)),
                "reason": "API endpoints may lack integration tests",
                "priority": "high"
            })

    return {"gaps": gaps, "count": len(gaps)}


def validate(project_root: Path) -> Dict[str, Any]:
    """Main function to check coverage setup."""
    result = {
        "valid": True,
        "summary": {},
        "commands": [],
        "gaps": [],
        "recommendations": []
    }

    # Find testable modules
    modules = find_testable_modules(project_root)
    result["summary"]["testable_modules"] = modules["count"]

    # Find test files
    tests = find_test_files(project_root)
    result["summary"]["test_files"] = tests["count"]

    # Calculate ratio
    if modules["count"] > 0:
        ratio = tests["count"] / modules["count"]
        result["summary"]["test_to_code_ratio"] = round(ratio, 2)

        if ratio < 0.5:
            result["recommendations"].append({
                "message": f"Low test-to-code ratio ({ratio:.2f}). Target is 1.0-2.0"
            })

    # Suggest commands
    commands = suggest_coverage_commands(project_root)
    result["commands"] = commands["commands"]

    # Estimate gaps
    gaps = estimate_coverage_gaps(project_root)
    result["gaps"] = gaps["gaps"]

    if gaps["count"] > 0:
        result["recommendations"].append({
            "message": f"Found {gaps['count']} potential coverage gaps"
        })

    # Coverage targets recommendation
    result["recommendations"].append({
        "message": "Coverage targets: 80%+ for business logic, 100% for critical paths"
    })

    return result


def main():
    parser = argparse.ArgumentParser(description="Check test coverage setup")
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
        print(f"\nTest Coverage Analysis")
        print("=" * 50)

        summary = result["summary"]
        print(f"\nSummary:")
        print(f"  Testable modules: {summary.get('testable_modules', 0)}")
        print(f"  Test files: {summary.get('test_files', 0)}")
        print(f"  Test-to-code ratio: {summary.get('test_to_code_ratio', 'N/A')}")

        if result["gaps"]:
            print(f"\nPotential Coverage Gaps ({len(result['gaps'])}):")
            for gap in result["gaps"][:5]:
                print(f"  - {gap['file']}: {gap['reason']}")

        if result["commands"]:
            print(f"\nCoverage Commands:")
            for cmd in result["commands"]:
                print(f"  {cmd['name']}:")
                print(f"    $ {cmd['command']}")

        if result["recommendations"]:
            print(f"\nRecommendations:")
            for rec in result["recommendations"]:
                print(f"  - {rec['message']}")

    import sys
    sys.exit(0)


if __name__ == "__main__":
    main()
