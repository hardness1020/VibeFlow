#!/usr/bin/env python3
"""
VibeFlow Track Detection Script

Detects the current workflow state and suggests the appropriate track.
Supports per-work-item detection and manifest verification.

Usage:
    python detect_track.py [--project-root PATH] [--json]
    python detect_track.py --workitem <ID> [--verify]
    python detect_track.py --all-workitems
    python detect_track.py --verify

Exit codes:
    0 - Detection successful
    1 - Error during detection
    2 - Verification found drift
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Track definitions
TRACKS = {
    "micro": {
        "name": "Micro",
        "stages": ["F", "G"],
        "description": "Bug fix, typo, small refactor",
        "examples": ["Fix typo in error message", "Update config value", "Minor refactor"]
    },
    "small": {
        "name": "Small",
        "stages": ["E", "F", "G", "H"],
        "description": "Single feature, no contracts",
        "examples": ["Add form field", "UI polish", "Simple validation"]
    },
    "medium": {
        "name": "Medium",
        "stages": ["B", "C", "D", "E", "F", "G", "H", "I", "J"],
        "description": "Multi-component, no new services",
        "examples": ["New API endpoint", "Database migration", "Cross-component feature"]
    },
    "large": {
        "name": "Large",
        "stages": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"],
        "description": "System change, new contracts/services",
        "examples": ["New LLM integration", "New auth system", "New service"]
    }
}

# Stage definitions
STAGES = {
    "A": {"name": "Initiate", "artifact": "PRD", "path": "docs/prds/prd.md"},
    "B": {"name": "Discovery", "artifact": "Discovery Doc", "path": "docs/discovery/disco-*.md"},
    "C": {"name": "Specify", "artifact": "Tech Specs", "path": "docs/specs/spec-*.md"},
    "D": {"name": "Decide", "artifact": "ADRs", "path": "docs/adrs/adr-*.md"},
    "E": {"name": "Plan", "artifact": "Feature Spec", "path": "docs/features/ft-*.md"},
    "F": {"name": "RED", "artifact": "Failing Tests", "path": "**/test_*.py"},
    "G": {"name": "GREEN", "artifact": "Passing Tests", "path": "tests passing"},
    "H": {"name": "REFACTOR", "artifact": "Integration Tests", "path": "**/test_*integration*.py"},
    "I": {"name": "Reconcile", "artifact": "Updated Specs", "path": "docs/specs/index.md"},
    "J": {"name": "Prepare", "artifact": "OP-NOTE", "path": "docs/op-notes/op-*.md"},
    "K": {"name": "Deploy", "artifact": "Deployment", "path": "deployment verified"},
    "L": {"name": "Close", "artifact": "Indices Updated", "path": "indices updated"}
}

# Stages that produce checkable file artifacts, mapped to their glob patterns
STAGE_ARTIFACT_PATTERNS = {
    "A": ["docs/prds/prd.md"],
    "B": ["docs/discovery/disco-{id}.md", "docs/discovery/disco-*.md"],
    "C": ["docs/specs/spec-*.md"],
    "D": ["docs/adrs/adr-*.md"],
    "E": ["docs/features/ft-{id}-*.md", "docs/features/ft-*.md"],
    "J": ["docs/op-notes/op-{id}-*.md", "docs/op-notes/op-*.md"],
}


def find_project_root() -> Path:
    """Find the project root by looking for docs/ directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "docs").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def load_manifest(project_root: Path) -> Optional[Dict[str, Any]]:
    """Load the workflow state manifest from docs/workflow-state.yaml."""
    manifest_path = project_root / "docs" / "workflow-state.yaml"
    if not manifest_path.exists():
        return None

    if HAS_YAML:
        with open(manifest_path) as f:
            return yaml.safe_load(f) or {}
    else:
        # Simple YAML parsing fallback for basic key-value structure
        return _parse_simple_yaml(manifest_path)


