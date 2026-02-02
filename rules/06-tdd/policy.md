# Hybrid Test-Driven Development (Hybrid TDD) — Implementation Mandate

## Purpose

This rule mandates a Hybrid Test-Driven Development approach for all feature implementation, bug fixes, and refactoring. **Unit tests** are written before implementation code (RED phase), and **integration tests** are written during refactoring (REFACTOR phase) to balance fast feedback with comprehensive coverage.

## Core Hybrid TDD Cycle: Red → Green → Refactor

### 1. RED Phase (Stage F: Write Unit Tests First)

**Mandatory Steps:**
1. **Test Cleanup** (using Stage B test update checklist)
   - Update deprecated tests to align with new feature design
   - Remove obsolete tests with justification
   - Ensure remaining tests still pass

2. **Create Implementation Stubs** (from FEATURE spec API signatures)
   - Extract function/class signatures from FEATURE spec "API Design" section
   - Create stub files with exact function names, parameters, return types from spec
   - Use "not implemented" markers with helpful messages
   - Verify stubs are importable
   - **If naming issues discovered:** STOP → Update FEATURE spec → Resume Stage F

3. **Write New Failing Unit Tests**
   - Import stubs to ensure names resolve correctly
   - Write tests using exact signatures from FEATURE spec
   - Tests must fail with clear "not implemented" errors (not import errors)
   - All external dependencies mocked
   - Tests serve as executable specifications
   - Apply proper test categorization (speed/scope + module)

**Requirements:**
- Function signatures must match FEATURE spec contracts
- Tests must specify expected behavior with descriptive assertions
- Mock all external dependencies (database, APIs, file system)

**Implementation Details:** See project docs/testing/ for stub creation examples and step-by-step workflows

### 2. GREEN Phase (Stage G: Implement to Pass Unit Tests)

**Requirements:**
- Write **minimal code** to make **unit tests** pass
- Focus on making tests green, not on perfect code
- Resist the urge to write more than necessary
- **If implementation reveals contract changes** (API signatures, database schemas, external interfaces):
  - **STOP immediately** - Do not continue implementation
  - Follow "Stage G.1: Handling Design Changes During Implementation" protocol in `rules/00-workflow.md`
  - Update SPEC → Update tests → Resume implementation
- If tests reveal missing requirements (not contract changes), add more failing unit tests first
- **Integration tests are not required yet** - defer to refactor phase

### 3. REFACTOR Phase (Stage H: Write Integration Tests & Refactor)

**Mandatory Steps:**
1. Write integration tests for I/O boundaries (see "When Integration Tests Are Mandatory" below)
2. Pass integration tests - implement any missing integration code
3. Refactor code while keeping all tests (unit + integration) green
4. **Complete Stage H.4 Test Quality Validation checklist** (see below)

**Refactoring Activities:**
- Remove duplication, improve naming, optimize algorithms
- Add error handling and edge cases
- Enhance documentation
- All tests act as safety net during refactoring

## Test Types and When to Use Them

### Unit Tests (Always Required - RED Phase)

- **Scope:** Single function, method, or class
- **Speed:** Must run in milliseconds (<1s per test)
- **Dependencies:** Mock all external dependencies (database, APIs, file system)
- **Coverage Target:** 80%+ for business logic
- **When:** Write in RED phase (Stage F) before implementation
- **Purpose:** Fast feedback, API design clarification, executable specifications

### Integration Tests (Required for I/O - REFACTOR Phase)

- **Scope:** Component interactions, API endpoints, database operations, external service calls
- **Speed:** Seconds acceptable (<5s per test)
- **Dependencies:** Use test database, mocked external services
- **Coverage Target:** All critical paths involving I/O
- **When:** Write in REFACTOR phase (Stage H) before refactoring
- **Purpose:** Verify component interactions, catch integration issues, validate end-to-end flows

### When Integration Tests Are Mandatory

Integration tests **MUST** be written during Stage H (REFACTOR) for:
- **API Endpoints:** All REST/GraphQL endpoints
- **Database Operations:** Any code that reads/writes to database
- **External Service Calls:** Third-party APIs, external services
- **File System Operations:** Document uploads, PDF generation, file processing
- **LLM Pipelines:** End-to-end prompt → LLM → response flows
- **Authentication Flows:** Login, OAuth, JWT validation
- **Background Tasks:** Async processing, queued jobs

Integration tests are **OPTIONAL** for:
- Pure business logic with no I/O
- Data transformation functions (if unit tested)
- Utility/helper functions with no external dependencies

## Test Writing Requirements

### Test Naming Conventions

- **Format:** `test_<what>_<condition>_<expected_result>`
- **Examples:**
  - `test_authentication_with_valid_token_returns_user()`
  - `test_payment_with_insufficient_funds_raises_error()`
  - `test_search_with_empty_query_returns_empty_list()`

