# Hybrid Test-Driven Development (Hybrid TDD) — Implementation Mandate

## Purpose
This rule mandates a Hybrid Test-Driven Development approach for all feature implementation, bug fixes, and refactoring. **Unit tests** are written before implementation code (RED phase), and **integration tests** are written during refactoring (REFACTOR phase) to balance fast feedback with comprehensive coverage.

## Core Hybrid TDD Cycle: Red → Green → Refactor

### 1. RED Phase (Stage F: Write Unit Tests First)
- **Two Substeps:**
  1. **Test Cleanup (using Stage B test update checklist)**
     - Update deprecated tests to align with new feature design
     - Remove obsolete tests that are no longer relevant
     - Document why tests were removed/updated (in commit message or comments)
     - Ensure remaining tests still pass before proceeding
  2. **Write New Failing Unit Tests**
     - **Write failing unit test(s)** that define expected behavior and clarify requirements
     - **Focus on business logic and API design** - defer integration tests to refactor phase
     - Tests should **use `NotImplementedError`** because the functionality doesn't exist yet
     - Each test should be **minimal** and test **one thing**
     - **Use meaningful function names** that express intent clearly
     - **Include helper descriptions** to clarify the expected behavior
     - Consider **sync v.s. async**. If not sure, add to description
     - Tests should serve as **executable specifications** that clarify requirements
     - **Mock all external dependencies** (database, APIs, file system)

### 2. GREEN Phase (Stage G: Implement to Pass Unit Tests)
- Write **minimal code** to make **unit tests** pass
- Focus on making tests green, not on perfect code
- Resist the urge to write more than necessary
- If tests reveal missing requirements, add more failing unit tests first
- **Integration tests are not required yet** - defer to refactor phase

### 3. REFACTOR Phase (Stage H: Write Integration Tests & Refactor)
- **FIRST:** Write integration tests for I/O boundaries (see "When Integration Tests Are Mandatory" below)
- Pass integration tests - implement any missing integration code
- **THEN:** Refactor code while keeping all tests (unit + integration) green
- Remove duplication, improve naming, optimize algorithms
- Add error handling and edge cases
- Enhance documentation
- All tests act as safety net during refactoring

## Test Types and When to Use Them

### Unit Tests (Always Required - RED Phase)
- **Scope:** Single function, method, or class
- **Speed:** Must run in milliseconds
- **Dependencies:** Mock all external dependencies (database, APIs, file system)
- **Coverage Target:** 80%+ for business logic
- **When:** Write in RED phase (Stage F) before implementation
- **Purpose:** Fast feedback, API design clarification, executable specifications

### Integration Tests (Required for I/O - REFACTOR Phase)
- **Scope:** Component interactions, API endpoints, database operations, external service calls
- **Speed:** Seconds acceptable
- **Dependencies:** Use test database, real services where feasible
- **Coverage Target:** All critical paths involving I/O
- **When:** Write in REFACTOR phase (Stage H) before refactoring
- **Purpose:** Verify component interactions, catch integration issues, validate end-to-end flows

### When Integration Tests Are Mandatory

Integration tests **MUST** be written during Stage H (REFACTOR) for:
- ✅ **API Endpoints:** All REST/GraphQL endpoints
- ✅ **Database Operations:** Any code that reads/writes to database
- ✅ **External Service Calls:** OpenAI/Anthropic APIs, third-party services
- ✅ **File System Operations:** Document uploads, PDF generation, file processing
- ✅ **LLM Pipelines:** End-to-end prompt → LLM → response flows
- ✅ **Authentication Flows:** Login, OAuth, JWT validation
- ✅ **Background Tasks:** Celery tasks, async processing

Integration tests are **OPTIONAL** for:
- ❌ Pure business logic with no I/O
- ❌ Data transformation functions (if unit tested)
- ❌ Utility/helper functions with no external dependencies

## Test Writing Best Practices
    
### Test Naming Conventions
```python
# Format: test_<what>_<condition>_<expected_result>

test_authentication_with_valid_token_returns_user()
test_payment_with_insufficient_funds_raises_error()
test_search_with_empty_query_returns_empty_list()
```

### Test Data Management
- Use **factories** or **fixtures** for test data
- Avoid hardcoded values except for specific test cases
- Clean up test data after each test (use teardown/cleanup)
- Use **deterministic** data (avoid random without seeds)

### RED Phase Implementation Strategy

When writing failing tests in the RED phase, focus on **requirement clarification** and **API design**:

```python
def optimize_cv_for_ats(cv_content, job_requirements, optimization_level="standard"):
    """
    Optimize CV content for ATS (Applicant Tracking System) compatibility

    Args:
        cv_content: CV content to optimize
        job_requirements: Job description and requirements
        optimization_level: "conservative", "standard", or "aggressive"

    Returns:
        OptimizedCV with improved ATS score and change details
    """
    raise NotImplementedError(
        "optimize_cv_for_ats: Need to implement ATS optimization logic. "
        "Should analyze job requirements, identify keywords, and suggest content improvements. "
        "Expected to return OptimizedCV(ats_score, keyword_matches, optimization_changes)"
    )
```

**Key RED Phase Principles:**
- **Think API-first:** Function names, parameters, return types
- **Use descriptive assertions** that read like requirements
- **NotImplementedError messages** should guide implementation
- **Test names** should clearly express the business requirement
- **Helper functions** should have clear, single responsibilities
- **Data structures** should be designed through test usage


## Integration with Workflow Stages

### Stage E (Plan/FEATURE) → Stage F (Write Unit Tests)
- Review acceptance criteria in FEATURE spec
- Review **Stage B test update checklist** from FEATURE spec
- Transform each criterion into one or more failing **unit tests**
- Focus on business logic and API design
- Defer integration test planning to Stage H

### Stage F (Write Unit Tests) → Stage G (Implement)
- **Substep 1 (Test Cleanup) complete:**
  - All deprecated tests from Stage B checklist are updated/removed
  - Documentation added for why tests were changed
  - Remaining existing tests still pass
- **Substep 2 (New Failing Tests) complete:**
  - All **new unit tests** are failing (red) and use meaningful function names
  - Tests define the business logic specification with descriptive assertions
  - Functions use `NotImplementedError` with clear messages about expected behavior
  - API design is clarified through test usage (function names, parameters, return types)
  - All external dependencies are mocked
  - No implementation code exists yet

### Stage G (Implement) → Stage H (Write Integration Tests & Refactor)
- All **unit tests** must be passing (green)
- Code may be messy but functional
- Ready for integration testing and cleanup

### During Stage H (Write Integration Tests & Refactor)
1. **First substep:** Write integration tests for I/O boundaries (see mandatory list above)
2. **Second substep:** Implement any missing integration code to pass integration tests
3. **Third substep:** Refactor code while keeping all tests (unit + integration) green
4. Add tests for discovered edge cases
5. Improve test quality and readability

## Measuring TDD Effectiveness

### Metrics to Track
- **Coverage:** Aim for 80%+ on business logic
- **Test Runtime:** Keep under 5 minutes for unit tests
- **Defect Rate:** Should decrease over time
- **Test-to-Code Ratio:** Healthy projects have 1:1 to 2:1

### Signs of Good TDD Practice
- ✅ Small, frequent commits (red → green → refactor)
- ✅ Tests document the system behavior
- ✅ Refactoring happens without fear
- ✅ Bugs result in new tests first
- ✅ Tests run quickly and frequently

### Red Flags
- 🚩 Tests written days after code
- 🚩 Tests that never fail
- 🚩 Commented out or skipped tests
- 🚩 Tests that break when refactoring
- 🚩 Low confidence in test suite