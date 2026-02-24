# VibeFlow — AI-Assisted Docs-First Development Workflow

## Project Identity

VibeFlow is a workflow template that enforces docs-first, TDD-driven development for AI-assisted software engineering. It uses Claude Code skills and hooks to ensure documentation stays current and tests drive implementation.

## Core Principle: Docs-First Mandate

**All documentation MUST exist and be validated BEFORE any code is written.** Stages A-E produce documents; Stages F-H implement code that must match those documents.

## Workflow Structure

See `README.md` for the full pipeline diagram. Summary:

- **Stages A-D** (Planning): PRD, Discovery, Tech Specs, ADRs
- **Stage E** (Design): Feature Spec with API Design
- **Stages F-H** (Implementation): TDD cycle — RED, GREEN, REFACTOR
- **Stages I-L** (Release): Reconcile, OP-NOTE, Deploy, Close — **optional**
- **DONE**: Terminal state after Checkpoint #4 (can close without release)

Six checkpoints gate progression between phases.

## Tracks

| Track | Start | End | Planning | Release |
|-------|-------|-----|----------|---------|
| Micro | F | G → DONE | None | No |
| Small | E | H → DONE or I-L | Feature spec | Optional |
| Medium | B | H → DONE or I-L | Full planning | Optional |
| Large | A | H → DONE or I-L | Full + PRD | Optional |

## Branch Convention

Every work item is bound to a dedicated git branch:

- **Format:** `feat/<slug>` (e.g., `feat/add-anti-hallucination-guardrails`)
- **Slug:** The work item key from `docs/workflow-state.yaml` (kebab-case from description)
- **Lifecycle:** Register creates branch → all work happens on branch → close/merge to main
- **Enforcement:** Hook blocks edits on `main` and on branches not matching an active work item

## Enforcement Rules

These rules are **deterministic** — enforced by hooks and skills:

1. **Branch binding (UserPromptSubmit hook):** All prompts blocked unless current branch is `feat/<slug>` for an active work item. Workitem commands are exempted so users can register new work items from main.
2. **Checkpoint gates (two layers):**
   - **UserPromptSubmit hook:** `checkpoint-gate.py` blocks prompts containing "advance"/"close" if checkpoint not passed (deterministic safety net)
   - **Workitem skill:** `advance` and `close` commands validate checkpoints before updating the manifest (skill-instructed, redundant backup)
3. **Exception:** Prompts are always allowed when no manifest exists (initial project setup) or when no active work items are present
4. **All hooks are read-only** — no hook mutates any file. All manifest updates happen in skills.

## File Naming Conventions

- **Manifest:** `docs/workflow-state.yaml` (single source of truth)
- **PRD:** `docs/prds/prd.md`
- **Discovery:** `docs/discovery/disco-<ID>.md`
- **Tech Specs:** `docs/specs/spec-<name>.md`
- **ADRs:** `docs/adrs/adr-<ID>-<slug>.md`
- **Feature Specs:** `docs/features/ft-<ID>-<slug>.md`
- **OP-NOTEs:** `docs/op-notes/op-<slug>.md`

## Document Hierarchy

```
docs/
  workflow-state.yaml    # Manifest — source of truth
  prds/prd.md            # Product Requirements
  discovery/disco-*.md   # Codebase Analysis
  specs/spec-*.md        # Tech Specifications
  adrs/adr-*.md          # Architecture Decisions
  features/ft-*.md       # Feature Specifications
  op-notes/op-*.md       # Deployment Runbooks
```

## Skills

| Skill | Stages | Purpose |
|-------|--------|---------|
| `/workitem` | All | Register, track, advance, close work items |
| `/plan` | A-D | PRDs, discovery, tech specs, ADRs |
| `/spec` | E | Feature specs with acceptance criteria |
| `/tdd` | F-H | TDD cycle: RED → GREEN → REFACTOR |
| `/release` | I-L | Reconcile, OP-NOTE, deploy, close |
| `/validate` | Checkpoints | Checkpoint validation and enforcement |
| `/intake` | A (optional) | Demand clarification + feasibility → register handoff |

## Agents

Specialized subagents with tool restrictions enforced by PreToolUse hooks:

| Agent | Stages | Tools | Hook | Purpose |
|-------|--------|-------|------|---------|
| `codebase-analyst` | B | Read, Grep, Glob | — | Analyze codebase, map dependencies |
| `spec-drafter` | C-D | Read, Grep, Glob, Write, Edit | `enforce-docs-only.py` | Draft specs and ADRs (docs/ only) |
| `api-researcher` | E | Read, Grep, Glob | — | Analyze existing API patterns |
| `test-writer` | F | Read, Grep, Glob, Write, Edit, Bash | `enforce-test-files-only.py` | Create stubs + failing tests |
| `implementer` | G | Read, Grep, Glob, Write, Edit, Bash | `enforce-no-test-no-doc.py` | Implement to pass tests (source only) |

Agent definitions live in `.claude/agents/`. Enforcement hooks exit 2 to block, exit 0 to allow, and fail open on errors.

## Quick Reference

```
/workitem register "<desc>" <ID> <track>   # Create work item + branch
/workitem status [<ID>]                     # Dashboard or detail view
/workitem advance <ID>                      # Move to next stage
/workitem close <ID>                        # Mark DONE after CP#4
/workitem next <ID>                         # Show next action
/validate checkpoint <N>                    # Validate checkpoint
/intake                                     # Clarify idea → register
```
