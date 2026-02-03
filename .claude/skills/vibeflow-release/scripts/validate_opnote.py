#!/usr/bin/env python3
"""
OP-NOTE Validation Script

Validates that an OP-NOTE has all required sections and content.

Usage:
    python validate_opnote.py [--path <opnote-path>] [--json]

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


# Required sections for a valid OP-NOTE
REQUIRED_SECTIONS = [
    "preflight",
    "deploy",  # "deploy steps" or "deployment"
    "monitoring",
    "runbook",
    "rollback",
    "post-deploy",  # "post-deploy checks" or "post-deployment"
]

# Required header fields
REQUIRED_HEADER_FIELDS = ["file", "date"]


def find_opnotes(project_root: Path) -> List[Path]:
    """Find all OP-NOTE files in the project."""
    opnotes_dir = project_root / "docs" / "op-notes"

    if not opnotes_dir.exists():
        return []

    opnotes = []
    for f in opnotes_dir.glob("op-*.md"):
        if f.name != "index.md":
            opnotes.append(f)

    return opnotes


def check_header(content: str) -> Dict[str, Any]:
    """Check OP-NOTE header fields."""
    result = {"valid": True, "issues": [], "warnings": [], "fields": {}}

    # Check for file field
    file_match = re.search(r"\*\*File:\*\*\s*(.+)", content)
    if file_match:
        result["fields"]["file"] = file_match.group(1).strip()
    else:
        result["issues"].append({
            "severity": "error",
            "message": "Missing **File:** field in header"
        })
        result["valid"] = False

    # Check for date field
    date_match = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", content)
    if date_match:
        result["fields"]["date"] = date_match.group(1)
    else:
        result["issues"].append({
            "severity": "error",
            "message": "Missing **Date:** field in header (format: YYYY-MM-DD)"
        })
        result["valid"] = False

    # Check for features field (warning only)
    features_match = re.search(r"\*\*Features?:\*\*\s*(.+)", content)
    if features_match:
        result["fields"]["features"] = features_match.group(1).strip()
    else:
        result["warnings"].append({
            "message": "Missing **Features:** field - recommended to list covered features"
        })

    return result


def check_sections(content: str) -> Dict[str, Any]:
    """Check for required sections."""
    result = {"valid": True, "issues": [], "warnings": [], "found": [], "missing": []}

    content_lower = content.lower()

    section_patterns = {
        "preflight": [r"##\s*preflight", r"##\s*pre-flight", r"##\s*prerequisites"],
        "deploy": [r"##\s*deploy\s*steps", r"##\s*deployment", r"##\s*deploy\b"],
        "monitoring": [r"##\s*monitoring", r"##\s*observability"],
        "runbook": [r"##\s*runbook", r"##\s*playbook", r"##\s*troubleshooting"],
        "rollback": [r"##\s*rollback", r"##\s*roll-back", r"##\s*revert"],
        "post-deploy": [r"##\s*post-deploy", r"##\s*post-deployment", r"##\s*verification"],
    }

    for section, patterns in section_patterns.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, content_lower):
                found = True
                result["found"].append(section)
                break

        if not found:
            result["missing"].append(section)
            result["issues"].append({
                "severity": "error",
                "message": f"Missing required section: {section}"
            })
            result["valid"] = False

    return result


def check_preflight_content(content: str) -> Dict[str, Any]:
    """Check preflight section has substantive content."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Find preflight section
    preflight_match = re.search(
        r"##\s*(?:preflight|pre-flight|prerequisites)(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not preflight_match:
        return result  # Already caught by section check

    preflight_content = preflight_match.group(1)

    # Check for migrations mention
    if "migration" not in preflight_content.lower():
        result["warnings"].append({
            "message": "Preflight should document migrations (or explicitly state none needed)"
        })

    # Check for feature flags mention
    if "flag" not in preflight_content.lower() and "feature" not in preflight_content.lower():
        result["warnings"].append({
            "message": "Preflight should document feature flags (or explicitly state none)"
        })

    # Check for environment variables mention
    if "env" not in preflight_content.lower() and "variable" not in preflight_content.lower():
        result["warnings"].append({
            "message": "Preflight should document environment variables"
        })

    return result


def check_deploy_steps(content: str) -> Dict[str, Any]:
    """Check deploy steps have commands and verification."""
    result = {"valid": True, "issues": [], "warnings": [], "step_count": 0}

    # Find deploy section
    deploy_match = re.search(
        r"##\s*(?:deploy\s*steps?|deployment)(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not deploy_match:
        return result

    deploy_content = deploy_match.group(1)

    # Count numbered steps
    steps = re.findall(r"^\s*\d+[\.\)]\s*", deploy_content, re.MULTILINE)
    result["step_count"] = len(steps)

    if len(steps) == 0:
        result["issues"].append({
            "severity": "error",
            "message": "Deploy section should have numbered steps"
        })
        result["valid"] = False

    # Check for code blocks (commands)
    code_blocks = re.findall(r"```", deploy_content)
    if len(code_blocks) < 2:  # At least one code block (open + close)
        result["warnings"].append({
            "message": "Deploy steps should include code blocks with exact commands"
        })

    # Check for verification mentions
    if "verify" not in deploy_content.lower() and "check" not in deploy_content.lower():
        result["warnings"].append({
            "message": "Deploy steps should include verification for each step"
        })

    return result


def check_runbook_content(content: str) -> Dict[str, Any]:
    """Check runbook has symptom/diagnose/remediate structure."""
    result = {"valid": True, "issues": [], "warnings": [], "entries": 0}

    # Find runbook section
    runbook_match = re.search(
        r"##\s*(?:runbook|playbook|troubleshooting)(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not runbook_match:
        return result

    runbook_content = runbook_match.group(1).lower()

    # Check for symptom entries
    symptoms = re.findall(r"symptom", runbook_content)
    result["entries"] = len(symptoms)

    if len(symptoms) == 0:
        result["warnings"].append({
            "message": "Runbook should have at least one 'Symptom:' entry"
        })

    # Check for diagnose/remediate structure
    if "diagnose" not in runbook_content and "diagnosis" not in runbook_content:
        result["warnings"].append({
            "message": "Runbook entries should include 'Diagnose:' steps"
        })

    if "remediate" not in runbook_content and "action" not in runbook_content and "fix" not in runbook_content:
        result["warnings"].append({
            "message": "Runbook entries should include 'Remediate:' actions"
        })

    return result


def check_rollback_content(content: str) -> Dict[str, Any]:
    """Check rollback section has steps and conditions."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Find rollback section
    rollback_match = re.search(
        r"##\s*(?:rollback|roll-back|revert)(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not rollback_match:
        return result

    rollback_content = rollback_match.group(1)

    # Check for numbered steps or commands
    has_steps = bool(re.search(r"^\s*\d+[\.\)]", rollback_content, re.MULTILINE))
    has_code = "```" in rollback_content

    if not has_steps and not has_code:
        result["issues"].append({
            "severity": "error",
            "message": "Rollback section must have specific steps or commands"
        })
        result["valid"] = False

    # Check for data compatibility notes
    if "data" not in rollback_content.lower() and "migration" not in rollback_content.lower():
        result["warnings"].append({
            "message": "Rollback should address data compatibility"
        })

    return result


def check_monitoring_content(content: str) -> Dict[str, Any]:
    """Check monitoring section has dashboards and alerts."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Find monitoring section
    monitoring_match = re.search(
        r"##\s*(?:monitoring|observability)(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not monitoring_match:
        return result

    monitoring_content = monitoring_match.group(1).lower()

    # Check for dashboard mention
    if "dashboard" not in monitoring_content:
        result["warnings"].append({
            "message": "Monitoring should list relevant dashboards"
        })

    # Check for alert mention
    if "alert" not in monitoring_content:
        result["warnings"].append({
            "message": "Monitoring should list relevant alerts"
        })

    # Check for SLO/SLI mention
    if "slo" not in monitoring_content and "sli" not in monitoring_content:
        result["warnings"].append({
            "message": "Monitoring should include SLOs/SLIs"
        })

    return result


def validate_opnote(opnote_path: Path) -> Dict[str, Any]:
    """Validate a single OP-NOTE file."""
    result = {
        "valid": True,
        "file": str(opnote_path),
        "issues": [],
        "warnings": [],
        "details": {}
    }

    try:
        content = opnote_path.read_text()
    except Exception as e:
        result["valid"] = False
        result["issues"].append({
            "severity": "error",
            "message": f"Cannot read file: {e}"
        })
        return result

    # Check header
    header_result = check_header(content)
    result["details"]["header"] = header_result
    if not header_result["valid"]:
        result["valid"] = False
    result["issues"].extend(header_result.get("issues", []))
    result["warnings"].extend(header_result.get("warnings", []))

    # Check sections
    sections_result = check_sections(content)
    result["details"]["sections"] = sections_result
    if not sections_result["valid"]:
        result["valid"] = False
    result["issues"].extend(sections_result.get("issues", []))
    result["warnings"].extend(sections_result.get("warnings", []))

    # Check section content (only if sections exist)
    if "preflight" in sections_result.get("found", []):
        preflight_result = check_preflight_content(content)
        result["details"]["preflight"] = preflight_result
        result["warnings"].extend(preflight_result.get("warnings", []))

    if "deploy" in sections_result.get("found", []):
        deploy_result = check_deploy_steps(content)
        result["details"]["deploy"] = deploy_result
        if not deploy_result["valid"]:
            result["valid"] = False
        result["issues"].extend(deploy_result.get("issues", []))
        result["warnings"].extend(deploy_result.get("warnings", []))

    if "runbook" in sections_result.get("found", []):
        runbook_result = check_runbook_content(content)
        result["details"]["runbook"] = runbook_result
        result["warnings"].extend(runbook_result.get("warnings", []))

    if "rollback" in sections_result.get("found", []):
        rollback_result = check_rollback_content(content)
        result["details"]["rollback"] = rollback_result
        if not rollback_result["valid"]:
            result["valid"] = False
        result["issues"].extend(rollback_result.get("issues", []))
        result["warnings"].extend(rollback_result.get("warnings", []))

    if "monitoring" in sections_result.get("found", []):
        monitoring_result = check_monitoring_content(content)
        result["details"]["monitoring"] = monitoring_result
        result["warnings"].extend(monitoring_result.get("warnings", []))

    return result


def validate(project_root: Path, opnote_path: str = None) -> Dict[str, Any]:
    """Main validation function."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "opnotes": []
    }

    if opnote_path:
        # Validate specific OP-NOTE
        path = Path(opnote_path)
        if not path.is_absolute():
            path = project_root / path

        if not path.exists():
            result["valid"] = False
            result["failed"] += 1
            result["issues"].append({
                "severity": "error",
                "message": f"OP-NOTE not found: {opnote_path}"
            })
            return result

        opnote_result = validate_opnote(path)
        result["opnotes"].append(opnote_result)

        if opnote_result["valid"]:
            result["passed"] += 1
        else:
            result["valid"] = False
            result["failed"] += 1

        result["issues"].extend(opnote_result.get("issues", []))
        result["warnings"].extend(opnote_result.get("warnings", []))

    else:
        # Find and validate all OP-NOTEs
        opnotes = find_opnotes(project_root)

        if not opnotes:
            result["warnings"].append({
                "message": "No OP-NOTEs found in docs/op-notes/"
            })
            return result

        for opnote in opnotes:
            opnote_result = validate_opnote(opnote)
            result["opnotes"].append(opnote_result)

            if opnote_result["valid"]:
                result["passed"] += 1
            else:
                result["valid"] = False
                result["failed"] += 1

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate OP-NOTE documents")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--path", "-p", help="Path to specific OP-NOTE to validate")
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    result = validate(project_root, args.path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nOP-NOTE Validation")
        print("=" * 50)

        if result["opnotes"]:
            for opnote in result["opnotes"]:
                status = "PASS" if opnote["valid"] else "FAIL"
                print(f"\n{opnote['file']}: {status}")

                sections = opnote.get("details", {}).get("sections", {})
                if sections.get("found"):
                    print(f"  Sections found: {', '.join(sections['found'])}")
                if sections.get("missing"):
                    print(f"  Sections missing: {', '.join(sections['missing'])}")

        if result["issues"]:
            print(f"\nIssues:")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue['message']}")

        if result["warnings"]:
            print(f"\nWarnings:")
            for warning in result["warnings"][:10]:
                print(f"  [WARN] {warning['message']}")

        print(f"\nPassed: {result['passed']}, Failed: {result['failed']}")
        status = "PASSED" if result["valid"] else "FAILED"
        print(f"Result: {status}")

    import sys
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
