---
name: define-prd
description: Create PRDs with success metrics for Stage A of the VibeFlow docs-first workflow
metadata:
  triggers:
    - create PRD
    - write PRD
    - product requirements
    - Stage A
    - plan feature
---

# define-prd

Create PRDs with success metrics for Stage A of the VibeFlow docs-first workflow.

## Purpose

This skill creates and validates PRD (Product Requirements Document) for Stage A:
- Define problem, users, and scope
- Set success metrics with baseline → target
- Document requirements, dependencies, and risks

## Workflow

```
Stage A: Initiate
    │
    ├── Create/update PRD
    ├── Define problem, users, scope
    └── Set success metrics
```

## Usage

### Create PRD

```
/define-prd
```

Creates or updates `docs/prds/prd.md` with required sections.

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

## Validation

- `scripts/validate_prd.py` — Validate PRD structure and content

## References

See `assets/`:
- `prd-template.md` — PRD template

## Manifest Update

After completing Stage A, update `docs/workflow-state.yaml`:

- Set `stage: A`
- Set `docs.prd: docs/prds/prd.md`

To advance to the next stage: `/manage-work advance <ID>`
