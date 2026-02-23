---
name: vibeflow-tdd-implementation
description: Write failing unit tests (RED), implement minimal code (GREEN), refactor with quality validation for Stages F-H of the VibeFlow docs-first workflow
metadata:
  triggers:
    - implement feature
    - start TDD
    - write tests
    - Stage F
    - Stage G
    - Stage H
    - RED phase
    - GREEN phase
    - REFACTOR phase
---

# vibeflow-tdd-implementation

TDD implementation cycle for Stages F-H of the VibeFlow docs-first workflow.

## Purpose

This skill guides the TDD cycle:
- **Stage F (RED)**: Create stubs + write failing unit tests
- **Stage G (GREEN)**: Implement minimal code to pass tests
- **Stage H (REFACTOR)**: Write integration tests + refactor + quality validation

## Workflow

```
Stage F: RED
    │
    ├── Create stubs from Feature Spec API Design
    ├── Write failing unit tests
    ├── Tests fail with NotImplementedError
    └── Checkpoint #3: Tests Complete
    │
    ▼
Stage G: GREEN
    │
    ├── Implement minimal code to pass tests
    ├── If contracts change → Stage G.1
    └── All unit tests pass
    │
    ▼
Stage H: REFACTOR
    │
    ├── Write integration tests for I/O
    ├── Pass integration tests
    ├── Refactor with tests green
    ├── Complete H.4 quality validation
    └── Checkpoint #4: Implementation Complete
```

## Usage

### Start TDD Cycle

```
/vibeflow-tdd-implementation start
```

Guides through the full TDD cycle starting with Stage F.

### Stage F: RED Phase

```
/vibeflow-tdd-implementation red
```

1. Create implementation stubs from Feature Spec API Design
2. Write failing unit tests
3. Verify tests fail with "not implemented" errors

### Stage G: GREEN Phase

```
/vibeflow-tdd-implementation green
```

1. Implement minimal code to pass unit tests
2. Check for contract changes (trigger G.1 if needed)
3. Verify all unit tests pass

### Stage H: REFACTOR Phase

```
/vibeflow-tdd-implementation refactor
```

1. Write integration tests for I/O boundaries
2. Refactor code while keeping tests green
3. Complete H.4 quality validation

### Validate Tests

```
/vibeflow-tdd-implementation validate
```

Runs test quality validation (Stage H.4 checklist).

### Handle Design Changes

```
/vibeflow-tdd-implementation g1
```

Guides through Stage G.1 protocol when implementation reveals contract changes.

## Stage G.1: Design Changes Protocol

If implementation reveals contract changes, **STOP IMMEDIATELY** and follow these steps:

1. Document the discovered issue
2. Update SPEC first (increment version)
3. Create/update ADR if non-trivial
4. Update Feature Spec API Design
5. Update tests to new contract
6. Resume implementation

**Contract changes that trigger G.1:**
- API/Interface signature changes
- Database schema changes
- Event format changes
- New external dependencies
- SLO changes

**Changes that DON'T trigger G.1:**
- Internal algorithms
- Private function names
- Error handling improvements (within taxonomy)
- Performance optimizations (within SLO)

## Test Categorization

All tests must have categorization tags:

**Speed/Scope (required):**
- `unit` / `fast` — All dependencies mocked, runs in ms
- `integration` / `medium` — Uses test DB, mocked external APIs
- `e2e` / `slow` — Full workflow, multiple components
- `real_api` — Makes real external API calls

**Module (required):**
- Tag with module name (e.g., `accounts`, `generation`, `api`)

## Stage H.4 Quality Validation

Before completing Stage H, validate:

**Organization:**
- File structure follows conventions
- Test names use `test_<what>_<condition>_<expected>`
- Related tests grouped

**Usefulness:**
- Tests based on acceptance criteria
- Happy path, edge cases, error cases tested
- Tests validate behavior, not implementation

**Code Quality:**
- External dependencies mocked in unit tests
- AAA pattern clear
- No skipped tests without justification

**Categorization:**
- All tests have speed/scope tags
- No real API calls in "unit" tests

**Reliability:**
- Unit tests < 1s each
- Integration tests < 5s each
- Tests pass consistently (no flaky tests)

**Quality Gate:**
- 0-2 violations: PASS
- 3-5 violations: CONDITIONAL
- 6+ violations OR 2+ major: FAIL

## Validation

- `scripts/validate_red.py` — Validate Stage F (tests failing correctly)
- `scripts/validate_green.py` — Validate Stage G (tests passing)
- `scripts/validate_refactor.py` — Validate Stage H (integration + quality)
- `scripts/check_coverage.py` — Report test coverage

## References

See `references/`:
- `tdd-policy.md` — TDD policy and requirements
- `tdd-guide.md` — TDD workflow guidance
- `stage-g1-protocol.md` — Design change handling protocol

## Manifest Update

After completing each stage, update `docs/workflow-state.yaml`:

**Stage F (RED):**
- Set `stage: F`

**Checkpoint #3 (after Stage F):**
- Set `checkpoint: 3` after passing validation
- Criteria: Stubs exist matching Feature Spec API Design, unit tests exist and fail with NotImplementedError

**Stage G (GREEN):**
- Set `stage: G`

**Stage H (REFACTOR):**
- Set `stage: H`

**Checkpoint #4 (after Stage H):**
- Set `checkpoint: 4` after passing validation
- Criteria: All unit tests pass, integration tests pass, H.4 quality validation passes

To advance to the next stage: `/vibeflow-orchestrator advance <ID>`
To check readiness: `/vibeflow-validate checkpoint 3` (after RED) or `/vibeflow-validate checkpoint 4` (after REFACTOR)
