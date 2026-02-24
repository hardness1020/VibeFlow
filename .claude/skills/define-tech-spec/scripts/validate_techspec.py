#!/usr/bin/env python3
"""
Tech Spec Validation Script

Validates that a tech spec has all required sections and architecture elements.

Usage:
    python validate_techspec.py <spec-name> [--json]

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
    ("Overview", r"#+\s*Overview"),
    ("Architecture", r"#+\s*Architecture"),
    ("Interfaces", r"#+\s*Interfaces"),
    ("Data & Storage", r"#+\s*Data"),
    ("Reliability", r"#+\s*Reliability"),
    ("Security", r"#+\s*Security"),
    ("Evaluation", r"#+\s*Evaluation"),
]


def find_spec_file(project_root: Path, spec_name: Optional[str]) -> Optional[Path]:
    """Find spec file by name."""
    specs_path = project_root / "docs" / "specs"
    if not specs_path.exists():
        return None

    if spec_name:
        spec_path = specs_path / f"spec-{spec_name}.md"
        if spec_path.exists():
            return spec_path

    # Get most recent spec
    spec_files = [f for f in specs_path.glob("spec-*.md") if f.name != "index.md"]
    if spec_files:
        return max(spec_files, key=lambda f: f.stat().st_mtime)

    return None


def validate_techspec(spec_path: Path) -> Dict[str, Any]:
    """Validate tech spec document."""
    result = {
        "file": str(spec_path),
        "valid": True,
        "issues": [],
        "warnings": [],
        "sections_found": [],
        "sections_missing": []
    }

    if not spec_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Spec file not found: {spec_path}"
        })
        return result

    content = spec_path.read_text()
    line_count = len(content.split("\n"))

    # Check header
    if not re.search(r"\*\*Version\*\*", content):
        result["warnings"].append({
            "message": "Spec should have Version in header"
        })

    if not re.search(r"\*\*Status\*\*", content):
        result["warnings"].append({
            "message": "Spec should have Status in header (Draft/Current/Superseded)"
        })

    if not re.search(r"\*\*PRD\*\*", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "Spec should link to PRD"
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

    # Check for Table of Contents if >800 lines
    if line_count > 800:
        if not re.search(r"#+\s*Table of Contents|#+\s*TOC", content, re.IGNORECASE):
            result["warnings"].append({
                "message": f"Spec has {line_count} lines - should include Table of Contents"
            })

    # Check Architecture section has required elements
    arch_match = re.search(r"#+\s*Architecture.*?\n(.*?)(?=\n#[^#]|\Z)", content, re.IGNORECASE | re.DOTALL)
    if arch_match:
        arch_content = arch_match.group(1)

        # Check for topology diagram
        has_diagram = (
            "mermaid" in arch_content.lower() or
            "```" in arch_content and ("┌" in arch_content or "+-" in arch_content or "│" in arch_content)
        )
        if not has_diagram:
            result["warnings"].append({
                "section": "Architecture",
                "message": "Architecture should include topology diagram (Mermaid or ASCII)"
            })

        # Check for component inventory table
        if "|" not in arch_content:
            result["warnings"].append({
                "section": "Architecture",
                "message": "Architecture should include component inventory table"
            })

    # Check for implementation code (should not be present)
    # Look for function bodies (def ... : followed by indented code)
    impl_patterns = [
        r"def \w+\([^)]*\):\s*\n\s+[^#\s]",  # Python function with body
        r"async def \w+\([^)]*\):\s*\n\s+[^#\s]",  # Async function with body
        r"for \w+ in",  # For loops
        r"while .+:",  # While loops
        r"if .+:\s*\n\s+\w",  # If statements with body
    ]
    for pattern in impl_patterns:
        if re.search(pattern, content):
            result["warnings"].append({
                "message": "Spec may contain implementation code - keep to interface signatures only"
            })
            break

    # Check for interface signatures (good)
    if not re.search(r"(?:class|def|async def|interface)\s+\w+", content):
        result["warnings"].append({
            "message": "Spec should include service/class interface signatures"
        })

    # Check size - warn if too large
    if line_count > 1500:
        result["warnings"].append({
            "message": f"Spec has {line_count} lines - consider splitting or removing feature-level detail"
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate tech spec")
    parser.add_argument("name", nargs="?", help="Spec name (e.g., api, llm, frontend)")
    parser.add_argument("--path", "-p", help="Direct path to spec file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Find project root
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    # Find spec file
    if args.path:
        spec_path = Path(args.path)
    else:
        spec_path = find_spec_file(project_root, args.name)

    if not spec_path:
        print(json.dumps({"valid": False, "issues": [{"severity": "error", "message": "No spec file found"}]}))
        import sys
        sys.exit(1)

    result = validate_techspec(spec_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nTech Spec Validation: {spec_path}")
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
