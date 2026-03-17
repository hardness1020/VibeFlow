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

## Library Documentation Lookup

When referencing external libraries, frameworks, or APIs in this document, use the Context7 MCP tools to look up current documentation rather than relying on training data:

1. `mcp__context7_resolve-library-id` — find the library ID
2. `mcp__context7_get-library-docs` — retrieve current docs

Also consider using `/find-docs` for broader technical documentation lookup.

## Manifest Update

After completing Stage C, update `docs/workflow-state.yaml`:

- Set `stage: C`
- Append to `docs.specs[]`: `docs/specs/spec-<name>.md`

## Git Commit

After completing this stage, ask the user for permission before committing:

```bash
git add docs/specs/spec-<name>.md docs/workflow-state.yaml
git commit -m "feat(spec): define <name> tech spec (#ft-<ID>)"
```

Replace `<name>` and `<ID>` with actual values.

## Auto-Advance

After the commit is complete, directly run `/manage-work advance <ID>` to advance to the next stage.
