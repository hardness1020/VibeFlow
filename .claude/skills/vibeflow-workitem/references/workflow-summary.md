# VibeFlow Workflow Summary

Quick reference for the docs-first development workflow.

## Core Principle

> **Docs-First Mandate:** Generate or update required docs BEFORE generating code. Code must FOLLOW the documented contracts.

## Workflow Tracks

Choose based on change scope:

```
MICRO   → F → G                          (Bug fixes, typos)
SMALL   → E → F → G → H                  (Single feature)
MEDIUM  → B → C → D → E → F → G → H → I → J   (Multi-component)
LARGE   → A → B → C → D → E → F → G → H → I → J → K → L   (System change)
```

## Stage Quick Reference

### Planning Phase

| Stage | Name | Output | Required For |
|-------|------|--------|--------------|
| A | Initiate | PRD | Large |
| B | Discovery | disco-*.md | Medium, Large |
| C | Specify | spec-*.md | Medium, Large |
| D | Decide | adr-*.md | Non-trivial decisions |

### Design Phase

| Stage | Name | Output | Required For |
|-------|------|--------|--------------|
| E | Plan | ft-*.md | Small, Medium, Large |

### Implementation Phase (TDD)

| Stage | Name | Output | Required For |
|-------|------|--------|--------------|
| F | RED | Failing tests + stubs | All tracks |
| G | GREEN | Passing tests | All tracks |
| H | REFACTOR | Integration tests + quality | All tracks |

### Release Phase

| Stage | Name | Output | Required For |
|-------|------|--------|--------------|
| I | Reconcile | Updated specs | Medium, Large |
| J | Prepare | op-*.md | Production changes |
| K | Deploy | Verified deployment | Production changes |
| L | Close | Updated indices | Production changes |

## Checkpoints

6 strategic review points:

1. **Planning Complete** (after D) — PRD + Discovery + SPECs + ADRs
2. **Design Complete** (after E) — FEATURE spec with API Design
3. **Tests Complete** (after F) — Failing tests with proper stubs
4. **Implementation Complete** (after H) — Passing tests + quality validation
5. **Release Ready** (after J) — OP-NOTE with all sections
6. **Deployed** (after L) — Verification + index updates

## File Locations

```
docs/
├── prds/
│   └── prd.md                    # Single PRD file
├── discovery/
│   └── disco-<ID>.md             # Discovery per work item
├── specs/
│   ├── index.md                  # Spec index
│   └── spec-<name>.md            # Tech specs
├── adrs/
│   └── adr-<ID>-<slug>.md        # Decisions
├── features/
│   ├── schedule.md               # Feature tracking
│   └── ft-<ID>-<slug>.md         # Feature specs
└── op-notes/
    ├── index.md                  # OP-NOTE index
    └── op-<ID>-<slug>.md         # Runbooks
```

## Enforcement Rules (Blockers)

### Planning
- Code before docs → **BLOCK**
- Stage B skipped for Medium/Large → **BLOCK**
- Missing test impact analysis → **BLOCK**

### Design
- Feature without API Design section → **BLOCK**
- Missing acceptance criteria → **BLOCK**

### Implementation
- Implementation before unit tests → **BLOCK**
- Unit tests not failing initially → **BLOCK**
- Tests without categorization → **BLOCK**
- Contract changes without SPEC update → **BLOCK**
- Stage H without integration tests for I/O → **BLOCK**
- Quality validation with 6+ violations → **BLOCK**

### Release
- Production deploy without OP-NOTE → **BLOCK**
- Missing rollback plan → **BLOCK**

## Trace IDs

Use consistent IDs everywhere:
- **Docs:** `ft-123-<slug>.md`, `disco-123.md`
- **Branch:** `feat/ft-123-<slug>`
- **Commits:** `feat(scope): subject (#ft-123)`
- **PR:** `[ft-123] Title`

## Multi-Work-Item Tracking

VibeFlow tracks multiple work items simultaneously using a manifest file at `docs/workflow-state.yaml`. Each work item has its own entry with ID, description, track, current stage, last checkpoint passed, and document paths produced at each stage.

```yaml
workitems:
  add-anti-hallucination-guardrails:
    id: 030
    description: "Add anti-hallucination guardrails"
    track: medium
    stage: G
    started: 2025-02-20
    checkpoint: 3
    docs:
      prd: docs/prds/prd.md
      discovery: docs/discovery/disco-030.md
      specs:
        - docs/specs/spec-llm.md
      adrs:
        - docs/adrs/adr-030-prompt-strategy.md
      feature: docs/features/ft-030-anti-hallucination.md
      opnote: null
```

Use `/vibeflow-workitem status` to see all work items, or `/vibeflow-workitem status <ID>` for one work item. Every stage skill updates the manifest after completing its work.

## Quick Commands

```bash
# Validate current checkpoint
python vibeflow-validate/scripts/validate_checkpoint.py

# Detect workflow state
python vibeflow-workitem/scripts/detect_track.py

# Validate specific document
python vibeflow-validate/scripts/check_planning.py
```

## Skills Reference

| Skill | Purpose | Stages |
|-------|---------|--------|
| vibeflow-workitem | Navigation, track selection | All |
| vibeflow-planning | PRD, Discovery, Specs, ADRs | A-D |
| vibeflow-feature-spec | Feature Spec with API Design | E |
| vibeflow-tdd-implementation | TDD cycle | F-H |
| vibeflow-release | OP-NOTE, Deploy, Close | I-L |
| vibeflow-validate | Checkpoint validation | All |
