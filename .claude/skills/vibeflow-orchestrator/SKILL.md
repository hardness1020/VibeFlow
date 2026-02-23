---
name: vibeflow-orchestrator
description: Master workflow navigation and track selection for the VibeFlow docs-first development workflow
metadata:
  triggers:
    - start vibeflow
    - begin workflow
    - new feature
    - workflow status
    - where am I
    - what stage
    - what track
    - select track
    - register work item
    - advance work item
---

# vibeflow-orchestrator

Master workflow navigation and track selection for the VibeFlow docs-first development workflow.

## Purpose

This skill tracks multiple work items through the VibeFlow workflow by:
- Registering work items with their workflow track (Micro/Small/Medium/Large)
- Tracking each work item's current stage independently
- Advancing work items through stages and routing to the appropriate skill
- Providing a dashboard view of all in-flight work items

## Workflow

```
Register Work Item
    │
    ├── Assign ID, generate slug from description, and assign track
    ├── Create entry in docs/workflow-state.yaml
    └── Determine starting stage from track
    │
    ▼
Track Progress
    │
    ├── Show status dashboard (all work items)
    ├── Show detailed status (single work item)
    └── Cross-check manifest against artifacts
    │
    ▼
Advance & Route
    │
    ├── Mark work item as advancing to next stage
    ├── Recommend the appropriate skill command
    └── Update manifest with new stage
```

## Usage

### Register a New Work Item

```
/vibeflow-orchestrator register "<description>" <ID> <track>
```

Registers a work item in `docs/workflow-state.yaml` and determines the starting stage. Claude generates the kebab-case slug from the description.

Example:
```
/vibeflow-orchestrator register "Add anti-hallucination guardrails" 030 medium
/vibeflow-orchestrator register "Export data to CSV" 031 small
```

### Status Dashboard

```
/vibeflow-orchestrator status
```

Shows all registered work items with their current stage, track, and last checkpoint.

Example output:
```
Work Item                          Track    Stage  Checkpoint  Started
add-anti-hallucination-guardrails  Medium   G      3           2025-02-20
export-data-to-csv                 Small    E      2           2025-02-22
```

### Detailed Work Item Status

```
/vibeflow-orchestrator status <ID>
```

Shows detailed status for one work item including:
- Current stage and description
- Completed and remaining stages for its track
- Last checkpoint passed
- Artifact verification (cross-check with `detect_track.py --workitem <ID>`)

### Advance a Work Item

```
/vibeflow-orchestrator advance <ID>
```

Marks a work item as advancing to the next stage in its track:
- Updates `stage` in `docs/workflow-state.yaml`
- Updates `checkpoint` if a checkpoint boundary was crossed
- Updates `docs` with any new document paths produced
- Shows what the next stage requires

### Next Steps for a Work Item

```
/vibeflow-orchestrator next <ID>
```

Shows the recommended next action for a work item:
- What the current stage requires
- Which `/vibeflow-*` command to run
- Whether a checkpoint validation is needed first

## Workflow Tracks

| Track | Scope | Stages | Example |
|-------|-------|--------|---------|
| **Micro** | Bug fix, typo, small refactor | F → G | Fix typo, update config |
| **Small** | Single feature, no contracts | E → F → G → H | Add form field, UI polish |
| **Medium** | Multi-component, no new services | B → C → D → E → F → G → H → I → J | New API endpoint |
| **Large** | System change, new contracts/services | Full A → L | New LLM integration |

## Stage Overview

### Planning Stages (A-D)
- **A — Initiate**: Create/update PRD
- **B — Discovery**: Analyze codebase (Medium/Large)
- **C — Specify**: Create/update Tech Specs
- **D — Decide**: Create ADRs for decisions

**Checkpoint #1: Planning Complete**

### Design Stage (E)
- **E — Plan**: Create Feature Spec with API Design

**Checkpoint #2: Design Complete**

### Implementation Stages (F-H)
- **F — RED**: Write failing unit tests + stubs
- **G — GREEN**: Implement to pass tests
- **H — REFACTOR**: Integration tests + quality validation

**Checkpoint #3: Tests Complete** (after F)
**Checkpoint #4: Implementation Complete** (after H)

