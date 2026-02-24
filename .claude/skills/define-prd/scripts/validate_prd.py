#!/usr/bin/env python3
"""
PRD Validation Script

Validates that a PRD file has all required sections and follows best practices.

Usage:
    python validate_prd.py [--path PATH] [--json]

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


REQUIRED_SECTIONS = [
    ("Summary", r"#+\s*Summary"),
    ("Problem & Context", r"#+\s*Problem"),
    ("Users & Use Cases", r"#+\s*Users"),
    ("Scope", r"#+\s*Scope"),
    ("Success Metrics", r"#+\s*Success\s*Metrics"),
    ("Non-Goals", r"#+\s*Non-Goals"),
    ("Requirements", r"#+\s*Requirements"),
    ("Dependencies", r"#+\s*Dependencies"),
    ("Risks", r"#+\s*Risks"),
]

RECOMMENDED_SECTIONS = [
    ("Analytics & Telemetry", r"#+\s*(?:Analytics|Telemetry)"),
]


def validate_prd(prd_path: Path) -> Dict[str, Any]:
    """Validate PRD document."""
    result = {
        "file": str(prd_path),
        "valid": True,
        "issues": [],
        "warnings": [],
        "sections_found": [],
        "sections_missing": []
    }

    if not prd_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"PRD file not found: {prd_path}"
        })
        return result

    content = prd_path.read_text()

    # Check required sections
    for section_name, pattern in REQUIRED_SECTIONS:
        if re.search(pattern, content, re.IGNORECASE):
            result["sections_found"].append(section_name)
        else:
            result["sections_missing"].append(section_name)
            result["valid"] = False
            result["issues"].append({
                "severity": "error",
                "section": section_name,
                "message": f"Missing required section: {section_name}"
            })

    # Check recommended sections
    for section_name, pattern in RECOMMENDED_SECTIONS:
        if not re.search(pattern, content, re.IGNORECASE):
            result["warnings"].append({
                "section": section_name,
                "message": f"Missing recommended section: {section_name}"
            })

    # Check header
    if not re.search(r"\*\*Version\*\*", content):
        result["warnings"].append({
            "message": "PRD should have Version in header"
        })

    if not re.search(r"\*\*(?:Owners?|Last_updated)\*\*", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "PRD should have Owners and Last_updated in header"
        })

    # Check MoSCoW in Scope
    scope_match = re.search(r"#+\s*Scope.*?\n(.*?)(?=\n#[^#]|\Z)", content, re.IGNORECASE | re.DOTALL)
    if scope_match:
        scope_content = scope_match.group(1).lower()
        moscow_keywords = ["must", "should", "could", "won't", "will not"]
        moscow_found = sum(1 for kw in moscow_keywords if kw in scope_content)
        if moscow_found < 2:
            result["warnings"].append({
                "section": "Scope",
                "message": "Scope section should use MoSCoW format (Must/Should/Could/Won't)"
            })

    # Check for implementation details (should not be in PRD)
    if re.search(r"```(?:python|javascript|typescript|java|go|rust|sql)", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "PRD contains code blocks - implementation details belong in TECH-SPEC"
        })

    # Check Success Metrics have targets
    metrics_match = re.search(r"#+\s*Success\s*Metrics.*?\n(.*?)(?=\n#[^#]|\Z)", content, re.IGNORECASE | re.DOTALL)
    if metrics_match:
        metrics_content = metrics_match.group(1)
        if "baseline" not in metrics_content.lower() or "target" not in metrics_content.lower():
            if "→" not in metrics_content and "->" not in metrics_content:
                result["warnings"].append({
                    "section": "Success Metrics",
                    "message": "Success Metrics should include baseline → target format"
                })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate PRD document")
    parser.add_argument("--path", "-p", default="docs/prds/prd.md", help="Path to PRD file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    prd_path = Path(args.path)
    if not prd_path.is_absolute():
        # Try to find project root
        project_root = Path.cwd()
        while project_root != project_root.parent:
            if (project_root / "docs").is_dir():
                prd_path = project_root / args.path
                break
            project_root = project_root.parent

    result = validate_prd(prd_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nPRD Validation: {prd_path}")
        print("=" * 50)

        if result["sections_found"]:
            print(f"\nSections Found ({len(result['sections_found'])}):")
            for section in result["sections_found"]:
                print(f"  ✓ {section}")

        if result["sections_missing"]:
            print(f"\nMissing Sections ({len(result['sections_missing'])}):")
            for section in result["sections_missing"]:
                print(f"  ✗ {section}")

        if result["issues"]:
            print(f"\nIssues ({len(result['issues'])}):")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue['message']}")

        if result["warnings"]:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                print(f"  [WARN] {warning['message']}")

        status = "PASSED" if result["valid"] else "FAILED"
        print(f"\nResult: {status}")

    import sys
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
