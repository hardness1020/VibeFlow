---
name: analyze-codebase
description: Codebase discovery and analysis for Stage B of the VibeFlow docs-first workflow
metadata:
  triggers:
    - discovery
    - analyze codebase
    - Stage B
    - codebase analysis
---

# analyze-codebase

Codebase discovery and analysis for Stage B of the VibeFlow docs-first workflow.

## Purpose

This skill creates Discovery documents for Stage B:
- Analyze existing specs and code
- Validate spec-code alignment
- Map dependencies and side effects
- Identify reusable components

## Workflow

```
Stage B: Discovery
    │
    ├── Analyze existing specs and code
    ├── Validate spec-code alignment
    ├── Map dependencies and side effects
    └── Identify reusable components
```

## Usage

### Create Discovery Document

```
/analyze-codebase <ID>
```

Creates `docs/discovery/disco-<ID>.md` with all 5 phases.

Example:
```
/analyze-codebase 030
```

## Document Requirements

### Discovery (`docs/discovery/disco-<ID>.md`)

Required phases:
- Phase 0: Spec Discovery (analyze existing specs)
- Phase 1: Spec-Code Validation (verify accuracy)
- Phase 2: Test Impact Analysis (test update checklist)
- Phase 3: Dependency & Side Effect Mapping
- Phase 4: Reusable Component Discovery
- Risk Assessment & Go/No-Go Recommendation

## Validation

- `scripts/validate_discovery.py` — Validate discovery document

## References

See `references/`:
- `discovery-guide.md` — Discovery phases guide

## Manifest Update

After completing Stage B, update `docs/workflow-state.yaml`:

- Set `stage: B`
- Set `docs.discovery: docs/discovery/disco-<ID>.md`

To advance to the next stage: `/manage-work advance <ID>`