### Release Stages (I-L)
- **I — Reconcile**: Update specs if implementation deviated
- **J — Prepare**: Write OP-NOTE
- **K — Deploy**: Follow OP-NOTE, verify
- **L — Close**: Update indices, tag release

**Checkpoint #5: Release Ready** (after J)
**Checkpoint #6: Deployed** (after L)

## Manifest Format

The manifest file `docs/workflow-state.yaml` is the single source of truth for work item lifecycle state:

```yaml
workitems:
  add-anti-hallucination-guardrails:
    id: 030
    description: "Add anti-hallucination guardrails"
    track: medium        # micro | small | medium | large
    stage: G             # current stage letter (A-L)
    started: 2025-02-20  # date work item was registered
    checkpoint: 3        # last checkpoint passed (1-6)
    docs:
      prd: docs/prds/prd.md
      discovery: docs/discovery/disco-030.md
      specs:
        - docs/specs/spec-llm.md
      adrs:
        - docs/adrs/adr-030-prompt-strategy.md
      feature: docs/features/ft-030-anti-hallucination.md
      opnote: null
  export-data-to-csv:
    id: 031
    description: "Export data to CSV"
    track: small
    stage: E
    started: 2025-02-22
    checkpoint: 2
    docs:
      prd: null
      discovery: null
      specs: []
      adrs: []
      feature: docs/features/ft-031-export-csv.md
      opnote: null
```

When registering a new work item:
1. Create `docs/workflow-state.yaml` if it doesn't exist (use `assets/workflow-state-template.yaml`)
2. Generate a kebab-case slug from the description (e.g., "Add anti-hallucination guardrails" → `add-anti-hallucination-guardrails`)
3. Add the work item entry with `id`, `description`, `track`, `stage` (first stage for the track), `started` (today), `checkpoint: 0`, and empty `docs` hierarchy

When advancing a work item:
1. Read `docs/workflow-state.yaml`
2. Update the `stage` field to the next stage in the track
3. Update `checkpoint` if a checkpoint boundary was crossed
4. Update `docs` with any document paths produced at the completed stage

## Skill Routing

Each stage maps to a specific skill. After determining the current stage for a work item, recommend the appropriate command:

| Stage | Skill | Recommended Command |
|-------|-------|--------------------|
| A | vibeflow-planning | `/vibeflow-planning prd` |
| B | vibeflow-planning | `/vibeflow-planning discovery <ID>` |
| C | vibeflow-planning | `/vibeflow-planning spec <name>` |
| D | vibeflow-planning | `/vibeflow-planning adr <ID> <slug>` |
| E | vibeflow-feature-spec | `/vibeflow-feature-spec <ID> <slug>` |
| F | vibeflow-tdd-implementation | `/vibeflow-tdd-implementation red` |
| G | vibeflow-tdd-implementation | `/vibeflow-tdd-implementation green` |
| H | vibeflow-tdd-implementation | `/vibeflow-tdd-implementation refactor` |
| I | vibeflow-release | `/vibeflow-release reconcile <ID>` |
| J | vibeflow-release | `/vibeflow-release opnote <slug>` |
| K | vibeflow-release | `/vibeflow-release check` |
| L | vibeflow-release | `/vibeflow-release check` |

**Checkpoint boundaries** — recommend `/vibeflow-validate checkpoint <N>` before advancing past:
- Stage D → E (Checkpoint #1)
- Stage E → F (Checkpoint #2)
- Stage F → G (Checkpoint #3)
- Stage H → I (Checkpoint #4)
- Stage J → K (Checkpoint #5)
- Stage L → done (Checkpoint #6)

## Artifact Verification

Use `detect_track.py` to cross-check the manifest against actual artifacts:

```bash
# Verify a specific work item's artifacts match its manifest stage
python scripts/detect_track.py --workitem <ID> --verify

# Detect artifacts for a specific work item
python scripts/detect_track.py --workitem <ID>

# Detect artifacts for all registered work items
python scripts/detect_track.py --all-workitems
```

This catches drift between the manifest and actual project state.

## References

See `references/workflow-summary.md` for a condensed workflow overview.
