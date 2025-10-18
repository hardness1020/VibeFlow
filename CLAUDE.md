# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **VibeFlow-ClaudeCode**, a workflow template repository that implements a Git-versioned living documentation system with Hybrid Test-Driven Development (TDD) practices. It provides a structured approach to software development with documentation-first mandate and stage-gated reviews.

## Core Philosophy

**Docs-first mandate:** Generate or update required docs **before** generating code. Code must follow documented contracts, topology, framework roles, and SLOs.

**Stage gating:** At each stage, generate required file(s) and **stop for human review/approval** before proceeding.

**Hybrid TDD:** Unit tests written before implementation (RED phase), integration tests written during refactoring (REFACTOR phase).

## Repository Structure

```
.
├── rules/                    # Workflow and documentation rules
│   ├── 00-workflow.md       # Top governance rule (MUST READ FIRST)
│   ├── 01-prd.md            # Product Requirements Document format
│   ├── 02-tech_spec.md      # Technical Specification format
│   ├── 03-adr.md            # Architecture Decision Records format
│   ├── 04-feature.md        # Feature specification format
│   ├── 05-tdd.md            # Hybrid TDD implementation mandate
│   ├── 06-op_note.md        # Operations/Runbook format
│   ├── design-principles.md # S-Tier SaaS dashboard design checklist
│   └── markdown.md          # Markdown authoring standards
└── docs/                    # Project documentation (to be created)
    ├── prds/                # Product requirement documents
    ├── specs/               # Technical specifications
    ├── adrs/                # Architecture decision records
    ├── features/            # Feature specifications
    └── op-notes/            # Operations notes/runbooks
```

## Workflow Stages

### Size-Based Tracks

| Track    | Scope                        | Stages              | Example                           |
|----------|------------------------------|---------------------|-----------------------------------|
| **Micro**   | Bug fix, typo, small refactor | F → G               | Fix typo, update config value     |
| **Small**   | Single feature, no contracts  | E → F → G → H       | Add field to form, UI polish      |
| **Medium**  | Multi-component, no services  | B → C → D → E → F → G → H → I | New API endpoint with existing services |
| **Large**   | System change, new contracts  | Full A → K          | New LLM integration, new auth system |

### 6 Strategic Review Checkpoints

1. **Planning Complete** (after Stage C): PRD + Discovery + SPECs + ADRs
2. **Design Complete** (after Stage E): FEATURE spec
3. **Tests Complete** (after Stage F): Failing unit tests
4. **Implementation Complete** (after Stage H): Working + refactored code
5. **Release Ready** (after Stage I): OP-NOTE
6. **Deployed** (after Stage K): Post-deployment verification

### Stage Pipeline (Large Track: A → K)

**A. Initiate** → Generate/update `docs/prds/prd.md`
**B. Codebase Discovery** → Search for reusable components, analyze patterns
**C. Specify** → Create/update `docs/specs/spec-<spec>.md` (system/api/frontend/llm)
**D. Decide** → Create `docs/adrs/adr-<ID>-<slug>.md` for non-trivial decisions
**E. Plan** → Create `docs/features/ft-<ID>-<slug>.md` + update schedule
**F. Write Unit Tests (RED)** → Failing unit tests with `NotImplementedError`
**G. Implement (GREEN)** → Minimal code to pass unit tests
**H. Integration Tests & Refactor** → Write integration tests, pass them, refactor code
**I. Release Prep** → Create `docs/op-notes/op-<ID>-<slug>.md` or `op-release-<semver>.md`
**J. Deploy & Verify** → Follow OP-NOTE, run smoke tests
**K. Close Loop** → Update indexes, tag release, close issues

## Critical Rules & Enforcement

### Documentation-First Blockers

- Code generated **before** required docs → **BLOCK** and generate docs first
- Stage B skipped for Medium/Large → **BLOCK** and perform discovery
- Duplicate code when reusable exists → **BLOCK** and refactor to reuse
- Implementation before unit tests → **BLOCK** and write tests first (TDD violation)
- Unit tests not failing initially → **BLOCK** and verify tests specify new behavior
- Stage H without integration tests for I/O → **BLOCK** and write integration tests
- Public contracts changed without SPEC update → **BLOCK merge**
- Non-trivial choices without ADR → **BLOCK merge**
- Feature work without FEATURE file → **BLOCK merge**
- Production changes without OP-NOTE → **BLOCK deployment**

### Hybrid TDD Cycle

**RED (Stage F):** Write failing **unit tests** first
- Focus on business logic and API design
- Mock all external dependencies
- Use `NotImplementedError` with helpful messages
- Tests serve as executable specifications

**GREEN (Stage G):** Write minimal code to pass **unit tests**
- Focus on making tests green
- Integration tests not required yet

**REFACTOR (Stage H):** Write integration tests, then refactor
1. Write integration tests for I/O boundaries (API endpoints, DB operations, external services, LLM pipelines, file I/O, auth flows, background tasks)
2. Implement missing integration code to pass tests
3. Refactor code while keeping all tests (unit + integration) green

