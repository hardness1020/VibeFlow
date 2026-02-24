---
name: define-tech-spec
description: Create tech specs with architecture for Stage C of the VibeFlow docs-first workflow
metadata:
  triggers:
    - tech spec
    - specification
    - Stage C
    - system specification
---

# define-tech-spec

Create tech specs with architecture for Stage C of the VibeFlow docs-first workflow.

## Purpose

This skill creates and validates Tech Spec documents for Stage C:
- Define architecture and interfaces
- Document data contracts and SLOs
- Specify component inventory and topology

## Workflow

```
Stage C: Specify
    │
    ├── Create/update Tech Specs
    ├── Define architecture and interfaces
    └── Document data contracts and SLOs
```

## Usage

### Create/Update Tech Spec

```
/define-tech-spec <spec-name>
```

Creates or updates `docs/specs/spec-<name>.md`.

Example:
```
/define-tech-spec api
/define-tech-spec llm
```

## Document Requirements

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

## Validation

- `scripts/validate_techspec.py` — Validate tech spec

## References

See `assets/`:
- `techspec-template.md` — Tech spec template

## Manifest Update

After completing Stage C, update `docs/workflow-state.yaml`:

- Set `stage: C`
- Append to `docs.specs[]`: `docs/specs/spec-<name>.md`

To advance to the next stage: `/manage-work advance <ID>`