def _parse_simple_yaml(path: Path) -> Dict[str, Any]:
    """Basic YAML parser for the manifest format (no external dependency).

    Parses the workitems format:
      workitems:
        slug-key:                    (2-space indent)
          id: 030                    (4-space indent)
          description: "..."         (4-space indent)
          track: medium              (4-space indent)
          stage: G                   (4-space indent)
          started: 2025-02-20       (4-space indent)
          checkpoint: 3              (4-space indent)
          docs:                      (4-space indent)
            prd: docs/prds/prd.md    (6-space indent)
            discovery: ...           (6-space indent)
            specs:                   (6-space indent)
              - docs/specs/spec.md   (8-space indent, list item)
            adrs:                    (6-space indent)
              - docs/adrs/adr.md     (8-space indent, list item)
            feature: ...             (6-space indent)
            opnote: null             (6-space indent)
    """
    result = {"workitems": {}}
    current_workitem = None
    in_docs = False
    current_docs_field = None
    with open(path) as f:
        for line in f:
            stripped = line.rstrip()
            if stripped.startswith("#") or not stripped:
                continue
            # Work item entry line (2-space indent, ends with colon)
            if re.match(r"^  ([a-z][\w-]+):$", stripped):
                current_workitem = stripped.strip().rstrip(":")
                result["workitems"][current_workitem] = {"docs": {}}
                in_docs = False
                current_docs_field = None
            # docs: sub-hierarchy start (4-space indent)
            elif current_workitem and re.match(r"^    docs:$", stripped):
                in_docs = True
                current_docs_field = None
            # docs sub-field (6-space indent)
            elif current_workitem and in_docs and re.match(r"^      \w+:", stripped):
                key, _, value = stripped.strip().partition(":")
                value = value.strip()
                # Strip inline comments
                if "#" in value:
                    value = value[:value.index("#")].strip()
                if not value or value == "":
                    # List field (e.g., specs:, adrs:) — initialize empty list
                    result["workitems"][current_workitem]["docs"][key] = []
                    current_docs_field = key
                elif value == "null":
                    result["workitems"][current_workitem]["docs"][key] = None
                    current_docs_field = None
                else:
                    result["workitems"][current_workitem]["docs"][key] = value
                    current_docs_field = None
            # docs list item (8-space indent, starts with -)
            elif current_workitem and in_docs and current_docs_field and re.match(r"^        - ", stripped):
                item = stripped.strip().lstrip("- ").strip()
                result["workitems"][current_workitem]["docs"][current_docs_field].append(item)
            # Regular field line (4-space indent, not docs:)
            elif current_workitem and re.match(r"^    \w+:", stripped) and not in_docs:
                key, _, value = stripped.strip().partition(":")
                value = value.strip()
                # Strip inline comments
                if "#" in value:
                    value = value[:value.index("#")].strip()
                # Strip quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                # Try to parse as int
                try:
                    value = int(value)
                except ValueError:
                    pass
                result["workitems"][current_workitem][key] = value
            # Non-docs field at 4-space indent resets docs context
            elif current_workitem and re.match(r"^    \w+:", stripped) and in_docs:
                in_docs = False
                current_docs_field = None
                key, _, value = stripped.strip().partition(":")
                value = value.strip()
                if "#" in value:
                    value = value[:value.index("#")].strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                try:
                    value = int(value)
                except ValueError:
                    pass
                result["workitems"][current_workitem][key] = value
    return result


