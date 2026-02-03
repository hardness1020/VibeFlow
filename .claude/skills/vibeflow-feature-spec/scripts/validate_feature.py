#!/usr/bin/env python3
"""
Feature Spec Validation Script

Validates that a feature spec has all required sections including API Design.

Usage:
    python validate_feature.py <ID> [--size-track TRACK] [--json]

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
    ("Architecture Conformance", r"#+\s*Architecture\s*Conformance"),
    ("API Design", r"#+\s*API\s*Design"),
    ("Acceptance Criteria", r"#+\s*Acceptance\s*Criteria"),
    ("Design Changes", r"#+\s*Design\s*Changes"),
    ("Test & Eval Plan", r"#+\s*Test"),
    ("Telemetry", r"#+\s*Telemetry"),
    ("Edge Cases", r"#+\s*Edge\s*Cases"),
]

MEDIUM_LARGE_SECTIONS = [
    ("Stage B Discovery", r"#+\s*Stage\s*B\s*Discovery"),
    ("Test Impact", r"#+\s*Test\s*Impact"),
    ("Existing Implementation", r"#+\s*Existing\s*Implementation"),
    ("Dependency", r"#+\s*Dependency"),
]


def find_feature_file(project_root: Path, feature_id: Optional[str]) -> Optional[Path]:
    """Find feature spec file by ID."""
    features_path = project_root / "docs" / "features"
    if not features_path.exists():
        return None

    if feature_id:
        matches = list(features_path.glob(f"ft-{feature_id}*.md"))
        if matches:
            return matches[0]

    # Get most recent feature
    feature_files = [f for f in features_path.glob("ft-*.md") if f.name != "schedule.md"]
    if feature_files:
        return max(feature_files, key=lambda f: f.stat().st_mtime)

    return None


def validate_api_design(content: str) -> Dict[str, Any]:
    """Validate API Design section has required elements."""
    result = {"valid": True, "issues": [], "warnings": [], "signatures_found": 0}

    # Find API Design section
    api_match = re.search(
        r"#+\s*API\s*Design\s*\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not api_match:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "API Design section not found"
        })
        return result

    api_section = api_match.group(1)

    # Check for signature indicators
    signature_patterns = [
        r"\*\*Signature\*\*",
        r"def \w+\(",
        r"function \w+\(",
        r"async def \w+\(",
        r"class \w+",
        r"→|->",
    ]

    signature_count = 0
    for pattern in signature_patterns:
        matches = re.findall(pattern, api_section)
        signature_count += len(matches)

    result["signatures_found"] = signature_count

    if signature_count == 0:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "API Design must include function/method signatures"
        })

    # Check for parameter documentation
    if "parameter" not in api_section.lower() and "param" not in api_section.lower():
        result["warnings"].append({
            "message": "API Design should document parameters"
        })

    # Check for return type documentation
    if "return" not in api_section.lower():
        result["warnings"].append({
            "message": "API Design should document return types"
        })

    # Check for API endpoints if mentioned
    if "endpoint" in content.lower() or "/api/" in content:
        if not re.search(r"(?:GET|POST|PUT|DELETE|PATCH)\s+/", api_section):
            result["warnings"].append({
                "message": "Feature mentions endpoints but API Design lacks HTTP method/path"
            })

    return result


def validate_acceptance_criteria(content: str) -> Dict[str, Any]:
    """Validate acceptance criteria are testable."""
    result = {"valid": True, "issues": [], "warnings": [], "criteria_count": 0}

    # Find Acceptance Criteria section
    ac_match = re.search(
        r"#+\s*Acceptance\s*Criteria\s*\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not ac_match:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "Acceptance Criteria section not found"
        })
        return result

    ac_section = ac_match.group(1)

    # Count criteria (checkboxes or Gherkin)
    checkbox_count = len(re.findall(r"- \[ \]|\* \[ \]", ac_section))
    gherkin_count = len(re.findall(r"(?:Given|When|Then)\s+", ac_section, re.IGNORECASE))

    result["criteria_count"] = max(checkbox_count, gherkin_count // 3)

    if result["criteria_count"] < 3:
        result["warnings"].append({
            "message": f"Only {result['criteria_count']} acceptance criteria found - consider adding more"
        })

    # Check for testable language
    vague_terms = ["should be good", "should work", "must be nice", "easy to use"]
    for term in vague_terms:
        if term in ac_section.lower():
            result["warnings"].append({
                "message": f"Acceptance criteria should be specific, not vague ('{term}')"
            })

    return result


def validate_spec_links(content: str) -> Dict[str, Any]:
    """Validate links to TECH-SPECs with versions."""
    result = {"valid": True, "issues": [], "warnings": [], "specs_linked": []}

    # Find spec references
    spec_refs = re.findall(r"spec-(\w+)\.md(?:\s*\(v[\d.]+\))?", content, re.IGNORECASE)
    result["specs_linked"] = list(set(spec_refs))

    if not spec_refs:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "Feature must link to TECH-SPECs"
        })
        return result

    # Check for version numbers
    versioned = len(re.findall(r"spec-\w+\.md\s*\(v[\d.]+\)", content, re.IGNORECASE))
    if versioned < len(set(spec_refs)):
        result["warnings"].append({
            "message": "TECH-SPEC references should include version numbers"
        })

    return result


def validate_feature(feature_path: Path, size_track: str = "medium") -> Dict[str, Any]:
    """Validate feature spec document."""
    result = {
        "file": str(feature_path),
        "valid": True,
        "issues": [],
        "warnings": [],
        "sections_found": [],
        "sections_missing": [],
        "size_track": size_track
    }

    if not feature_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Feature file not found: {feature_path}"
        })
        return result

    content = feature_path.read_text()

    # Check header
    if not re.search(r"\*\*(?:File|Owner|TECH-SPEC)\*\*", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "Feature should have header with File, Owner, TECH-SPECs"
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

    # Check Medium/Large specific sections
    if size_track in ["medium", "large"]:
        for section_name, pattern in MEDIUM_LARGE_SECTIONS:
            if not re.search(pattern, content, re.IGNORECASE):
                result["warnings"].append({
                    "section": section_name,
                    "message": f"Missing section for Medium/Large: {section_name}"
                })

    # Validate API Design
    api_result = validate_api_design(content)
    if not api_result["valid"]:
        result["valid"] = False
        result["issues"].extend(api_result["issues"])
    result["warnings"].extend(api_result.get("warnings", []))
    result["api_signatures"] = api_result.get("signatures_found", 0)

    # Validate Acceptance Criteria
    ac_result = validate_acceptance_criteria(content)
    if not ac_result["valid"]:
        result["valid"] = False
        result["issues"].extend(ac_result["issues"])
    result["warnings"].extend(ac_result.get("warnings", []))
    result["acceptance_criteria_count"] = ac_result.get("criteria_count", 0)

    # Validate spec links
    links_result = validate_spec_links(content)
    if not links_result["valid"]:
        result["valid"] = False
        result["issues"].extend(links_result["issues"])
    result["warnings"].extend(links_result.get("warnings", []))
    result["specs_linked"] = links_result.get("specs_linked", [])

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate feature spec")
    parser.add_argument("id", nargs="?", help="Feature ID (e.g., 030)")
    parser.add_argument("--path", "-p", help="Direct path to feature file")
    parser.add_argument("--size-track", "-s", choices=["micro", "small", "medium", "large"],
                        default="medium", help="Size track for the change")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Find project root
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    # Find feature file
    if args.path:
        feature_path = Path(args.path)
    else:
        feature_path = find_feature_file(project_root, args.id)

    if not feature_path:
        error = {"valid": False, "issues": [{"severity": "error", "message": "No feature file found"}]}
        print(json.dumps(error))
        import sys
        sys.exit(1)

    result = validate_feature(feature_path, args.size_track)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nFeature Spec Validation: {feature_path}")
        print("=" * 50)

        if result["sections_found"]:
            print(f"\nSections Found ({len(result['sections_found'])}):")
            for section in result["sections_found"]:
                print(f"  ✓ {section}")

        if result["sections_missing"]:
            print(f"\nMissing Sections ({len(result['sections_missing'])}):")
            for section in result["sections_missing"]:
                print(f"  ✗ {section}")

        print(f"\nAPI Design: {result.get('api_signatures', 0)} signatures found")
        print(f"Acceptance Criteria: {result.get('acceptance_criteria_count', 0)} criteria found")
        print(f"Specs Linked: {', '.join(result.get('specs_linked', [])) or 'None'}")

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