### Test Data Management

- Use **factories** or **fixtures** for test data
- Avoid hardcoded values except for specific test cases
- Clean up test data after each test (use teardown/cleanup)
- Use **deterministic** data (avoid random without seeds)

### Test Categorization Requirements

**Mandatory Test Categories:**

1. **Speed/Scope (mandatory - choose one):**
   - **Unit Tests (fast):** Single function/method/class, all dependencies mocked, run in milliseconds
   - **Integration Tests (medium):** Component interactions, database operations, mocked external APIs, run in seconds
   - **End-to-End Tests (slow):** Full workflows, multiple components, may use real services, run in seconds to minutes
   - **Real API Tests (slow):** Makes real external API calls, requires API keys, costs money

2. **Module/Package (mandatory):**
   - Tag tests with the module/package they belong to (e.g., 'accounts', 'artifacts', 'generation', 'api')

3. **Feature (optional but recommended):**
   - Tag tests with feature identifiers for feature-specific test runs (e.g., 'ft-123', 'enrichment')

**Decision Criteria for Categorization:**

```
Does test make external API calls (real network requests)?
├─ YES (real API) → Category: Real API Tests (slow)
└─ NO → Does test use database/filesystem/external services?
    ├─ YES → Category: Integration Tests (medium)
    └─ NO → Category: Unit Tests (fast)
```

**Validation Requirements (Stage F exit requirement):**
- All tests have appropriate category tags (speed + module)
- Speed category matches test characteristics:
  - **Unit (fast)** → All external dependencies mocked, no database, no file I/O, no network
  - **Integration (medium)** → Uses test database or mocked external services
  - **E2E (slow)** → Full workflow, multiple components integrated
  - **Real API (slow)** → Makes real external API calls
- Module/package tags match file location
- No real API calls in tests tagged as "unit" or "fast"

**Implementation Details:** See project docs/testing/ for framework-specific categorization syntax and tagging examples

### Proper Mocking Requirements (Unit Tests)

- Mock all external dependencies (database, APIs, file system, network)
- Use project-standard mock utilities
- Mock setup/teardown properly handled (patches started and stopped)
- Mock configurations realistic (match actual API behavior)
- No real API calls in tests tagged as "unit" or "fast"

**Implementation Details:** See project docs/testing/ for mocking utilities and patterns

### Mocking Strategy by Test Type

Different test types require different mocking strategies. Understanding what to mock (and what not to mock) is critical for test reliability and speed.

**Mocking Decision Matrix:**

| Test Type | Database | Internal APIs/Services | External APIs | File System | Network |
|-----------|----------|------------------------|---------------|-------------|---------|
| **Unit** | Mock | Mock | Mock | Mock | Mock |
| **Integration** | Real (test environment) | Real | Mock | Real (test environment) | Mock |
| **End-to-End** | Real (test environment) | Real | Mock (if expensive) | Real (test environment) | Mock (if expensive) |
| **Real API** | Real | Real | Real | Real | Real |

**Decision Criteria:**

```
What should I mock for this dependency?
│
├─ Is it an external service (third-party API, payment processor, email)?
│  ├─ Unit test → ALWAYS mock
│  ├─ Integration test → ALWAYS mock
│  ├─ E2E test → Mock if expensive/unreliable
│  └─ Real API test → NEVER mock
│
├─ Is it my own application component (database, service, API)?
│  ├─ Unit test → ALWAYS mock
│  ├─ Integration test → Use REAL (test environment)
│  ├─ E2E test → Use REAL (test environment)
│  └─ Real API test → Use REAL
│
└─ Is it infrastructure (file system, time, randomness)?
   ├─ Unit test → ALWAYS mock
   ├─ Integration test → Use REAL (test environment)
   ├─ E2E test → Use REAL (test environment)
   └─ Real API test → Use REAL
```

**Test Pyramid Principle:**

Maintain this distribution for optimal speed and coverage:
- **70% Unit Tests:** Fast feedback (milliseconds), all dependencies mocked
- **20% Integration Tests:** Moderate speed (seconds), external dependencies mocked
- **9% End-to-End Tests:** Slower (seconds to minutes), expensive external services mocked
- **1% Real API Tests:** Slowest/expensive, no mocking (manual or scheduled runs)

**Key Principles:**
- **Unit tests:** Mock everything external to enable fast, isolated testing
- **Integration tests:** Use real internal components, mock only external services
- **E2E tests:** Use real application stack, mock only expensive/unreliable external services
- **Real API tests:** No mocking, validate actual external service behavior

## Integration with Workflow Stages

### Stage E (FEATURE) → Stage F (Write Unit Tests)

- Review acceptance criteria in FEATURE spec
- Review **Stage B test update checklist** from FEATURE spec
- Create implementation stubs from FEATURE spec API Design section
- Transform each criterion into one or more failing **unit tests**
- Focus on business logic and API design