def detect_artifacts(project_root: Path, feature_id: Optional[str] = None) -> Dict[str, Any]:
    """Detect which artifacts exist in the project.

    If feature_id is provided, only look for artifacts matching that feature.
    """
    docs_path = project_root / "docs"
    artifacts = {}

    # Check PRD
    prd_path = docs_path / "prds" / "prd.md"
    artifacts["prd"] = {
        "exists": prd_path.exists(),
        "path": str(prd_path.relative_to(project_root)) if prd_path.exists() else None
    }

    # Check Discovery docs
    disco_path = docs_path / "discovery"
    if feature_id:
        disco_files = list(disco_path.glob(f"disco-{feature_id}*.md")) if disco_path.exists() else []
    else:
        disco_files = list(disco_path.glob("disco-*.md")) if disco_path.exists() else []
    artifacts["discovery"] = {
        "exists": len(disco_files) > 0,
        "count": len(disco_files),
        "files": [str(f.relative_to(project_root)) for f in disco_files[:5]]
    }

    # Check Tech Specs
    specs_path = docs_path / "specs"
    spec_files = [f for f in specs_path.glob("spec-*.md") if f.name != "index.md"] if specs_path.exists() else []
    artifacts["specs"] = {
        "exists": len(spec_files) > 0,
        "count": len(spec_files),
        "files": [str(f.relative_to(project_root)) for f in spec_files[:5]]
    }

    # Check ADRs
    adrs_path = docs_path / "adrs"
    if feature_id:
        adr_files = list(adrs_path.glob(f"adr-{feature_id}*.md")) if adrs_path.exists() else []
    else:
        adr_files = list(adrs_path.glob("adr-*.md")) if adrs_path.exists() else []
    artifacts["adrs"] = {
        "exists": len(adr_files) > 0,
        "count": len(adr_files),
        "files": [str(f.relative_to(project_root)) for f in adr_files[:5]]
    }

    # Check Feature Specs
    features_path = docs_path / "features"
    if feature_id:
        feature_files = list(features_path.glob(f"ft-{feature_id}-*.md")) if features_path.exists() else []
    else:
        feature_files = [f for f in features_path.glob("ft-*.md") if f.name != "schedule.md"] if features_path.exists() else []
    artifacts["features"] = {
        "exists": len(feature_files) > 0,
        "count": len(feature_files),
        "files": [str(f.relative_to(project_root)) for f in feature_files[:5]]
    }

    # Check OP-NOTEs
    opnotes_path = docs_path / "op-notes"
    if feature_id:
        opnote_files = list(opnotes_path.glob(f"op-{feature_id}*.md")) if opnotes_path.exists() else []
    else:
        opnote_files = [f for f in opnotes_path.glob("op-*.md") if f.name != "index.md"] if opnotes_path.exists() else []
    artifacts["opnotes"] = {
        "exists": len(opnote_files) > 0,
        "count": len(opnote_files),
        "files": [str(f.relative_to(project_root)) for f in opnote_files[:5]]
    }

    # Check test files
    test_patterns = ["**/test_*.py", "**/tests/**/*.py", "**/*_test.py"]
    test_files = []
    for pattern in test_patterns:
        test_files.extend(project_root.glob(pattern))
    test_files = [f for f in test_files if "__pycache__" not in str(f)]
    artifacts["tests"] = {
        "exists": len(test_files) > 0,
        "count": len(test_files),
        "sample": [str(f.relative_to(project_root)) for f in list(set(test_files))[:5]]
    }

    return artifacts


def detect_current_stage(artifacts: Dict[str, Any]) -> Tuple[str, str]:
    """
    Detect the current stage based on artifacts.

    Returns tuple of (current_stage, next_stage)
    """
    # Work backwards from most advanced stage

    if artifacts["opnotes"]["exists"]:
        # Has OP-NOTE, check if deployed
        return ("J", "K")  # Ready for deployment

    if artifacts["tests"]["exists"]:
        # Has tests, check status
        # Would need to run tests to determine F vs G vs H
        # For now, assume implementation phase
        return ("G", "H")

    if artifacts["features"]["exists"]:
        # Has feature spec, ready for TDD
        return ("E", "F")

    if artifacts["adrs"]["exists"]:
        # Has ADRs, may need feature spec
        return ("D", "E")

    if artifacts["specs"]["exists"]:
        # Has specs, may need ADRs
        return ("C", "D")

    if artifacts["discovery"]["exists"]:
        # Has discovery, may need specs
        return ("B", "C")

    if artifacts["prd"]["exists"]:
        # Has PRD, may need discovery
        return ("A", "B")

    # No artifacts, start from beginning
    return ("none", "A")


def suggest_track(artifacts: Dict[str, Any]) -> str:
    """Suggest the appropriate track based on artifact presence."""
    # If PRD exists or being modified, likely Large
    if artifacts["prd"]["exists"]:
        if artifacts["discovery"]["exists"]:
            return "large"
        return "medium"

    # If discovery exists, at least Medium
    if artifacts["discovery"]["exists"]:
        return "medium"

    # If only feature specs and tests
    if artifacts["features"]["exists"]:
        return "small"

    # Default to micro for simple changes
    return "micro"


