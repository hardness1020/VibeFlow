#!/usr/bin/env python3
"""
Discovery Document Validation Script

Validates that a discovery document has all required phases.

Usage:
    python validate_discovery.py <ID> [--path PATH] [--json]

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


REQUIRED_PHASES = [
    ("Phase 0", r"#+\s*Phase\s*0"),
    ("Phase 1", r"#+\s*Phase\s*1"),
    ("Phase 2", r"#+\s*Phase\s*2"),
    ("Phase 3", r"#+\s*Phase\s*3"),
    ("Phase 4", r"#+\s*Phase\s*4"),
    ("Risk Assessment", r"#+\s*Risk\s*Assessment"),
]

REQUIRED_SUBSECTIONS = {
    "Phase 0": ["Affected Specs", "Patterns", "Confidence"],
    "Phase 1": ["Discrepancies", "Confidence"],
    "Phase 2": ["Test Files", "Test Update Checklist", "Coverage"],
    "Phase 3": ["Dependency", "Side Effects", "Impact"],
    "Phase 4": ["Similar", "Reusable", "Duplicate"],
}


def find_discovery_file(project_root: Path, feature_id: Optional[str]) -> Optional[Path]:
    """Find discovery file by ID or most recent."""
    disco_path = project_root / "docs" / "discovery"
    if not disco_path.exists():
        return None

    if feature_id:
        matches = list(disco_path.glob(f"disco-{feature_id}*.md"))
        if matches:
            return matches[0]

    # Get most recent
    disco_files = list(disco_path.glob("disco-*.md"))
    if disco_files:
        return max(disco_files, key=lambda f: f.stat().st_mtime)

    return None


def validate_discovery(disco_path: Path) -> Dict[str, Any]:
    """Validate discovery document."""
    result = {
        "file": str(disco_path),
        "valid": True,
        "issues": [],
        "warnings": [],
        "phases_found": [],
        "phases_missing": []
    }

    if not disco_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Discovery file not found: {disco_path}"
        })
        return result

    content = disco_path.read_text()

    # Check header
    if not re.search(r"\*\*(?:ID|Type|Date|Size Track)\*\*", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "Discovery should have header with ID, Type, Date, Size Track"
        })

    # Check summary
    if not re.search(r"#+\s*Summary", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "Discovery should have Summary section"
        })

    # Check required phases
    for phase_name, pattern in REQUIRED_PHASES:
        if re.search(pattern, content, re.IGNORECASE):
            result["phases_found"].append(phase_name)

            # Check subsections for this phase
            if phase_name in REQUIRED_SUBSECTIONS:
                phase_start = re.search(pattern, content, re.IGNORECASE)
                if phase_start:
                    # Get content until next phase
                    phase_content = content[phase_start.end():]
                    next_phase = re.search(r"\n#+\s*Phase\s*\d", phase_content)
                    if next_phase:
                        phase_content = phase_content[:next_phase.start()]

                    missing_subsections = []
                    for subsection in REQUIRED_SUBSECTIONS[phase_name]:
                        if subsection.lower() not in phase_content.lower():
                            missing_subsections.append(subsection)

                    if missing_subsections:
                        result["warnings"].append({
                            "phase": phase_name,
                            "message": f"{phase_name} missing subsections: {', '.join(missing_subsections)}"
                        })
        else:
            result["phases_missing"].append(phase_name)
            result["valid"] = False
            result["issues"].append({
                "severity": "error",
                "phase": phase_name,
                "message": f"Missing required phase: {phase_name}"
            })

    # Check for Go/No-Go recommendation
    if "go/no-go" not in content.lower() and "recommendation" not in content.lower():
        result["warnings"].append({
            "message": "Discovery should include Go/No-Go Recommendation"
        })

    # Check test update checklist has markers
    if "test update checklist" in content.lower() or "test impact" in content.lower():
        if not re.search(r"(?:✅|🔄|❌|➕|KEEP|UPDATE|REMOVE|ADD)", content):
            result["warnings"].append({
                "message": "Test Update Checklist should use KEEP/UPDATE/REMOVE/ADD markers"
            })

    # Check for code examples (should have some patterns documented)
    if "```" not in content:
        result["warnings"].append({
            "message": "Discovery should include code examples showing patterns to follow"
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate discovery document")
    parser.add_argument("id", nargs="?", help="Feature ID (e.g., 030)")
    parser.add_argument("--path", "-p", help="Direct path to discovery file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Find project root
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    # Find discovery file
    if args.path:
        disco_path = Path(args.path)
    else:
        disco_path = find_discovery_file(project_root, args.id)

    if not disco_path:
        print(json.dumps({"valid": False, "issues": [{"severity": "error", "message": "No discovery file found"}]}))
        import sys
        sys.exit(1)

    result = validate_discovery(disco_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nDiscovery Validation: {disco_path}")
        print("=" * 50)

        if result["phases_found"]:
            print(f"\nPhases Found ({len(result['phases_found'])}):")
            for phase in result["phases_found"]:
                print(f"  ✓ {phase}")

        if result["phases_missing"]:
            print(f"\nMissing Phases ({len(result['phases_missing'])}):")
            for phase in result["phases_missing"]:
                print(f"  ✗ {phase}")

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
