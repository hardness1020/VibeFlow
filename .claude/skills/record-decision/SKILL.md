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

## Context7 Library Research

Follow the workflow in `.claude/rules/context7-research.md` to fetch current library documentation.

**What to look for:** capabilities, limitations, compatibility, migration effort, maintenance status.

**Where to incorporate findings:**
- **Decision** — ground the chosen option in verified library capabilities
- **Consequences** — cite actual limitations and version constraints from docs
- **Alternatives Considered** — compare alternatives using current feature sets, not assumptions

## Manifest Update

After completing Stage D, update `docs/workflow-state.yaml`:

- Set `stage: D`
- Append to `docs.adrs[]`: `docs/adrs/adr-<ID>-<slug>.md`

**Checkpoint #1 (after Stage D):**
- Set `checkpoint: 1` after passing validation
- Criteria: PRD exists with all required sections, discovery doc exists, at least one tech spec, at least one ADR

## Git Commit

After completing this stage, ask the user for permission before committing:

```bash
git add docs/adrs/adr-<ID>-<slug>.md docs/workflow-state.yaml
git commit -m "feat(adr): record <slug> decision (#ft-<ID>)"
```

Replace `<ID>` and `<slug>` with actual values.

## Auto-Advance

After the commit is complete, directly run `/manage-work advance <ID>` to advance to the next stage.
The advance command will automatically validate Checkpoint #1 at the D→E boundary.