### Integration Tests Mandatory For

- ✅ API Endpoints (REST/GraphQL)
- ✅ Database Operations
- ✅ External Service Calls (OpenAI, Anthropic, etc.)
- ✅ File System Operations
- ✅ LLM Pipelines
- ✅ Authentication Flows
- ✅ Background Tasks (Celery, async)

## File Naming Conventions

### Documentation

- **PRD:** `docs/prds/prd.md` (single file, edit directly)
- **SPEC:** `docs/specs/spec-<spec>.md` (e.g., `spec-api.md`, `spec-frontend.md`)
- **ADR:** `docs/adrs/adr-<ID>-<slug>.md` (e.g., `adr-001-backend-framework.md`)
- **FEATURE:** `docs/features/ft-<ID>-<slug>.md` (e.g., `ft-001-hover-badge.md`)
- **OP-NOTE:** `docs/op-notes/op-<ID>-<slug>.md` or `op-release-<semver>.md`

### Git (User-Controlled Conventions)

- **Branches:** `feat/<ID>-<slug>`, `fix/<ID>-<slug>`, `chore/<ID>-<slug>`
- **Commits:** `<type>(scope): subject (#<ID>)` (Conventional Commits)
- **PRs:** `[<ID>] <title>`

## Versioning & Change Control

### SPEC Versioning (Semantic)

- **Minor edits:** Update file + Changelog (no version bump)
- **Material changes** (contracts/SLOs/topology/frameworks):
  - Increment version (v1.3.0 → v2.0.0)
  - Update Changelog with dated entry
  - Git tag: `spec-<spec>-v2.0.0`
  - Mark prior version as "Superseded"

### Version Update Triggers

- **Contracts:** API/GraphQL schemas, DB schemas, model/prompt I/O
- **Topology:** New components/paths/protocols/trust boundaries
- **Framework roles:** Django/DRF, React, Redis, Celery, Postgres changes
- **SLOs:** Availability/latency/error-rate targets

## Rule Compliance

Each generated file must follow its corresponding rule format:

- `rules/01-prd.md` → PRD format and standards
- `rules/02-tech_spec.md` → SPEC format and standards
- `rules/03-adr.md` → ADR format and standards
- `rules/04-feature.md` → FEATURE format and standards
- `rules/05-tdd.md` → Hybrid TDD practices
- `rules/06-op_note.md` → OP-NOTE format and standards
- `rules/markdown.md` → Markdown authoring standards

## Architecture Documentation Requirements

SPEC files must include:

1. **Comprehensive diagram** naming each framework and showing relationships (edges, protocols, trust boundaries)
2. **Component inventory table** with: framework/runtime, purpose, interfaces (in/out), dependencies, scale/HA, owner

## Working with This Repository

### Before Starting Any Work

1. Read `rules/00-workflow.md` (top governance rule)
2. Identify which track applies (Micro/Small/Medium/Large)
3. Follow the required stages for that track
4. Stop at each review checkpoint for human approval

### Stage B: Codebase Discovery (Medium/Large)

Before designing new solutions:
- Search for similar features (Grep, Glob, Read)
- Identify reusable services/components
- Map existing architecture patterns
- Check for duplicate implementations
- Review test coverage of related code
- Document findings with reuse checklist

### Writing Documentation

All documentation files must:
- Follow the format in corresponding `rules/*.md` file
- Include proper headers (version, file, owners, dates)
- Link upstream artifacts (PRD → SPEC → ADR → FEATURE)
- Maintain Changelog sections
- Use traceability IDs consistently

### Test Coverage Targets

- **Unit tests:** 80%+ coverage for business logic
- **Integration tests:** All critical I/O paths
- **Test runtime:** Unit tests under 5 minutes
- **Test-to-code ratio:** 1:1 to 2:1 for healthy projects

## Traceability System

Use IDs everywhere for traceability:

- **Docs:** `ft-123-<slug>.md`, `adr-123-<slug>.md`
- **Git:** Branch `feat/ft-123-<slug>`, PR `[ft-123] <title>`, Commits `feat(scope): subject (#ft-123)`
- **Code:** Reference IDs in TODOs and FIXMEs

## Design Principles (if applicable)

For UI/dashboard projects, reference `rules/design-principles.md` for S-Tier SaaS design standards inspired by Stripe, Airb, and Linear.

## Key Principles

1. **Users First:** Prioritize user needs and workflows
2. **Docs-First:** Documentation before code
3. **Stage Gating:** Human review at each checkpoint
4. **TDD Discipline:** Tests before implementation
5. **Reuse Over Rebuild:** Leverage existing components
6. **Pattern Compliance:** Follow established architecture patterns
7. **Contract Discipline:** Version and document all public interfaces
8. **Traceability:** IDs in docs, git, and code