def get_stage_guidance(stage: str, track: str) -> List[str]:
    """Get guidance for the current stage."""
    guidance = []

    stage_info = STAGES.get(stage, {})
    stage_name = stage_info.get("name", "Unknown")

    if stage == "A":
        guidance = [
            "Create or update the PRD at docs/prds/prd.md",
            "Include: Summary, Problem, Users, Scope (MoSCoW), Success Metrics",
            "Run: /plan to create PRD"
        ]
    elif stage == "B":
        guidance = [
            "Perform codebase discovery before designing",
            "Create docs/discovery/disco-<ID>.md",
            "Complete all 5 phases: Spec Discovery, Validation, Test Impact, Dependencies, Reusable Components",
            "Run: /plan to create discovery doc"
        ]
    elif stage == "C":
        guidance = [
            "Update existing specs or create new ones",
            "Include: Architecture diagram, Component inventory, Interfaces",
            "Check docs/specs/index.md first",
            "Run: /plan to update specs"
        ]
    elif stage == "D":
        guidance = [
            "Create ADRs for non-trivial decisions",
            "Include: Context, Decision, Consequences, Alternatives, Rollback",
            "Run: /plan to create ADRs",
            "After completion: /validate checkpoint 1"
        ]
    elif stage == "E":
        guidance = [
            "Create Feature Spec at docs/features/ft-<ID>-<slug>.md",
            "Include: API Design with exact signatures, Acceptance Criteria",
            "Run: /spec to create feature",
            "After completion: /validate checkpoint 2"
        ]
    elif stage == "F":
        guidance = [
            "Create implementation stubs from Feature Spec API Design",
            "Write failing unit tests (RED phase)",
            "Ensure tests fail with NotImplementedError",
            "Run: /tdd to begin TDD",
            "After completion: /validate checkpoint 3"
        ]
    elif stage == "G":
        guidance = [
            "Implement minimal code to pass tests (GREEN phase)",
            "Do not change contracts without updating specs first",
            "Run: /tdd"
        ]
    elif stage == "H":
        guidance = [
            "Write integration tests for I/O boundaries",
            "Refactor while keeping tests green",
            "Complete Stage H.4 quality validation",
            "Run: /tdd",
            "After completion: /validate checkpoint 4"
        ]
    elif stage == "I":
        guidance = [
            "Reconcile specs with actual implementation",
            "Update specs if implementation deviated",
            "Add Post-Implementation Notes to discovery doc",
            "Run: /release"
        ]
    elif stage == "J":
        guidance = [
            "Create OP-NOTE at docs/op-notes/op-<ID>-<slug>.md",
            "Include: Preflight, Deploy Steps, Monitoring, Rollback",
            "Run: /release to create OP-NOTE",
            "After completion: /validate checkpoint 5"
        ]
    elif stage == "K":
        guidance = [
            "Follow OP-NOTE deployment steps",
            "Verify post-deploy checks pass",
            "Monitor dashboards and alerts"
        ]
    elif stage == "L":
        guidance = [
            "Update docs/specs/index.md with Current version",
            "Update docs/features/schedule.md to Done",
            "Tag release in Git",
            "Close issues with 'Closes #<ID>'",
            "After completion: /validate checkpoint 6"
        ]

    return guidance


