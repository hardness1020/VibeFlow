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
---

# vibeflow-orchestrator

Master workflow navigation and track selection for the VibeFlow docs-first development workflow.

## Purpose

This skill helps navigate the VibeFlow workflow by:
- Detecting the current stage based on existing artifacts
- Selecting the appropriate workflow track (Micro/Small/Medium/Large)
- Guiding through the complete pipeline
- Showing workflow status and next steps

## Workflow

```
Track Selection
    │
    ├── Assess change scope
    ├── Select track (Micro/Small/Medium/Large)
    └── Determine starting stage
    │
    ▼
Stage Navigation
    │
    ├── Detect current stage from artifacts
    ├── Validate checkpoint completion
    ├── Route to appropriate skill
    └── Guide to next stage
```

## Usage

### Start New Workflow

```
/vibeflow-orchestrator start [track]
```

Example:
```
/vibeflow-orchestrator start medium
```

### Check Status

```
/vibeflow-orchestrator status
```

### Get Next Steps

```
/vibeflow-orchestrator next
```

### Select Track

```
/vibeflow-orchestrator track
```

This will help determine the appropriate track based on the change scope.

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

## State Detection

The orchestrator detects the current stage by checking for:

| Stage | Artifact | Location |
|-------|----------|----------|
| A | PRD | `docs/prds/prd.md` |
| B | Discovery | `docs/discovery/disco-*.md` |
| C | Tech Specs | `docs/specs/spec-*.md` |
| D | ADRs | `docs/adrs/adr-*.md` |
| E | Feature Spec | `docs/features/ft-*.md` |
| F | Test stubs | `**/test_*.py` with NotImplementedError |
| G | Passing tests | Tests green |
| H | Integration tests | `**/test_*integration*.py` |
| I | Updated specs | Spec version incremented |
| J | OP-NOTE | `docs/op-notes/op-*.md` |
| K-L | Deployment | Git tags, index updates |

## Invoke Other Skills

The orchestrator guides you to use other VibeFlow skills:

- `/vibeflow-planning` - For Stages A-D
- `/vibeflow-feature-spec` - For Stage E
- `/vibeflow-tdd-implementation` - For Stages F-H
- `/vibeflow-release` - For Stages I-L
- `/vibeflow-validate` - For checkpoint validation

## References

See `references/workflow-summary.md` for a condensed workflow overview.