### Stage F (Write Unit Tests) → Stage G (Implement)

**Exit Criteria:**
- All deprecated tests from Stage B checklist are updated/removed with justification
- Implementation stubs created with correct function signatures from FEATURE spec
- All **new unit tests** are failing (red) with "not implemented" errors
- Tests use actual implementation names from FEATURE spec (not conceptual doc names)
- Tests have proper categorization tags
- Tests define behavior with descriptive assertions
- All external dependencies are mocked
- No implementation code exists yet

### Stage G (Implement) → Stage H (Write Integration Tests & Refactor)

**Exit Criteria:**
- All **unit tests** must be passing (green)
- Code may be messy but functional
- No regressions in existing tests
- Code follows established patterns from Stage B discovery

### During Stage H (Write Integration Tests & Refactor)

**Four Substeps:**
1. Write integration tests for I/O boundaries (see mandatory list above) with proper categorization tags
2. Pass integration tests - implement any missing integration code
3. Refactor code while keeping all tests (unit + integration) green
4. **Complete Stage H.4 Test Quality Validation checklist** (see below)

## Test Execution Strategy

### Execution Requirements by Stage

**Stage F → G (Unit Tests):**
- Run new test file first (fast feedback - seconds)
- Then run all fast unit tests (full regression - minutes)

**Stage H (Integration Tests):**
- Run new integration test first (fast feedback - seconds)
- Then run all integration tests for affected module (minutes)
- Finally run full integration suite before commit/PR (5-10 minutes)

**Full Regression Required:**
- Before committing code
- Before creating/updating PR
- Before deployment
- In CI/CD pipeline

### Performance Requirements

- **Unit tests:** <1s per test (with proper mocking)
- **Integration tests:** <5s per test
- **Full unit suite:** <3 minutes
- **Full integration suite:** <10 minutes

**Implementation Details:** See project docs/testing/ for test execution commands, framework-specific tips, and time-saving best practices

## Stage H.4: Test Quality Validation (Mandatory Exit Checklist)

### Purpose

Validate test quality before completing Stage H to ensure new tests are well-organized, useful, and maintainable.

### Quality Dimensions

**1. Test Organization:**
- File structure and naming conventions followed
- Test classes/suites have descriptive names
- Test methods use clear naming pattern
- Related tests grouped in same class/suite
- Test isolation (each test can run independently)
- Clear separation between unit and integration tests

**2. Test Usefulness:**
- Tests based on acceptance criteria from FEATURE spec
- All acceptance criteria have corresponding tests
- Tests validate behavior, not implementation details
- Happy path, edge cases, and error cases tested
- No duplicate tests

**3. Test Code Quality:**
- All external dependencies mocked in unit tests
- Mock setup/teardown properly handled
- Test data uses factories/fixtures
- Arrange-Act-Assert (AAA) pattern clear
- Assertion messages explain what failed
- No commented-out code or skipped tests without justification

**4. Test Categorization:**
- All tests have appropriate category tags (speed + module)
- Speed category matches test characteristics
- No real API calls in tests tagged "unit" or "fast"
- Tags verified by running tests in isolation

**5. Performance & Reliability:**
- Unit tests run quickly (<1s per test)
- Integration tests reasonable (<5s per test)
- Tests pass consistently (run 3-5 times, all pass)
- No flaky tests (timing-dependent, random failures)
- Tests don't depend on execution order

### Quality Gate Decision Matrix

Count violations across all new tests:

| Violations | Decision | Action Required |
|------------|----------|-----------------|
| 0-2 minor | **PASS** | Fix violations and proceed to next stage |
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

**Implementation Details:** See project docs/testing/ for detailed quality checklist with code examples and validation walkthroughs

## Measuring TDD Effectiveness

### Target Metrics

- **Coverage:** Aim for 80%+ on business logic
- **Test Runtime:** Keep under 5 minutes for unit tests, under 10 minutes for integration tests
- **Test-to-Code Ratio:** Healthy projects have 1:1 to 2:1
- **Defect Rate:** Should decrease over time

### Signs of Good TDD Practice

- Small, frequent commits (red → green → refactor)
- Tests document the system behavior
- Refactoring happens without fear
- Bugs result in new tests first
- Tests run quickly and frequently

### Red Flags

- Tests written days after code
- Tests that never fail
- Commented out or skipped tests
- Tests that break when refactoring
- Low confidence in test suite

## See Also

- **Project Implementation:** See your project's `docs/testing/` directory for:
  - Framework-specific test decorators and tagging syntax
  - Stub creation code examples
  - Mocking utilities and patterns
  - Test execution commands
  - Detailed quality validation examples
- **TDD Workflow Guide:** See `rules/06-tdd/guide.md` for conceptual TDD workflow and decision-making guidance
