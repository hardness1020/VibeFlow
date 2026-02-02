# Test-Driven Development Implementation Guide

**Purpose:** Conceptual guidance for implementing TDD workflow and decision-making. For code examples, framework-specific commands, and implementation details, see your project's `docs/testing/` directory.

**Policy Reference:** See `rules/06-tdd/policy.md` for mandatory TDD requirements, test type definitions, and quality gate decision criteria.

## Table of Contents
1. [Complete TDD Workflow Concepts](#complete-tdd-workflow-concepts)
2. [Stub Creation from FEATURE Specs](#stub-creation-from-feature-specs)
3. [Test Categorization Principles](#test-categorization-principles)
4. [Test Execution Strategy](#test-execution-strategy)
5. [Test Quality Validation](#test-quality-validation)
6. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

## Complete TDD Workflow Concepts

### Stage F → G → H: The TDD Cycle

The TDD cycle consists of three distinct phases, each with specific goals and validation checkpoints.

#### Stage F: Write Failing Unit Tests (RED Phase)

**Goal:** Define expected behavior through tests before writing implementation.

**Process:**
1. Write failing unit tests based on FEATURE spec acceptance criteria
2. Tests should fail with clear "not implemented" errors (not import/syntax errors)
3. Verify tests are discoverable by test runner
4. Confirm all external dependencies are mocked

**Quick Validation:**
- Run only new test file (should complete in seconds)
- Expected outcome: All new tests fail with "not implemented" error

#### Stage G: Implement to Pass Tests (GREEN Phase)

**Goal:** Write minimal code to make tests pass.

**Process:**
1. Implement only what's needed to pass failing tests
2. Don't optimize or add extra features
3. Focus on making tests green, not perfect code

**Quick Validation:**
- Run only new test file (should complete in seconds)
- Expected outcome: All new tests pass
- Run all unit tests for affected module (should complete in seconds to minutes)
- Expected outcome: No regressions, all tests pass

#### Stage H: Write Integration Tests & Refactor (REFACTOR Phase)

**Goal:** Add integration tests for I/O boundaries, then refactor with confidence.

**Process:**
1. Write integration tests for database, API endpoints, file I/O, external services
2. Implement any missing integration code to pass integration tests
3. Refactor implementation while keeping all tests green
4. Complete Test Quality Validation checklist

**Validation:**
- Run new integration test file (should complete in seconds)
- Run all integration tests for affected module (should complete in minutes)
- Run full integration suite before commit (should complete in 5-10 minutes)

## Stub Creation from FEATURE Specs

### Why Create Stubs First

Before writing failing tests in Stage F, create implementation stub files based on API signatures defined in FEATURE spec. This ensures:
- Tests reference actual function/class names from the contract
- Tests fail with "not implemented" errors (not import errors)
- API design is validated before writing tests
- Function names are contracts, not ad-hoc choices

### Prerequisites

FEATURE spec (Stage E) must provide:
- "API Design" section with exact function/class/method signatures
- Function names, parameters, and return types as part of the contract
- If naming is uncertain, it must be resolved in Stage E before proceeding to Stage F

### Stub Creation Process

#### Step 1: Extract API Signatures from FEATURE Spec

Review the FEATURE spec's "API Design" section and identify all public functions/classes/methods to be implemented.

**What to extract:**
- Function/method names
- Parameter names and types
- Return types
- Expected behaviors (for error messages)

#### Step 2: Create Stub Files with Exact Signatures

Create implementation files matching the spec design, using exact names from FEATURE spec.

**Stub characteristics:**
- Use exact function/class names from FEATURE spec
- Include all parameters with correct types
- Raise/throw "not implemented" error with helpful context
- Add docstrings/comments explaining what needs to be implemented
- Reference feature ID (e.g., "Implementation for ft-XXX")

**For code examples, see project docs/testing/.**

#### Step 3: Write Tests Using Stubs

Import stub functions in test files and verify:
- Names resolve correctly (no import errors)
- Tests use exact signatures from FEATURE spec
- Tests fail with expected "not implemented" errors
- All external dependencies are mocked

### What to Do If Naming Issues Discovered

If creating stubs reveals better naming patterns (e.g., existing codebase uses different conventions):

1. **STOP** - Do not proceed with tests
2. **Update FEATURE spec** (Stage E) with corrected API signatures
3. **Document rationale** for naming change in spec
4. **Resume Stage F** with updated signatures

### Benefits of Stub-First Approach

- Tests fail with clear "not implemented" errors (not import/reference errors)
- Function names are contracts defined in FEATURE spec, not ad-hoc
- Stub creation validates API design before writing tests
- Documents expected signatures for implementer in Stage G

## Test Categorization Principles

### Decision Tree for Categorization

All tests must be categorized by two dimensions: **Speed/Scope** and **Module**.

**Speed/Scope Decision Criteria:**

```
Does test make external API calls (real network requests)?
├─ YES (real API) → Category: Real API Tests (slow)
└─ NO → Does test use database/filesystem/external services?
    ├─ YES → Category: Integration Tests (medium)
    └─ NO → Category: Unit Tests (fast)
```

### Categorization Requirements

**Mandatory Categories:**
1. **Speed/Scope** (choose one): unit/fast, integration/medium, e2e/slow, real_api/slow
2. **Module/Package**: Tag with module name (e.g., accounts, generation, api)
3. **Feature** (optional): Tag with feature ID for feature-specific test runs (e.g., ft-123)

**Validation Checklist:**
- Speed category matches test characteristics
- Unit tests have ALL dependencies mocked
- Integration tests use test database/filesystem
- Real API tests are protected with safeguards
- Module tags match file location
- No real API calls in tests tagged "unit" or "fast"

**For framework-specific tagging syntax and code examples, see project docs/testing/.**

## Test Execution Strategy

### Execution Philosophy

**Goal:** Fast feedback during TDD cycle, comprehensive validation before committing.

**Key Principles:**
- Run only new tests first (seconds) for rapid iteration
- Expand to module tests (minutes) for local regression
- Run full suite (minutes to 10+ minutes) only at checkpoints (before commit, in CI/CD)

### Stage F → G Cycle: Unit Test Execution

**During TDD Iteration (RED → GREEN):**
1. **First:** Run only new test file (fast feedback - seconds)
   - Validates new tests work correctly
   - Catches syntax errors, import issues immediately
2. **Then:** Run all fast unit tests (full regression - minutes)
   - Ensures no regressions in existing functionality
   - Validates mocking is working correctly

**Why This Matters:**
- Without targeted execution: 5-10 minutes per change (running all tests)
- With targeted execution: Seconds for new tests, full suite only when needed
- Time saved: 80-90% faster TDD feedback loop

### Stage H: Integration Test Execution

**During Integration Testing:**
1. **First:** Run only new integration test file (fast feedback)
2. **Then:** Run all integration tests for affected module
3. **Finally:** Run full integration suite before commit/PR

### Execution Checkpoints

**When to Run Full Test Suite:**
- Before committing code
- Before creating/updating PR
- Before deployment
- In CI/CD pipeline

**Time-Saving Strategies:**
1. Use database/state persistence flags (save 2-10 seconds per run)
2. Run targeted tests first (catch issues in seconds, not minutes)
3. Use module/package tags (run only affected module's tests)
4. Skip slow tests during rapid iteration (run only before commits)

### Performance Benchmarks (with proper mocking)

| Execution Type | Expected Time | Use Case |
|----------------|---------------|----------|
| Single new test file | <1s | Rapid TDD cycle (Stage F/G) |
| Module unit tests | 10-30s | Module regression |
| All unit tests | 1-3min | Full unit regression |
| Module integration tests | 10-60s | Module integration check |
| All integration tests | 5-10min | Full integration check |
| All tests (unit + integration) | 6-13min | Pre-commit checkpoint |

**For framework-specific test execution commands, see project docs/testing/.**

## Test Quality Validation

### Complete Quality Validation Checklist

Use this comprehensive checklist before completing Stage H to ensure new tests are well-organized, useful, and maintainable.

#### Test Organization Quality

**File Structure and Naming:**
- [ ] Test files follow project naming conventions
- [ ] Test classes/suites have descriptive names
- [ ] Test methods/functions use clear naming pattern: `test_<what>_<condition>_<expected_result>`
- [ ] Related tests grouped in same class/suite

**Test Structure:**
- [ ] One test class/suite per service/component/API endpoint
- [ ] Setup/teardown used for shared test data and cleanup
- [ ] Test isolation - each test can run independently
- [ ] Clear separation between unit and integration tests (different files/folders)

**Documentation:**
- [ ] Module/file docstring explains what's being tested and references feature ID
- [ ] Class/suite docstrings describe test scope and dependencies
- [ ] Complex test scenarios have docstrings explaining the situation
- [ ] Naming choices documented if they differ from FEATURE spec

#### Test Usefulness Quality

**Requirement Coverage:**
- [ ] Tests based on acceptance criteria from FEATURE spec
- [ ] All acceptance criteria have corresponding tests
- [ ] Tests validate behavior, not implementation details
- [ ] Tests check outcomes and state changes, not internal/private methods

**Test Coverage Completeness:**
- [ ] **Happy path:** Normal operation tested
- [ ] **Edge cases:** Empty inputs, boundary values, null/undefined handled
- [ ] **Error cases:** Invalid inputs, exceptions, error conditions tested
- [ ] **Integration points:** All I/O boundaries have integration tests (if Stage H)

**Test Value:**
- [ ] Tests would catch real bugs (not just tautologies)
- [ ] No duplicate tests (same scenario tested multiple times)
- [ ] Tests are focused (one logical assertion per test)
- [ ] Tests don't rely on shared mutable state

#### Test Code Quality

**Proper Mocking (Unit Tests):**
- [ ] All external dependencies mocked (database, APIs, file system, network)
- [ ] Mocks use project-standard utilities
- [ ] Mock setup/teardown properly handled
- [ ] Mock configurations realistic (match actual API behavior)
- [ ] No real API calls in tests tagged as "unit" or "fast"

**Test Data Management:**
- [ ] Uses factories/fixtures for test data (not hardcoded everywhere)
- [ ] Test data cleaned up after each test
- [ ] Deterministic data (no random values without seeds)
- [ ] Realistic data (matches production scenarios)
- [ ] Minimal data (only create what's needed for test)

**Readability and Maintainability:**
- [ ] Arrange-Act-Assert (AAA) pattern clear in each test
- [ ] No magic numbers or strings (use named constants)
- [ ] Assertion messages explain what failed and why
- [ ] No commented-out code or skipped tests without justification
- [ ] Test code follows same quality standards as production code

### Quality Gate Decision Matrix

After reviewing all new tests against the checklist, count violations:

| Violations | Decision | Action Required |
|------------|----------|-----------------|
| 0-2 minor | **PASS** | Fix violations and proceed |
| 3-5 violations | **CONDITIONAL** | Fix critical issues before proceeding |
| 1 major violation | **CONDITIONAL** | Fix major violation, review all tests |
| 6+ violations OR 2+ major | **FAIL** | Refactor tests before proceeding |

**Major Violations (must fix immediately):**
- Tests make external API calls but tagged as "fast" or "unit"
- Tests share mutable state (tests fail when run in different order)
- Tests don't use mocking for external dependencies in unit tests
- No tests for critical acceptance criteria
- Tests check implementation details (private methods) instead of behavior
- Tests are non-deterministic (flaky, random failures)

**Minor Violations (should fix before proceeding):**
- Missing docstrings
- Poor test names (not descriptive enough)
- Hardcoded values instead of named constants
- Missing edge case tests
- No assertion messages
- Inconsistent test structure

**For code examples of good vs. poor test quality, see project docs/testing/.**

## Common Pitfalls and Solutions

### Pitfall 1: Tests Run Slow

**Problem:** Unit tests take minutes instead of seconds

**Root Causes:**
- Missing mocks for external APIs (tests make real network calls)
- Not using database persistence flags (recreating database each run)
- Running all tests instead of targeted subset
- Integration tests mixed with unit tests

**Solutions:**
1. Check for missing mocks: Review tests tagged "unit" or "fast" for external calls
2. Use database persistence: Enable test database reuse between runs
3. Run targeted tests first: Execute only new test file during iteration
4. Separate unit and integration: Ensure unit tests have zero I/O

### Pitfall 2: Flaky Tests

**Problem:** Tests pass/fail randomly

**Root Causes:**
- Timing dependencies (sleep statements, timeouts)
- Random data without seeds
- Test execution order dependencies
- Shared mutable state between tests

**Solutions:**
1. Use deterministic data: Seed random generators, use fixed timestamps
2. Avoid sleep/timeouts: Mock time-based functions instead of waiting
3. Ensure test isolation: Each test should set up and tear down its own state
4. Don't share mutable state: Use fixtures/factories to create fresh data per test

### Pitfall 3: Tests Break During Refactoring

**Problem:** Tests coupled to implementation details

**Root Causes:**
- Testing private methods
- Checking internal state
- Implementation-specific assertions
- Over-mocking (mocking too much internal behavior)

**Solutions:**
1. Test behavior, not implementation: Assert on outcomes, not internal details
2. Test public API only: Don't test private/internal methods directly
3. Use black-box testing: Test from outside perspective (inputs → outputs)
4. Mock only external dependencies: Don't mock internal collaborators

### Pitfall 4: Poor Test Names

**Problem:** Test names don't explain what's being tested

**Root Causes:**
- Generic names (test1, test_service, test_method)
- Missing context (what condition, what expected result)
- Unclear intent (not obvious what behavior is validated)

**Solutions:**
1. Use pattern: `test_<what>_<condition>_<expected_result>`
2. Be specific: Name should read like a sentence describing behavior
3. Include context: What scenario is being tested
4. State expectation: What outcome is expected

**Examples of good vs. poor naming:**
- ❌ Poor: `test1`, `test_service`, `test_method`
- ✅ Good: `test_generate_cv_with_valid_artifacts_returns_cv`
- ✅ Good: `test_generate_cv_with_empty_artifacts_raises_error`

### Pitfall 5: Missing Edge Cases

**Problem:** Tests only cover happy path

**Root Causes:**
- Writing tests after code (tests validate existing behavior only)
- Not thinking through error scenarios
- Incomplete acceptance criteria in FEATURE spec

**Solutions:**
1. Write tests first (TDD): Forces thinking through edge cases before implementation
2. Use boundary value analysis: Test min, max, empty, null values
3. Think about error cases: What can go wrong? What inputs are invalid?
4. Review acceptance criteria: Ensure FEATURE spec covers error scenarios

### Pitfall 6: Not Mocking External Dependencies

**Problem:** Unit tests make real database/API calls

**Root Causes:**
- Not understanding what to mock
- Missing mock utilities in project
- Complexity of setting up mocks
- Tests categorized as "unit" but actually integration tests

**Solutions:**
1. Identify external dependencies: Database, APIs, file system, network, time
2. Use project mock utilities: Learn project-standard mocking patterns
3. Mock at service boundaries: Mock external services, not internal classes
4. Recategorize if needed: If test requires database, it's an integration test

### Pitfall 7: Tests Don't Fail When They Should

**Problem:** Tests pass even when code is broken

**Root Causes:**
- Tautological tests (testing the same logic twice)
- Missing assertions
- Incorrect assertions (asserting wrong thing)
- Mocks too permissive (accept any input)

**Solutions:**
1. Temporarily break code: Verify test fails when implementation is broken
2. Review assertions: Ensure testing actual behavior, not test setup
3. Strengthen mocks: Make mocks stricter to catch incorrect calls
4. Delete useless tests: If test doesn't provide value, remove it

## See Also

- **Project Implementation:** See your project's `docs/testing/` directory for:
  - Framework-specific test decorators and tagging syntax
  - Stub creation code examples in your language/framework
  - Mocking utilities and patterns for your stack
  - Test execution commands for your test runner
  - Detailed quality validation examples with code
- **TDD Policy:** See `rules/06-tdd/policy.md` for mandatory TDD requirements and quality gates
