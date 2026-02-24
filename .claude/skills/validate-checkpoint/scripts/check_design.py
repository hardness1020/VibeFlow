#!/usr/bin/env python3
"""
Checkpoint #2: Design Complete Validator

Validates:
- FEATURE spec exists with required sections
- API Design section has exact function/class signatures
- Acceptance criteria are testable
- Links to TECH-SPECs with version numbers
- Schedule file updated

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Warnings only
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


FEATURE_REQUIRED_SECTIONS = [
    "Architecture Conformance",
    "API Design",
    "Acceptance Criteria",
    "Design Changes",
    "Test & Eval Plan",
    "Telemetry",
    "Edge Cases",
]

FEATURE_REQUIRED_MEDIUM_LARGE = [
    "Stage B Discovery",
    "Test Impact",
    "Existing Implementation",
    "Dependency",
]


def find_feature_file(docs_path: Path, feature_id: Optional[str]) -> Optional[Path]:
    """Find the feature spec file."""
    features_path = docs_path / "features"
    if not features_path.exists():
        return None

    if feature_id:
        # Look for specific feature
        matches = list(features_path.glob(f"ft-{feature_id}*.md"))
        if matches:
            return matches[0]

    # Get the most recent feature file
    feature_files = [f for f in features_path.glob("ft-*.md") if f.name != "schedule.md"]
    if not feature_files:
        return None

    return max(feature_files, key=lambda f: f.stat().st_mtime)


def check_api_design_section(content: str) -> Dict[str, Any]:
    """Validate the API Design section has required elements."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Find API Design section
    api_design_match = re.search(
        r"#+\s*API Design\s*\n(.*?)(?=\n#[^#]|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not api_design_match:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "API Design section not found"
        })
        return result

    api_section = api_design_match.group(1)

    # Check for function/method signatures
    has_signatures = bool(re.search(
        r"(?:def |function |class |async def |->|:.*\))",
        api_section
    ))

    # Check for signature indicators (Signature:, Parameters:, Returns:)
    has_signature_docs = bool(re.search(
        r"(?:\*\*Signature\*\*|\*\*Parameters\*\*|\*\*Returns\*\*|Parameters:|Returns:)",
        api_section,
        re.IGNORECASE
    ))

    if not has_signatures and not has_signature_docs:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "API Design must include function/class signatures with parameters and return types"
        })

    # Check for parameter types
    if not re.search(r"(?:str|int|float|bool|List|Dict|Optional|\[\]|string|number|boolean)", api_section):
        result["warnings"].append({
            "message": "API Design should specify parameter types"
        })

    # Check for API endpoint if applicable
    if "endpoint" in content.lower() or "api" in content.lower():
        if not re.search(r"(?:GET|POST|PUT|DELETE|PATCH)\s+/", api_section):
            result["warnings"].append({
                "message": "API Design mentions endpoints but no HTTP method/path found"
            })

    return result


def check_acceptance_criteria(content: str) -> Dict[str, Any]:
    """Validate acceptance criteria are present and testable."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Find Acceptance Criteria section
    ac_match = re.search(
        r"#+\s*Acceptance Criteria\s*\n(.*?)(?=\n#[^#]|\Z)",
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

    # Check for checklist or Gherkin format
    has_checklist = bool(re.search(r"- \[ \]|\* \[ \]|^\d+\.", ac_section, re.MULTILINE))
    has_gherkin = bool(re.search(r"(?:Given|When|Then|And|But)\s+", ac_section, re.IGNORECASE))

    if not has_checklist and not has_gherkin:
        result["warnings"].append({
            "message": "Acceptance criteria should use checklist (- [ ]) or Gherkin format"
        })

    # Count criteria
    criteria_count = len(re.findall(r"(?:- \[ \]|\* \[ \]|^\d+\.|Given\s+)", ac_section, re.MULTILINE | re.IGNORECASE))
    if criteria_count < 3:
        result["warnings"].append({
            "message": f"Only {criteria_count} acceptance criteria found - consider adding more"
        })

    return result


def check_spec_links(content: str) -> Dict[str, Any]:
    """Check for links to TECH-SPECs with versions."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Check for TECH-SPEC references
    spec_refs = re.findall(r"spec-\w+\.md(?:\s*\(v[\d.]+\))?", content, re.IGNORECASE)

    if not spec_refs:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": "Feature must link to TECH-SPECs"
        })
        return result

    # Check for version numbers
    versioned_refs = [r for r in spec_refs if re.search(r"v[\d.]+", r)]
    if len(versioned_refs) < len(spec_refs):
        result["warnings"].append({
            "message": "TECH-SPEC references should include version numbers (e.g., spec-api.md (v1.3))"
        })

    return result


