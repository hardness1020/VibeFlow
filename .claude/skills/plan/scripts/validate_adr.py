#!/usr/bin/env python3
"""
ADR Validation Script

Validates that an ADR has all required sections.

Usage:
    python validate_adr.py <ID> [--json]

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


REQUIRED_SECTIONS = [
    ("Context", r"#+\s*Context"),
    ("Decision", r"#+\s*Decision"),
    ("Consequences", r"#+\s*Consequences"),
    ("Alternatives", r"#+\s*Alternatives"),
    ("Rollback", r"#+\s*Rollback"),
]

RECOMMENDED_SECTIONS = [
    ("Links", r"#+\s*Links"),
]


def find_adr_file(project_root: Path, adr_id: Optional[str]) -> Optional[Path]:
    """Find ADR file by ID."""
    adrs_path = project_root / "docs" / "adrs"
    if not adrs_path.exists():
        return None

    if adr_id:
        matches = list(adrs_path.glob(f"adr-{adr_id}*.md"))
        if matches:
            return matches[0]

    # Get most recent ADR
    adr_files = list(adrs_path.glob("adr-*.md"))
    if adr_files:
        return max(adr_files, key=lambda f: f.stat().st_mtime)

    return None


def validate_adr(adr_path: Path) -> Dict[str, Any]:
    """Validate ADR document."""
    result = {
        "file": str(adr_path),
        "valid": True,
        "issues": [],
        "warnings": [],
        "sections_found": [],
        "sections_missing": []
    }

    if not adr_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"ADR file not found: {adr_path}"
        })
        return result

    content = adr_path.read_text()

    # Check header
    if not re.search(r"\*\*Status\*\*", content):
        result["warnings"].append({
            "message": "ADR should have Status in header (Draft/Accepted/Rejected/Superseded)"
        })
    else:
        # Check status value
        status_match = re.search(r"\*\*Status\*\*[:\s]*(\w+)", content, re.IGNORECASE)
        if status_match:
            status = status_match.group(1).lower()
            valid_statuses = ["draft", "accepted", "rejected", "superseded"]
            if status not in valid_statuses:
                result["warnings"].append({
                    "message": f"ADR status should be one of: {', '.join(valid_statuses)}"
                })

    if not re.search(r"\*\*File\*\*", content):
        result["warnings"].append({
            "message": "ADR should have File path in header"
        })

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
        if re.search(pattern, content, re.IGNORECASE):
            result["sections_found"].append(section_name)
        else:
            result["warnings"].append({
                "section": section_name,
                "message": f"Missing recommended section: {section_name}"
            })

    # Check Consequences has positive and negative
    consequences_match = re.search(
        r"#+\s*Consequences.*?\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )
    if consequences_match:
        cons_content = consequences_match.group(1)
        has_positive = bool(re.search(r"(?:\+|positive|pro|benefit)", cons_content, re.IGNORECASE))
        has_negative = bool(re.search(r"(?:−|-|negative|con|tradeoff|cost)", cons_content, re.IGNORECASE))

        if not has_positive:
            result["warnings"].append({
                "section": "Consequences",
                "message": "Consequences should include positive impacts (+)"
            })
        if not has_negative:
            result["warnings"].append({
                "section": "Consequences",
                "message": "Consequences should include negative impacts/tradeoffs (−)"
            })

    # Check Alternatives has at least one alternative
    alternatives_match = re.search(
        r"#+\s*Alternatives.*?\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )
    if alternatives_match:
        alt_content = alternatives_match.group(1)
        if len(alt_content.strip()) < 50:
            result["warnings"].append({
                "section": "Alternatives",
                "message": "Alternatives section seems too brief - include at least one alternative"
            })

    # Check Rollback has actionable steps
    rollback_match = re.search(
        r"#+\s*Rollback.*?\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )
    if rollback_match:
        rollback_content = rollback_match.group(1)
        if len(rollback_content.strip()) < 30:
            result["warnings"].append({
                "section": "Rollback",
                "message": "Rollback section should include specific steps"
            })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate ADR")
    parser.add_argument("id", nargs="?", help="ADR ID (e.g., 001, 045)")
    parser.add_argument("--path", "-p", help="Direct path to ADR file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Find project root
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    # Find ADR file
    if args.path:
        adr_path = Path(args.path)
    else:
        adr_path = find_adr_file(project_root, args.id)

    if not adr_path:
        print(json.dumps({"valid": False, "issues": [{"severity": "error", "message": "No ADR file found"}]}))
        import sys
        sys.exit(1)

    result = validate_adr(adr_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nADR Validation: {adr_path}")
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
