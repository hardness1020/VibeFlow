# Hybrid TDD Policy

Mandatory requirements for Test-Driven Development in VibeFlow.

## Core Principle

> **Unit tests** are written BEFORE implementation code (RED phase).
> **Integration tests** are written during REFACTOR phase.

## The TDD Cycle

### Stage F: RED Phase

**Mandatory Steps:**

1. **Test Cleanup** (from Stage B checklist)
   - Update deprecated tests
   - Remove obsolete tests with justification
   - Verify remaining tests pass

2. **Create Implementation Stubs**
   - Extract signatures from Feature Spec "API Design" section
   - Create files with exact function names from spec
   - Use `raise NotImplementedError("...")` markers
   - Verify stubs are importable

3. **Write Failing Unit Tests**
   - Import stubs (not mock names)
   - Use exact signatures from Feature Spec
   - Tests must fail with "not implemented" errors
   - Mock all external dependencies
   - Add proper categorization tags

**Exit Criteria:**
- [ ] All deprecated tests handled
- [ ] Stubs created with correct signatures
- [ ] All new unit tests FAIL with NotImplementedError
- [ ] Tests have proper categorization
- [ ] External dependencies mocked

### Stage G: GREEN Phase

**Requirements:**
- Write **minimal** code to pass tests
- Focus on green, not perfect code
- **If contracts change** → STOP → Follow G.1 Protocol
- If tests reveal missing requirements → Add failing tests first

**Exit Criteria:**
- [ ] All unit tests PASS
- [ ] No regressions
- [ ] Code follows established patterns

### Stage H: REFACTOR Phase

**Four Substeps:**

1. **Write Integration Tests**
   - For I/O boundaries (see mandatory list below)
   - Add proper categorization tags
   - Verify tests pass in isolation

2. **Pass Integration Tests**
   - Implement any missing integration code
   - Run integration tests

3. **Refactor**
   - Clean up code
   - Keep all tests green
   - Improve naming, remove duplication

4. **Quality Validation (H.4)**
   - Complete quality checklist
   - Must have < 6 violations
   - Must have < 2 major violations

**Exit Criteria:**
- [ ] All unit tests PASS
- [ ] All integration tests PASS
- [ ] H.4 quality validation PASS
- [ ] Code meets quality standards

## Mandatory Integration Tests

Integration tests MUST be written for:

| Area | Examples |
|------|----------|
| API Endpoints | REST endpoints, GraphQL |
| Database Operations | CRUD, transactions |
| External Service Calls | Third-party APIs |
| File System Operations | Uploads, exports |
| LLM Pipelines | Prompt → LLM → Response |
| Authentication Flows | Login, OAuth, JWT |
| Background Tasks | Celery, async jobs |

Integration tests are OPTIONAL for:
- Pure business logic (if unit tested)
- Data transformation functions
- Utility functions with no I/O

## Test Categorization

**Required Tags:**

| Category | Meaning | Speed |
|----------|---------|-------|
| `unit` / `fast` | Isolated, all mocked | < 1s |
| `integration` / `medium` | Uses test DB, mocked external | < 5s |
| `e2e` / `slow` | Full workflow | seconds+ |
| `real_api` | Real external calls | varies |

**Module Tags:**
- Tag with module: `accounts`, `generation`, `api`, etc.

## Mocking Strategy

| Test Type | Database | Internal APIs | External APIs | File System |
|-----------|----------|---------------|---------------|-------------|
| Unit | Mock | Mock | Mock | Mock |
| Integration | Real (test) | Real | Mock | Real (test) |
| E2E | Real (test) | Real | Mock if expensive | Real (test) |

## Test Naming

Pattern: `test_<what>_<condition>_<expected>`

Examples:
- `test_generate_cv_with_valid_artifacts_returns_cv`
- `test_generate_cv_with_empty_artifacts_raises_error`
- `test_authentication_with_expired_token_returns_401`

## H.4 Quality Validation

### Quality Dimensions

**Organization:**
- File structure follows conventions
- Descriptive class/method names
- Related tests grouped
- Unit/integration separated

**Usefulness:**
- Based on acceptance criteria
- Tests behavior, not implementation
- Happy path + edge cases + errors

**Code Quality:**
- External deps mocked in unit tests
- Test data uses factories/fixtures
- AAA pattern clear
- No skipped tests without reason

**Categorization:**
- Speed/scope tags present
- Module tags present
- No real API calls in "unit" tests

**Reliability:**
- Unit tests < 1s each
- Integration tests < 5s each
- No flaky tests

### Quality Gate Matrix

| Violations | Decision |
|------------|----------|
| 0-2 minor | PASS |
| 3-5 | CONDITIONAL - Fix critical first |
| 1 major | CONDITIONAL - Fix major, review all |
| 6+ OR 2+ major | FAIL - Refactor tests |

### Major Violations

- Real API calls in "unit" tests
- Shared mutable state between tests
- No mocking in unit tests
- Missing tests for acceptance criteria
- Testing implementation instead of behavior
- Flaky tests

## Enforcement

### BLOCK Conditions

- Implementation before unit tests
- Unit tests not failing initially
- Tests without categorization
- Contract changes without SPEC update
- Stage H without integration tests for I/O
- H.4 validation with 6+ violations
