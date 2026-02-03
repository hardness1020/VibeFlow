#!/usr/bin/env python3
"""
Checkpoint #1: Planning Complete Validator

Validates:
- PRD exists with required sections
- Discovery document exists (for Medium/Large)
- Tech Specs exist with required sections
- ADRs exist for non-trivial decisions

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


# Required sections for each document type
PRD_REQUIRED_SECTIONS = [
    "Summary",
    "Problem & Context",
    "Users & Use Cases",
    "Scope",
    "Success Metrics",
    "Non-Goals",
    "Requirements",
    "Dependencies",
    "Risks & Mitigations",
]

DISCOVERY_REQUIRED_SECTIONS = [
    "Summary",
    "Phase 0",
    "Phase 1",
    "Phase 2",
    "Phase 3",
    "Phase 4",
    "Risk Assessment",
]

SPEC_REQUIRED_SECTIONS = [
    "Overview",
    "Architecture",
    "Interfaces",
    "Data",
    "Reliability",
    "Security",
    "Evaluation",
]

ADR_REQUIRED_SECTIONS = [
    "Context",
    "Decision",
    "Consequences",
    "Alternatives",
    "Rollback",
]


def check_file_has_sections(file_path: Path, required_sections: List[str]) -> Dict[str, bool]:
    """Check if a file contains the required sections."""
    if not file_path.exists():
        return {section: False for section in required_sections}

    content = file_path.read_text().lower()
    results = {}

    for section in required_sections:
        # Look for section headers (## Section or # Section)
        pattern = rf"#+\s*{re.escape(section.lower())}"
        results[section] = bool(re.search(pattern, content))

    return results


def validate_prd(docs_path: Path) -> Dict[str, Any]:
    """Validate PRD document."""
    result = {"file": "docs/prds/prd.md", "valid": True, "issues": [], "warnings": []}
    prd_path = docs_path / "prds" / "prd.md"

    if not prd_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "PRD file not found"
        })
        return result

    # Check required sections
    sections = check_file_has_sections(prd_path, PRD_REQUIRED_SECTIONS)
    missing = [s for s, found in sections.items() if not found]

    if missing:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Missing required sections: {', '.join(missing)}"
        })

    # Check for implementation details (should not be in PRD)
    content = prd_path.read_text()
    if re.search(r"```(python|javascript|typescript|java|go|rust)", content, re.IGNORECASE):
        result["warnings"].append({
            "message": "PRD contains code blocks - implementation details belong in TECH-SPEC/ADRs"
        })

    # Check for MoSCoW format in Scope
    if "must" not in content.lower() or "should" not in content.lower():
        result["warnings"].append({
            "message": "Scope section should use MoSCoW format (Must/Should/Could/Won't)"
        })

    return result


def validate_discovery(docs_path: Path, feature_id: Optional[str], size_track: str) -> Dict[str, Any]:
    """Validate Discovery document (required for Medium/Large only)."""
    result = {"file": None, "valid": True, "issues": [], "warnings": [], "skipped": False}

    # Discovery only required for Medium/Large
    if size_track in ["micro", "small"]:
        result["skipped"] = True
        result["message"] = "Discovery optional for Micro/Small changes"
        return result

    discovery_path = docs_path / "discovery"
    if not discovery_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "Discovery directory not found (required for Medium/Large changes)"
        })
        return result

    # Find discovery file
    if feature_id:
        disco_files = list(discovery_path.glob(f"disco-{feature_id}*.md"))
    else:
        disco_files = list(discovery_path.glob("disco-*.md"))

    if not disco_files:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "No discovery document found (required for Medium/Large changes)"
        })
        return result

    disco_file = disco_files[0]
    result["file"] = str(disco_file.relative_to(docs_path.parent))

    # Check required sections
    sections = check_file_has_sections(disco_file, DISCOVERY_REQUIRED_SECTIONS)
    missing = [s for s, found in sections.items() if not found]

    if missing:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Missing required discovery phases: {', '.join(missing)}"
        })

    # Check for Go/No-Go recommendation
    content = disco_file.read_text().lower()
    if "go/no-go" not in content and "recommendation" not in content:
        result["warnings"].append({
            "message": "Discovery should include Go/No-Go recommendation"
        })

    return result


def validate_specs(docs_path: Path) -> Dict[str, Any]:
    """Validate Tech Spec documents."""
    result = {"files": [], "valid": True, "issues": [], "warnings": []}

    specs_path = docs_path / "specs"
    if not specs_path.exists():
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "Specs directory not found"
        })
        return result

    spec_files = list(specs_path.glob("spec-*.md"))
    if not spec_files:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "No spec files found in docs/specs/"
        })
        return result

    for spec_file in spec_files:
        if spec_file.name == "index.md":
            continue

        file_result = {"file": spec_file.name, "issues": [], "warnings": []}
        result["files"].append(file_result)

        # Check required sections
        sections = check_file_has_sections(spec_file, SPEC_REQUIRED_SECTIONS)
        missing = [s for s, found in sections.items() if not found]

        if missing:
            result["valid"] = False
            file_result["issues"].append({
                "severity": "error",
                "message": f"Missing required sections: {', '.join(missing)}"
            })

        content = spec_file.read_text()

        # Check for version in header
        if not re.search(r"\*\*Version\*\*.*v\d+\.\d+", content, re.IGNORECASE):
            file_result["warnings"].append({
                "message": "Spec should have version number in header"
            })

        # Check for architecture diagram
        if "```" not in content or ("mermaid" not in content.lower() and
                                     "┌" not in content and "+-" not in content):
            file_result["warnings"].append({
                "message": "Spec should include architecture diagram (Mermaid or ASCII)"
            })

        # Check for component inventory table
        if "|" not in content or "component" not in content.lower():
            file_result["warnings"].append({
                "message": "Spec should include component inventory table"
            })

        # Check file size and ToC requirement
        line_count = len(content.split("\n"))
        if line_count > 800:
            if "table of contents" not in content.lower() and "## toc" not in content.lower():
                file_result["warnings"].append({
                    "message": f"Spec has {line_count} lines - should include Table of Contents"
                })

    return result


def validate_adrs(docs_path: Path) -> Dict[str, Any]:
    """Validate ADR documents."""
    result = {"files": [], "valid": True, "issues": [], "warnings": []}

    adrs_path = docs_path / "adrs"
    if not adrs_path.exists():
        # ADRs may not exist if no non-trivial decisions
        result["warnings"].append({
            "message": "No ADRs directory - ensure no non-trivial decisions require ADRs"
        })
        return result

    adr_files = list(adrs_path.glob("adr-*.md"))
    if not adr_files:
        result["warnings"].append({
            "message": "No ADR files found - ensure no non-trivial decisions require ADRs"
        })
        return result

    for adr_file in adr_files:
        file_result = {"file": adr_file.name, "issues": [], "warnings": []}
        result["files"].append(file_result)

        # Check required sections
        sections = check_file_has_sections(adr_file, ADR_REQUIRED_SECTIONS)
        missing = [s for s, found in sections.items() if not found]

        if missing:
            result["valid"] = False
            file_result["issues"].append({
                "severity": "error",
                "message": f"Missing required sections: {', '.join(missing)}"
            })

        content = adr_file.read_text()

        # Check for status
        if not re.search(r"\*\*Status\*\*.*(?:draft|accepted|rejected)", content, re.IGNORECASE):
            file_result["warnings"].append({
                "message": "ADR should have Status field (Draft/Accepted/Rejected)"
            })

        # Check for consequences (both positive and negative)
        if "+" not in content or "-" not in content and "−" not in content:
            file_result["warnings"].append({
                "message": "Consequences should include both positive (+) and negative (-) impacts"
            })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #1."""
    docs_path = project_root / "docs"

    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Validate PRD
    prd_result = validate_prd(docs_path)
    result["details"]["prd"] = prd_result
    if not prd_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend([{**i, "file": prd_result["file"]} for i in prd_result["issues"]])
    else:
        result["passed"] += 1
    result["warnings"].extend([{**w, "file": prd_result["file"]} for w in prd_result.get("warnings", [])])

    # Validate Discovery (Medium/Large only)
    disco_result = validate_discovery(docs_path, feature_id, size_track)
    result["details"]["discovery"] = disco_result
    if not disco_result.get("skipped"):
        if not disco_result["valid"]:
            result["valid"] = False
            result["failed"] += 1
            result["issues"].extend([{**i, "file": disco_result.get("file")} for i in disco_result["issues"]])
        else:
            result["passed"] += 1
        result["warnings"].extend([{**w, "file": disco_result.get("file")} for w in disco_result.get("warnings", [])])

    # Validate Specs
    specs_result = validate_specs(docs_path)
    result["details"]["specs"] = specs_result
    if not specs_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        for f in specs_result.get("files", []):
            result["issues"].extend([{**i, "file": f["file"]} for i in f.get("issues", [])])
            result["warnings"].extend([{**w, "file": f["file"]} for w in f.get("warnings", [])])
    else:
        result["passed"] += 1

    # Validate ADRs
    adrs_result = validate_adrs(docs_path)
    result["details"]["adrs"] = adrs_result
    if not adrs_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        for f in adrs_result.get("files", []):
            result["issues"].extend([{**i, "file": f["file"]} for i in f.get("issues", [])])
            result["warnings"].extend([{**w, "file": f["file"]} for w in f.get("warnings", [])])
    else:
        result["passed"] += 1
    result["warnings"].extend(adrs_result.get("warnings", []))

    return result


if __name__ == "__main__":
    import sys
    import json

    project_root = Path.cwd()
    # Try to find project root
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    result = validate(project_root)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
