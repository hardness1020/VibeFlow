---
name: record-decision
description: Document ADRs for non-trivial choices at Stage D of the VibeFlow docs-first workflow
metadata:
  triggers:
    - ADR
    - decision record
    - Stage D
    - architecture decision
---

# record-decision

Document ADRs for non-trivial choices at Stage D of the VibeFlow docs-first workflow.

## Purpose

This skill creates ADR (Architecture Decision Record) documents for Stage D:
- Document non-trivial architectural decisions
- Record alternatives considered and consequences
- Include rollback plans

## Workflow

```
Stage D: Decide
    │
    ├── Create ADRs for non-trivial decisions
    ├── Document alternatives and consequences
    └── Include rollback plans
```

## Usage

### Create ADR

```
/record-decision <ID> <slug>
```

Creates `docs/adrs/adr-<ID>-<slug>.md`.

Example:
```
/record-decision 001 backend-framework
```

## Document Requirements

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

- `scripts/validate_adr.py` — Validate ADR

## References

See `assets/`:
- `adr-template.md` — ADR template

## Manifest Update

After completing Stage D, update `docs/workflow-state.yaml`:

- Set `stage: D`
- Append to `docs.adrs[]`: `docs/adrs/adr-<ID>-<slug>.md`

**Checkpoint #1 (after Stage D):**
- Set `checkpoint: 1` after passing validation
- Criteria: PRD exists with all required sections, discovery doc exists, at least one tech spec, at least one ADR

To check readiness: `/validate-checkpoint 1`
To advance to the next stage: `/manage-work advance <ID>`
