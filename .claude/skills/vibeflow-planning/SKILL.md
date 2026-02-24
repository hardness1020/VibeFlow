---
name: vibeflow-planning
description: Create PRDs, run codebase discovery, write tech specs, document ADRs for Stages A-D of the VibeFlow docs-first workflow
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

After completing each stage, update `docs/workflow-state.yaml`:

**Stage A:**
- Set `stage: A`
- Set `docs.prd: docs/prds/prd.md`

**Stage B:**
- Set `stage: B`
- Set `docs.discovery: docs/discovery/disco-<ID>.md`

**Stage C:**
- Set `stage: C`
- Append to `docs.specs[]`: `docs/specs/spec-<name>.md`

**Stage D:**
- Set `stage: D`
- Append to `docs.adrs[]`: `docs/adrs/adr-<ID>-<slug>.md`

**Checkpoint #1 (after Stage D):**
- Set `checkpoint: 1` after passing validation
- Criteria: PRD exists with all required sections, discovery doc exists, at least one tech spec, at least one ADR

To advance to the next stage: `/vibeflow-workitem advance <ID>`
To check readiness: `/vibeflow-validate checkpoint 1`