def verify_workitem(project_root: Path, workitem_key: str, workitem_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verify a single work item's manifest state against actual artifacts.

    Returns a dict with verification results.
    """
    # Extract the numeric ID from the id field
    workitem_id = str(workitem_data.get("id", ""))

    manifest_stage = workitem_data.get("stage", "?")
    manifest_track = workitem_data.get("track", "?")

    # Detect actual artifacts for this work item
    artifacts = detect_artifacts(project_root, feature_id=workitem_id if workitem_id else None)
    detected_stage, _ = detect_current_stage(artifacts)

    # Compare manifest vs detected
    issues = []
    if detected_stage == "none" and manifest_stage not in ("A", "none"):
        issues.append(f"Manifest says stage {manifest_stage} but no artifacts found")

    # Check if manifest stage is ahead of what artifacts support
    stage_order = list("ABCDEFGHIJKL")
    if manifest_stage in stage_order and detected_stage in stage_order:
        manifest_idx = stage_order.index(manifest_stage)
        detected_idx = stage_order.index(detected_stage)
        if manifest_idx > detected_idx + 1:
            issues.append(
                f"Manifest stage {manifest_stage} is ahead of detected artifacts (stage {detected_stage})"
            )

    # Validate track is valid
    if manifest_track not in TRACKS:
        issues.append(f"Invalid track '{manifest_track}' (must be micro/small/medium/large)")

    # Validate stage is in track's stage list
    if manifest_track in TRACKS and manifest_stage in stage_order:
        track_stages = TRACKS[manifest_track]["stages"]
        if manifest_stage not in track_stages:
            issues.append(
                f"Stage {manifest_stage} is not part of the {manifest_track} track "
                f"(valid stages: {', '.join(track_stages)})"
            )

    # Optionally check that docs paths actually exist on disk
    docs = workitem_data.get("docs", {})
    if docs:
        for doc_key in ("prd", "discovery", "feature", "opnote"):
            doc_path = docs.get(doc_key)
            if doc_path and doc_path != "null":
                full_path = project_root / doc_path
                if not full_path.exists():
                    issues.append(f"docs.{doc_key} path does not exist: {doc_path}")
        for doc_key in ("specs", "adrs"):
            doc_list = docs.get(doc_key, [])
            if isinstance(doc_list, list):
                for doc_path in doc_list:
                    full_path = project_root / doc_path
                    if not full_path.exists():
                        issues.append(f"docs.{doc_key} path does not exist: {doc_path}")

    return {
        "workitem": workitem_key,
        "manifest_stage": manifest_stage,
        "manifest_track": manifest_track,
        "detected_stage": detected_stage,
        "issues": issues,
        "ok": len(issues) == 0,
        "artifacts": artifacts,
    }


def run_verify(project_root: Path, workitem_id: Optional[str] = None) -> Dict[str, Any]:
    """Cross-check manifest against actual artifacts.

    If workitem_id is provided, verify only that work item.
    Otherwise verify all work items in the manifest.
    """
    manifest = load_manifest(project_root)
    if manifest is None:
        return {
            "ok": False,
            "error": "No manifest found at docs/workflow-state.yaml",
            "workitems": {}
        }

    workitems = manifest.get("workitems", {})
    if not workitems:
        return {
            "ok": True,
            "warning": "Manifest exists but has no work items registered",
            "workitems": {}
        }

    results = {}
    all_ok = True

    for workitem_key, workitem_data in workitems.items():
        # If filtering by workitem_id, skip non-matching work items
        if workitem_id:
            item_id = str((workitem_data or {}).get("id", ""))
            if item_id != workitem_id:
                continue

        result = verify_workitem(project_root, workitem_key, workitem_data or {})
        results[workitem_key] = result
        if not result["ok"]:
            all_ok = False

    return {
        "ok": all_ok,
        "workitems": results
    }


def run_all_workitems(project_root: Path) -> Dict[str, Any]:
    """Detect state for all registered work items in the manifest."""
    manifest = load_manifest(project_root)
    if manifest is None:
        return {
            "error": "No manifest found at docs/workflow-state.yaml",
            "workitems": {}
        }

    workitems = manifest.get("workitems", {})
    results = {}

    for workitem_key, workitem_data in workitems.items():
        wid = str((workitem_data or {}).get("id", ""))
        artifacts = detect_artifacts(project_root, feature_id=wid if wid else None)
        detected_stage, next_stage = detect_current_stage(artifacts)
        results[workitem_key] = {
            "id": wid,
            "manifest_stage": (workitem_data or {}).get("stage", "?"),
            "manifest_track": (workitem_data or {}).get("track", "?"),
            "detected_stage": detected_stage,
            "next_stage": next_stage,
            "artifacts": artifacts,
        }

    return {"workitems": results}


def main():
    parser = argparse.ArgumentParser(description="Detect VibeFlow workflow state")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--workitem", "-w", help="Work item ID for per-work-item detection (e.g., 030)")
    # Keep --feature as hidden alias for backwards compatibility
    parser.add_argument("--feature", "-f", help=argparse.SUPPRESS)
    parser.add_argument("--verify", "-v", action="store_true",
                        help="Cross-check manifest against actual artifacts")
    parser.add_argument("--all-workitems", "-a", action="store_true",
                        help="Detect state for all registered work items")
    # Keep --all-features as hidden alias
    parser.add_argument("--all-features", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Support --feature as alias for --workitem
    workitem_id = args.workitem or args.feature
    all_workitems = args.all_workitems or args.all_features

    # Find project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = find_project_root()

    # --- Verify mode ---
    if args.verify:
        verify_result = run_verify(project_root, workitem_id=workitem_id)
        if args.json:
            print(json.dumps(verify_result, indent=2, default=str))
        else:
            if "error" in verify_result:
                print(f"\nError: {verify_result['error']}")
                raise SystemExit(1)

            print(f"\n{'='*60}")
            print("VibeFlow Manifest Verification")
            print(f"{'='*60}")

            if not verify_result["workitems"]:
                print("\nNo work items to verify.")
                if workitem_id:
                    print(f"  Work item ID '{workitem_id}' not found in manifest.")
                return

            for wkey, wresult in verify_result["workitems"].items():
                status = "OK" if wresult["ok"] else "DRIFT"
                print(f"\n  [{status}] {wkey}")
                print(f"    Manifest stage: {wresult['manifest_stage']}, "
                      f"Detected: {wresult['detected_stage']}")
                if wresult["issues"]:
                    for issue in wresult["issues"]:
                        print(f"    ! {issue}")

            overall = "PASS" if verify_result["ok"] else "DRIFT DETECTED"
            print(f"\nOverall: {overall}")

        if not verify_result["ok"]:
            raise SystemExit(2)
        return

    # --- All work items mode ---
    if all_workitems:
        all_result = run_all_workitems(project_root)
        if args.json:
            print(json.dumps(all_result, indent=2, default=str))
        else:
            if "error" in all_result:
                print(f"\nError: {all_result['error']}")
                raise SystemExit(1)

            print(f"\n{'='*60}")
            print("VibeFlow All Work Items Status")
            print(f"{'='*60}")

            for wkey, wdata in all_result["workitems"].items():
                print(f"\n  {wkey} (id: {wdata['id']})")
                print(f"    Track: {wdata['manifest_track']}, "
                      f"Manifest stage: {wdata['manifest_stage']}, "
                      f"Detected: {wdata['detected_stage']}")
        return

    # --- Standard detection (global or per-work-item) ---
    artifacts = detect_artifacts(project_root, feature_id=workitem_id)

    # Detect current stage
    current_stage, next_stage = detect_current_stage(artifacts)

    # Suggest track
    suggested_track = suggest_track(artifacts)

    # Get guidance
    guidance = get_stage_guidance(next_stage, suggested_track)

    result = {
        "project_root": str(project_root),
        "detected_at": datetime.now().isoformat(),
        "workitem_id": workitem_id,
        "current_stage": current_stage,
        "next_stage": next_stage,
        "suggested_track": suggested_track,
        "track_info": TRACKS[suggested_track],
        "stage_info": STAGES.get(next_stage, {}),
        "guidance": guidance,
        "artifacts": artifacts
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        title = "VibeFlow Workflow Status"
        if workitem_id:
            title += f" (Work Item: {workitem_id})"
        print(title)
        print(f"{'='*60}")
        print(f"\nProject: {project_root}")
        print(f"\nCurrent Stage: {current_stage} ({STAGES.get(current_stage, {}).get('name', 'Not started')})")
        print(f"Next Stage: {next_stage} ({STAGES.get(next_stage, {}).get('name', 'Unknown')})")
        print(f"\nSuggested Track: {TRACKS[suggested_track]['name']}")
        print(f"  Description: {TRACKS[suggested_track]['description']}")
        print(f"  Stages: {' → '.join(TRACKS[suggested_track]['stages'])}")

        print(f"\nArtifacts Found:")
        for name, info in artifacts.items():
            status = "✓" if info.get("exists") else "✗"
            count = f" ({info.get('count', 0)})" if info.get('count') else ""
            print(f"  [{status}] {name.capitalize()}{count}")

        print(f"\nNext Steps:")
        for i, step in enumerate(guidance, 1):
            print(f"  {i}. {step}")

        print()


if __name__ == "__main__":
    main()
