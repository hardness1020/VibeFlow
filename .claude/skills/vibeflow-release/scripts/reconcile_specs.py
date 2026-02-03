#!/usr/bin/env python3
"""
Spec Reconciliation Script

Checks for potential divergence between specs and implementation.

Usage:
    python reconcile_specs.py [--feature-id <ID>] [--json]

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
from datetime import datetime


def find_feature_specs(project_root: Path, feature_id: str = None) -> List[Path]:
    """Find feature spec files."""
    features_dir = project_root / "docs" / "features"

    if not features_dir.exists():
        return []

    if feature_id:
        # Find specific feature
        pattern = f"*{feature_id}*.md"
        return list(features_dir.glob(pattern))

    # Find all feature specs
    return [f for f in features_dir.glob("ft-*.md") if f.name != "index.md"]


def find_specs(project_root: Path) -> List[Path]:
    """Find SPEC documents."""
    specs_dir = project_root / "docs" / "specs"

    if not specs_dir.exists():
        return []

    return [f for f in specs_dir.glob("spec-*.md") if f.name != "index.md"]


def find_adrs(project_root: Path) -> List[Path]:
    """Find ADR documents."""
    adrs_dir = project_root / "docs" / "adrs"

    if not adrs_dir.exists():
        return []

    return [f for f in adrs_dir.glob("adr-*.md") if f.name != "index.md"]


def extract_api_signatures(content: str) -> List[Dict[str, str]]:
    """Extract function signatures from API Design section."""
    signatures = []

    # Find API Design section
    api_match = re.search(
        r"##\s*(?:\d+\.\s*)?API Design(.*?)(?=##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if not api_match:
        return signatures

    api_content = api_match.group(1)

    # Extract Python function signatures
    python_sigs = re.findall(
        r"(?:def|async def)\s+(\w+)\s*\(([^)]*)\)\s*(?:->([^:\n]+))?",
        api_content
    )

    for match in python_sigs:
        signatures.append({
            "name": match[0],
            "params": match[1].strip(),
            "return_type": match[2].strip() if match[2] else "None",
            "language": "python"
        })

    # Extract TypeScript signatures
    ts_sigs = re.findall(
        r"(?:function|async function)\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^\n{]+)",
        api_content
    )

    for match in ts_sigs:
        signatures.append({
            "name": match[0],
            "params": match[1].strip(),
            "return_type": match[2].strip(),
            "language": "typescript"
        })

    return signatures


def find_implementation_signatures(project_root: Path, spec_signatures: List[Dict]) -> Dict[str, Any]:
    """Find matching signatures in implementation code."""
    result = {"found": [], "missing": [], "potentially_changed": []}

    if not spec_signatures:
        return result

    # Search in Python files
    for py_file in project_root.glob("**/*.py"):
        if "__pycache__" in str(py_file) or "test" in py_file.name.lower():
            continue

        try:
            content = py_file.read_text()

            for sig in spec_signatures:
                if sig["language"] != "python":
                    continue

                # Look for function definition
                pattern = rf"(?:def|async def)\s+{re.escape(sig['name'])}\s*\("
                if re.search(pattern, content):
                    # Check if signature matches
                    full_pattern = rf"(?:def|async def)\s+{re.escape(sig['name'])}\s*\(([^)]*)\)"
                    match = re.search(full_pattern, content)
                    if match:
                        impl_params = match.group(1).strip()
                        if sig["name"] not in [f["name"] for f in result["found"]]:
                            if impl_params != sig["params"]:
                                result["potentially_changed"].append({
                                    "name": sig["name"],
                                    "spec_params": sig["params"],
                                    "impl_params": impl_params,
                                    "file": str(py_file.relative_to(project_root))
                                })
                            else:
                                result["found"].append({
                                    "name": sig["name"],
                                    "file": str(py_file.relative_to(project_root))
                                })
        except Exception:
            pass

    # Check for missing implementations
    found_names = [f["name"] for f in result["found"]] + [f["name"] for f in result["potentially_changed"]]
    for sig in spec_signatures:
        if sig["name"] not in found_names:
            result["missing"].append(sig)

    return result


def check_spec_versions(specs: List[Path]) -> Dict[str, Any]:
    """Check SPEC document versions and last update dates."""
    result = {"specs": [], "warnings": []}

    for spec in specs:
        try:
            content = spec.read_text()

            spec_info = {"file": spec.name}

            # Extract version
            version_match = re.search(r"(?:version|v)[\s:]*(\d+\.\d+(?:\.\d+)?)", content, re.IGNORECASE)
            if version_match:
                spec_info["version"] = version_match.group(1)

            # Extract last updated date
            date_match = re.search(r"(?:last updated|updated|date)[\s:]*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)
            if date_match:
                spec_info["last_updated"] = date_match.group(1)

                # Check if stale (more than 90 days old)
                try:
                    update_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    days_old = (datetime.now() - update_date).days
                    if days_old > 90:
                        result["warnings"].append({
                            "message": f"{spec.name} last updated {days_old} days ago - verify still accurate"
                        })
                except ValueError:
                    pass

            result["specs"].append(spec_info)
        except Exception:
            pass

    return result


def check_adr_status(adrs: List[Path]) -> Dict[str, Any]:
    """Check ADR statuses for any pending decisions."""
    result = {"adrs": [], "warnings": []}

    for adr in adrs:
        try:
            content = adr.read_text()

            adr_info = {"file": adr.name}

            # Extract status
            status_match = re.search(r"(?:status|state)[\s:]*(\w+)", content, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).lower()
                adr_info["status"] = status

                if status in ["proposed", "draft", "pending"]:
                    result["warnings"].append({
                        "message": f"{adr.name} has status '{status}' - should be 'Accepted' before release"
                    })

            result["adrs"].append(adr_info)
        except Exception:
            pass

    return result


def check_feature_completion(feature_spec: Path) -> Dict[str, Any]:
    """Check feature spec for completion indicators."""
    result = {"valid": True, "issues": [], "warnings": [], "details": {}}

    try:
        content = feature_spec.read_text()

        # Check for completion status
        if "status" in content.lower():
            status_match = re.search(r"(?:status|state)[\s:]*(\w+)", content, re.IGNORECASE)
            if status_match:
                result["details"]["status"] = status_match.group(1)

        # Check for implementation notes (G.1 updates)
        if "design changes" in content.lower() or "g.1" in content.lower():
            result["details"]["has_design_changes"] = True
            result["warnings"].append({
                "message": "Feature has design changes (G.1) - verify SPEC was updated"
            })

        # Check acceptance criteria have checkboxes
        ac_match = re.search(
            r"##\s*(?:\d+\.\s*)?Acceptance Criteria(.*?)(?=##|\Z)",
            content,
            re.IGNORECASE | re.DOTALL
        )

        if ac_match:
            ac_content = ac_match.group(1)
            checkboxes = re.findall(r"\[[ x]\]", ac_content)
            checked = len(re.findall(r"\[x\]", ac_content, re.IGNORECASE))
            total = len(checkboxes)

            result["details"]["acceptance_criteria"] = {
                "total": total,
                "checked": checked
            }

            if total > 0 and checked < total:
                result["warnings"].append({
                    "message": f"Only {checked}/{total} acceptance criteria marked complete"
                })

    except Exception as e:
        result["issues"].append({
            "severity": "error",
            "message": f"Cannot read feature spec: {e}"
        })
        result["valid"] = False

    return result


def validate(project_root: Path, feature_id: str = None) -> Dict[str, Any]:
    """Main validation function for spec reconciliation."""
    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "passed": 0,
        "failed": 0,
        "details": {}
    }

    # Find feature specs
    feature_specs = find_feature_specs(project_root, feature_id)
    result["details"]["feature_specs_found"] = len(feature_specs)

    if not feature_specs:
        if feature_id:
            result["issues"].append({
                "severity": "error",
                "message": f"Feature spec not found for ID: {feature_id}"
            })
            result["valid"] = False
            result["failed"] += 1
        else:
            result["warnings"].append({
                "message": "No feature specs found in docs/features/"
            })
        return result

    # Analyze each feature spec
    for feature_spec in feature_specs[:5]:  # Limit to 5 for performance
        feature_result = check_feature_completion(feature_spec)
        result["details"][feature_spec.name] = feature_result

        if not feature_result["valid"]:
            result["valid"] = False
            result["failed"] += 1
        else:
            result["passed"] += 1

        result["issues"].extend(feature_result.get("issues", []))
        result["warnings"].extend(feature_result.get("warnings", []))

        # Extract and check API signatures
        try:
            content = feature_spec.read_text()
            signatures = extract_api_signatures(content)

            if signatures:
                impl_result = find_implementation_signatures(project_root, signatures)
                result["details"][f"{feature_spec.name}_api"] = impl_result

                if impl_result["missing"]:
                    for missing in impl_result["missing"]:
                        result["warnings"].append({
                            "message": f"API function '{missing['name']}' from spec not found in implementation"
                        })

                if impl_result["potentially_changed"]:
                    for changed in impl_result["potentially_changed"]:
                        result["warnings"].append({
                            "message": f"API function '{changed['name']}' signature may have changed from spec"
                        })
        except Exception:
            pass

    # Check SPEC versions
    specs = find_specs(project_root)
    if specs:
        spec_result = check_spec_versions(specs)
        result["details"]["specs"] = spec_result
        result["warnings"].extend(spec_result.get("warnings", []))

    # Check ADR statuses
    adrs = find_adrs(project_root)
    if adrs:
        adr_result = check_adr_status(adrs)
        result["details"]["adrs"] = adr_result
        result["warnings"].extend(adr_result.get("warnings", []))

    # Add reconciliation reminder
    result["warnings"].append({
        "message": "Manually verify: implementation matches SPEC contracts"
    })
    result["warnings"].append({
        "message": "Manually verify: any design changes (G.1) are reflected in docs"
    })

    return result


def main():
    parser = argparse.ArgumentParser(description="Check spec reconciliation")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--feature-id", "-f", help="Specific feature ID to check")
    parser.add_argument("--project-root", "-p", help="Project root directory")

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    while project_root != project_root.parent:
        if (project_root / "docs").is_dir():
            break
        project_root = project_root.parent

    result = validate(project_root, args.feature_id)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nSpec Reconciliation Check")
        print("=" * 50)

        print(f"\nFeature specs found: {result['details'].get('feature_specs_found', 0)}")

        # Show API reconciliation details
        for key, value in result["details"].items():
            if key.endswith("_api") and isinstance(value, dict):
                feature = key.replace("_api", "")
                print(f"\n{feature} API:")
                print(f"  Found: {len(value.get('found', []))}")
                print(f"  Missing: {len(value.get('missing', []))}")
                print(f"  Changed: {len(value.get('potentially_changed', []))}")

        if result["issues"]:
            print(f"\nIssues:")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue['message']}")

        if result["warnings"]:
            print(f"\nWarnings:")
            for warning in result["warnings"][:15]:
                print(f"  [WARN] {warning['message']}")

        status = "PASSED" if result["valid"] else "FAILED"
        print(f"\nResult: {status}")

    import sys
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
