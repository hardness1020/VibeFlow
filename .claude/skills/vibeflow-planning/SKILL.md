---
name: vibeflow-planning
description: Create planning documents for Stages A-D of the VibeFlow docs-first workflow
metadata:
  triggers:
    - create PRD
    - write PRD
    - product requirements
    - discovery
    - analyze codebase
    - Stage B
    - tech spec
    - specification
    - Stage C
    - ADR
    - decision record
    - Stage D
    - plan feature
    - planning phase
---

# vibeflow-planning

Create planning documents for Stages A-D of the VibeFlow docs-first workflow.

## Purpose

This skill helps create and validate planning documents:
- **PRD** (Stage A) — Product requirements
- **Discovery** (Stage B) — Codebase analysis
- **Tech Specs** (Stage C) — System specifications
- **ADRs** (Stage D) — Architectural decisions

## Workflow

```
Stage A: Initiate
    │
    ├── Create/update PRD
    ├── Define problem, users, scope
    └── Set success metrics
    │
    ▼
Stage B: Discovery
    │
    ├── Analyze existing specs and code
    ├── Validate spec-code alignment
    ├── Map dependencies and side effects
    └── Identify reusable components
    │
    ▼
Stage C: Specify
    │
    ├── Create/update Tech Specs
    ├── Define architecture and interfaces
    └── Document data contracts and SLOs
    │
    ▼
Stage D: Decide
    │
    ├── Create ADRs for non-trivial decisions
    ├── Document alternatives and consequences
    └── Include rollback plans
```

## Usage

### Create PRD

```
/vibeflow-planning prd
```

Creates or updates `docs/prds/prd.md` with required sections.

### Create Discovery Document

```
/vibeflow-planning discovery <ID>
```

Creates `docs/discovery/disco-<ID>.md` with all 5 phases.

Example:
```
/vibeflow-planning discovery 030
```

### Create/Update Tech Spec

```
/vibeflow-planning spec <spec-name>
```

Creates or updates `docs/specs/spec-<name>.md`.

Example:
```
/vibeflow-planning spec api
/vibeflow-planning spec llm
```

### Create ADR

```
/vibeflow-planning adr <ID> <slug>
```

Creates `docs/adrs/adr-<ID>-<slug>.md`.

Example:
```
/vibeflow-planning adr 001 backend-framework
```

### Validate Planning

```
/vibeflow-planning validate
```

Runs Checkpoint #1 validation on all planning documents.

## Document Requirements

### PRD (`docs/prds/prd.md`)

Required sections:
- Header (version, file, owners, last_updated)
- Summary (3-5 lines)
- Problem & Context
- Users & Use Cases
- Scope (MoSCoW format)
- Success Metrics (baseline → target)
- Non-Goals
- Requirements (functional + non-functional)
- Dependencies
- Risks & Mitigations
- Analytics & Telemetry

### Discovery (`docs/discovery/disco-<ID>.md`)

Required phases:
- Phase 0: Spec Discovery (analyze existing specs)
- Phase 1: Spec-Code Validation (verify accuracy)
- Phase 2: Test Impact Analysis (test update checklist)
- Phase 3: Dependency & Side Effect Mapping
- Phase 4: Reusable Component Discovery
- Risk Assessment & Go/No-Go Recommendation

### Tech Spec (`docs/specs/spec-<name>.md`)

Required sections:
- Header (version, status, PRD link, contract versions)
- Overview & Goals
- Architecture (topology diagram + component inventory)
- Interfaces & Data Contracts
- Data & Storage
- Reliability & SLIs/SLOs
- Security & Privacy
- Evaluation Plan

### ADR (`docs/adrs/adr-<ID>-<slug>.md`)

Required sections:
- Title with decision summary
- Header (File, Status)
- Context
- Decision
- Consequences (+/-)
- Alternatives
- Rollback Plan
- Links (PRD/SPEC/FEATURE references)

## Validation

The following scripts validate planning documents:

- `scripts/validate_prd.py` — Validate PRD structure and content
- `scripts/validate_discovery.py` — Validate discovery document
- `scripts/validate_techspec.py` — Validate tech spec
- `scripts/validate_adr.py` — Validate ADR

## References

See `assets/` for document templates:
- `prd-template.md` — PRD template
- `techspec-template.md` — Tech spec template
- `adr-template.md` — ADR template

See `references/` for guides:
- `discovery-guide.md` — Discovery phases guide

## Manifest Update

After completing a planning stage, update the work item's entry in `docs/workflow-state.yaml`:
- Set `stage` to the completed stage letter (A, B, C, or D)
- Update `checkpoint` to `1` if Stage D is complete (Checkpoint #1: Planning Complete)
- Record document paths in the `docs` hierarchy:
  - Stage A: set `docs.prd` to the PRD path (e.g., `docs/prds/prd.md`)
  - Stage B: set `docs.discovery` to the discovery doc path (e.g., `docs/discovery/disco-030.md`)
  - Stage C: append spec paths to `docs.specs[]` (e.g., `docs/specs/spec-llm.md`)
  - Stage D: append ADR paths to `docs.adrs[]` (e.g., `docs/adrs/adr-030-prompt-strategy.md`)

## Checkpoints

**Checkpoint #1 (Planning Complete):**
```
/vibeflow-validate checkpoint 1
```
Validates:
- PRD exists with all sections
- Discovery completed (Medium/Large)
- Tech Specs have architecture diagram and inventory
- ADRs exist for non-trivial decisions
