#!/usr/bin/env python3
"""
VibeFlow Track Detection Script

Detects the current workflow state and suggests the appropriate track.

Usage:
    python detect_track.py [--project-root PATH] [--json]

Exit codes:
    0 - Detection successful
    1 - Error during detection
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


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


def find_project_root() -> Path:
    """Find the project root by looking for docs/ directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "docs").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def detect_artifacts(project_root: Path) -> Dict[str, Any]:
    """Detect which artifacts exist in the project."""
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
    adr_files = list(adrs_path.glob("adr-*.md")) if adrs_path.exists() else []
    artifacts["adrs"] = {
        "exists": len(adr_files) > 0,
        "count": len(adr_files),
        "files": [str(f.relative_to(project_root)) for f in adr_files[:5]]
    }

    # Check Feature Specs
    features_path = docs_path / "features"
    feature_files = [f for f in features_path.glob("ft-*.md") if f.name != "schedule.md"] if features_path.exists() else []
    artifacts["features"] = {
        "exists": len(feature_files) > 0,
        "count": len(feature_files),
        "files": [str(f.relative_to(project_root)) for f in feature_files[:5]]
    }

    # Check OP-NOTEs
    opnotes_path = docs_path / "op-notes"
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
            "Run: /vibeflow-planning to create PRD"
        ]
    elif stage == "B":
        guidance = [
            "Perform codebase discovery before designing",
            "Create docs/discovery/disco-<ID>.md",
            "Complete all 5 phases: Spec Discovery, Validation, Test Impact, Dependencies, Reusable Components",
            "Run: /vibeflow-planning to create discovery doc"
        ]
    elif stage == "C":
        guidance = [
            "Update existing specs or create new ones",
            "Include: Architecture diagram, Component inventory, Interfaces",
            "Check docs/specs/index.md first",
            "Run: /vibeflow-planning to update specs"
        ]
    elif stage == "D":
        guidance = [
            "Create ADRs for non-trivial decisions",
            "Include: Context, Decision, Consequences, Alternatives, Rollback",
            "Run: /vibeflow-planning to create ADRs",
            "After completion: /vibeflow-validate checkpoint 1"
        ]
    elif stage == "E":
        guidance = [
            "Create Feature Spec at docs/features/ft-<ID>-<slug>.md",
            "Include: API Design with exact signatures, Acceptance Criteria",
            "Run: /vibeflow-feature-spec to create feature",
            "After completion: /vibeflow-validate checkpoint 2"
        ]
    elif stage == "F":
        guidance = [
            "Create implementation stubs from Feature Spec API Design",
            "Write failing unit tests (RED phase)",
            "Ensure tests fail with NotImplementedError",
            "Run: /vibeflow-tdd-implementation to begin TDD",
            "After completion: /vibeflow-validate checkpoint 3"
        ]
    elif stage == "G":
        guidance = [
            "Implement minimal code to pass tests (GREEN phase)",
            "Do not change contracts without updating specs first",
            "Run: /vibeflow-tdd-implementation"
        ]
    elif stage == "H":
        guidance = [
            "Write integration tests for I/O boundaries",
            "Refactor while keeping tests green",
            "Complete Stage H.4 quality validation",
            "Run: /vibeflow-tdd-implementation",
            "After completion: /vibeflow-validate checkpoint 4"
        ]
    elif stage == "I":
        guidance = [
            "Reconcile specs with actual implementation",
            "Update specs if implementation deviated",
            "Add Post-Implementation Notes to discovery doc",
            "Run: /vibeflow-release"
        ]
    elif stage == "J":
        guidance = [
            "Create OP-NOTE at docs/op-notes/op-<ID>-<slug>.md",
            "Include: Preflight, Deploy Steps, Monitoring, Rollback",
            "Run: /vibeflow-release to create OP-NOTE",
            "After completion: /vibeflow-validate checkpoint 5"
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
            "After completion: /vibeflow-validate checkpoint 6"
        ]

    return guidance


def main():
    parser = argparse.ArgumentParser(description="Detect VibeFlow workflow state")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Find project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = find_project_root()

    # Detect artifacts
    artifacts = detect_artifacts(project_root)

    # Detect current stage
    current_stage, next_stage = detect_current_stage(artifacts)

    # Suggest track
    suggested_track = suggest_track(artifacts)

    # Get guidance
    guidance = get_stage_guidance(next_stage, suggested_track)

    result = {
        "project_root": str(project_root),
        "detected_at": datetime.now().isoformat(),
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
        print(f"VibeFlow Workflow Status")
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
