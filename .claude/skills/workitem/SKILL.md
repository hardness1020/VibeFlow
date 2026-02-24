---
name: workitem
description: Register work items, create feature branches, track and advance stages, close work items in the VibeFlow docs-first development workflow
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

# workitem

Register work items, create feature branches, track and advance stages, close work items in the VibeFlow docs-first development workflow.

## Purpose

This skill tracks multiple work items through the VibeFlow workflow by:
- Registering work items with their workflow track and creating `feat/<slug>` branches
- Tracking each work item's current stage independently
- Advancing work items through stages and routing to the appropriate skill
- Closing work items as DONE after Checkpoint #4 (release is optional)
- Providing a dashboard view of all in-flight work items

## Workflow

```
Register Work Item
    │
    ├── Assign ID, generate slug from description, and assign track
    ├── Create entry in docs/workflow-state.yaml (with branch field)
    ├── Create git branch: feat/<slug>
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
    │
    ▼
Close Work Item (after Checkpoint #4)
    │
    ├── Mark stage as DONE (terminal state)
    ├── Branch ready for merge to main
    └── Alternative: advance to Stage I for release track
```

## Usage

### Register a New Work Item

```
/workitem register "<description>" <ID> <track>
```

Registers a work item in `docs/workflow-state.yaml`, determines the starting stage, and creates a git branch `feat/<slug>`.

Steps:
1. Generate kebab-case slug from description
2. Add entry to manifest with `branch: feat/<slug>`
3. Create and checkout git branch: `git checkout -b feat/<slug>`

Example:
```
/workitem register "Add anti-hallucination guardrails" 030 medium
# Creates branch: feat/add-anti-hallucination-guardrails

/workitem register "Export data to CSV" 031 small
# Creates branch: feat/export-data-to-csv
```

### Status Dashboard

```
/workitem status
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
/workitem status <ID>
```

Shows detailed status for one work item including:
- Current stage and description
- Completed and remaining stages for its track
- Last checkpoint passed
- Artifact verification (cross-check with `detect_track.py --workitem <ID>`)

### Advance a Work Item

```
/workitem advance <ID>
```

Marks a work item as advancing to the next stage in its track:
- Validates checkpoint if at a checkpoint boundary (blocks if failed)
- Updates `stage` in `docs/workflow-state.yaml`
- Updates `checkpoint` if a checkpoint boundary was crossed
- Updates `docs` paths with any documents produced at the completed stage
- Shows what the next stage requires
- **After Checkpoint #4 (Stage H):** Offers two paths:
  - `advance` → proceed to Stage I (release track)
  - `close` → mark as DONE (see Close command below)

### Close a Work Item

```
/workitem close <ID>
```

Marks a work item as DONE after passing Checkpoint #4 (Implementation Complete):
- Validates Checkpoint #4 if not yet passed (runs `validate_checkpoint.py 4 --json --project-root <root>`)
- Requires work item to be at stage H or later with checkpoint >= 4
- Sets `stage: DONE` in `docs/workflow-state.yaml`
- Branch `feat/<slug>` is ready for merge to main
- Blocked if Checkpoint #4 validation fails

Example:
```
/workitem close 030
# Sets stage: DONE, branch feat/add-anti-hallucination-guardrails ready for merge
```

### Next Steps for a Work Item

```
/workitem next <ID>
```

Shows the recommended next action for a work item:
- What the current stage requires
- Which skill command to run
- Whether a checkpoint validation is needed first

## Workflow Tracks

| Track | Scope | Stages | Release | Example |
|-------|-------|--------|---------|---------|
| **Micro** | Bug fix, typo, small refactor | F → G → DONE | No | Fix typo, update config |
| **Small** | Single feature, no contracts | E → F → G → H → DONE | Optional (I-L) | Add form field, UI polish |
| **Medium** | Multi-component, no new services | B → C → D → E → F → G → H → DONE | Optional (I-L) | New API endpoint |
| **Large** | System change, new contracts/services | A → B → C → D → E → F → G → H → DONE | Optional (I-L) | New LLM integration |

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
    stage: G             # current stage letter (A-L) or DONE
    branch: feat/add-anti-hallucination-guardrails  # git branch
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
    branch: feat/export-data-to-csv  # git branch
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
3. Add the work item entry with `id`, `description`, `track`, `stage` (first stage for the track), `branch` (`feat/<slug>`), `started` (today), `checkpoint: 0`, and empty `docs` hierarchy
4. Create and checkout git branch: `git checkout -b feat/<slug>`

When advancing a work item:
1. Read `docs/workflow-state.yaml`
2. Check if current stage is a checkpoint boundary (D→E=CP#1, E→F=CP#2, F→G=CP#3, H→I=CP#4, J→K=CP#5, L→done=CP#6)
3. If checkpoint boundary: run `python3 .claude/skills/validate/scripts/validate_checkpoint.py <N> --json --project-root <root>`
   - If exit code 1 (failed): STOP. Report errors. Do NOT update manifest.
   - If exit code 0 or 2 (passed/warnings): proceed
4. Update `stage` field to the next stage in the track
5. Update `checkpoint` if a checkpoint boundary was crossed
6. Update `docs` with any document paths produced at the completed stage

## Skill Routing

Each stage maps to a specific skill. After determining the current stage for a work item, recommend the appropriate command:

| Stage | Skill | Recommended Command |
|-------|-------|--------------------|
| A | plan | `/plan prd` |
| B | plan | `/plan discovery <ID>` |
| C | plan | `/plan spec <name>` |
| D | plan | `/plan adr <ID> <slug>` |
| E | spec | `/spec <ID> <slug>` |
| F | tdd | `/tdd red` |
| G | tdd | `/tdd green` |
| H | tdd | `/tdd refactor` |
| I | release | `/release reconcile <ID>` |
| J | release | `/release opnote <slug>` |
| K | release | `/release check` |
| L | release | `/release check` |

**Checkpoint boundaries** — recommend `/validate checkpoint <N>` before advancing past:
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