def check_schedule_updated(docs_path: Path, feature_id: Optional[str]) -> Dict[str, Any]:
    """Check if schedule.md includes this feature."""
    result = {"valid": True, "issues": [], "warnings": []}

    schedule_path = docs_path / "features" / "schedule.md"
    if not schedule_path.exists():
        result["warnings"].append({
            "message": "docs/features/schedule.md not found - create to track feature status"
        })
        return result

    content = schedule_path.read_text()

    if feature_id:
        if f"ft-{feature_id}" not in content.lower() and feature_id not in content:
            result["warnings"].append({
                "message": f"Feature ft-{feature_id} not found in schedule.md"
            })

    return result


def validate(project_root: Path, feature_id: Optional[str] = None,
             size_track: str = "medium") -> Dict[str, Any]:
    """Main validation function for Checkpoint #2."""
    docs_path = project_root / "docs"

    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find feature file
    feature_file = find_feature_file(docs_path, feature_id)
    if not feature_file:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "file": "docs/features/",
            "message": "No feature spec file found"
        })
        return result

    result["feature_file"] = str(feature_file.relative_to(project_root))
    content = feature_file.read_text()

    # Check required sections
    missing_sections = []
    for section in FEATURE_REQUIRED_SECTIONS:
        pattern = rf"#+\s*{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            missing_sections.append(section)

    if missing_sections:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].append({
            "severity": "error",
            "file": feature_file.name,
            "message": f"Missing required sections: {', '.join(missing_sections)}"
        })
    else:
        result["passed"] += 1

    # Check Medium/Large specific sections
    if size_track in ["medium", "large"]:
        missing_ml = []
        for section in FEATURE_REQUIRED_MEDIUM_LARGE:
            pattern = rf"#+\s*.*{re.escape(section)}"
            if not re.search(pattern, content, re.IGNORECASE):
                missing_ml.append(section)

        if missing_ml:
            result["warnings"].append({
                "file": feature_file.name,
                "message": f"Missing sections for Medium/Large: {', '.join(missing_ml)}"
            })

    # Validate API Design section
    api_result = check_api_design_section(content)
    result["details"]["api_design"] = api_result
    if not api_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend([{**i, "file": feature_file.name} for i in api_result["issues"]])
    else:
        result["passed"] += 1
    result["warnings"].extend([{**w, "file": feature_file.name} for w in api_result.get("warnings", [])])

    # Validate Acceptance Criteria
    ac_result = check_acceptance_criteria(content)
    result["details"]["acceptance_criteria"] = ac_result
    if not ac_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend([{**i, "file": feature_file.name} for i in ac_result["issues"]])
    else:
        result["passed"] += 1
    result["warnings"].extend([{**w, "file": feature_file.name} for w in ac_result.get("warnings", [])])

    # Check SPEC links
    spec_result = check_spec_links(content)
    result["details"]["spec_links"] = spec_result
    if not spec_result["valid"]:
        result["valid"] = False
        result["failed"] += 1
        result["issues"].extend([{**i, "file": feature_file.name} for i in spec_result["issues"]])
    else:
        result["passed"] += 1
    result["warnings"].extend([{**w, "file": feature_file.name} for w in spec_result.get("warnings", [])])

    # Check schedule
    schedule_result = check_schedule_updated(docs_path, feature_id)
    result["details"]["schedule"] = schedule_result
    result["warnings"].extend(schedule_result.get("warnings", []))

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
