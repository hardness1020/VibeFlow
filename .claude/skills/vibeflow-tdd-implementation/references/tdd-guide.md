# TDD Workflow Guide

Step-by-step guidance for implementing features using TDD.

## Stage F: RED Phase

### Step 1: Review Feature Spec

Before writing any code:

1. Open the Feature Spec (`docs/features/ft-<ID>-<slug>.md`)
2. Review the **API Design** section
3. Note exact function names, parameters, return types
4. Review **Acceptance Criteria** for test cases

### Step 2: Handle Deprecated Tests

If Stage B discovery identified tests to update/remove:

```bash
# Check Stage B test update checklist
# For each test marked UPDATE or REMOVE:
```

1. **UPDATE tests**: Modify to align with new design
2. **REMOVE tests**: Delete with commit message explaining why
3. Verify remaining tests still pass

### Step 3: Create Implementation Stubs

Create files with function signatures from Feature Spec:

**Python Example:**
```python
# service/bullet_verification_service.py

from typing import List
from dataclasses import dataclass

@dataclass
class VerificationResult:
    """Result of bullet verification."""
    passed: bool
    confidence: float
    issues: List[str]


class BulletVerificationService:
    """
    Verify generated bullets against source artifacts.

    Implementation for ft-030: Anti-hallucination verification.
    """

    def verify_bullet_set(
        self,
        bullets: List[BulletPoint],
        sources: List[Artifact],
        confidence_threshold: float = 0.8
    ) -> VerificationResult:
        """
        Verify bullet set against sources.

        Args:
            bullets: Bullets to verify
            sources: Source artifacts
            confidence_threshold: Minimum confidence (default 0.8)

        Returns:
            VerificationResult with pass/fail and details
        """
        raise NotImplementedError(
            "BulletVerificationService.verify_bullet_set not implemented. "
            "See docs/features/ft-030-anti-hallucination.md"
        )
```

### Step 4: Write Failing Unit Tests

```python
# tests/test_bullet_verification_service.py

import pytest
from unittest.mock import Mock, patch
from service.bullet_verification_service import (
    BulletVerificationService,
    VerificationResult
)


class TestBulletVerificationService:
    """Tests for BulletVerificationService.

    Feature: ft-030 Anti-hallucination verification
    """

    @pytest.fixture
    def service(self):
        return BulletVerificationService()

    @pytest.fixture
    def mock_bullets(self):
        return [Mock(content="Bullet 1"), Mock(content="Bullet 2")]

    @pytest.fixture
    def mock_sources(self):
        return [Mock(content="Source content")]

    @pytest.mark.unit
    @pytest.mark.generation
    def test_verify_bullet_set_with_valid_sources_returns_result(
        self, service, mock_bullets, mock_sources
    ):
        """Verify bullets returns VerificationResult."""
        # Arrange
        # (using fixtures)

        # Act
        result = service.verify_bullet_set(mock_bullets, mock_sources)

        # Assert
        assert isinstance(result, VerificationResult)
        assert hasattr(result, 'passed')
        assert hasattr(result, 'confidence')

    @pytest.mark.unit
    @pytest.mark.generation
    def test_verify_bullet_set_with_empty_sources_raises_error(
        self, service, mock_bullets
    ):
        """Empty sources raises InsufficientSourcesError."""
        with pytest.raises(InsufficientSourcesError):
            service.verify_bullet_set(mock_bullets, [])

    @pytest.mark.unit
    @pytest.mark.generation
    def test_verify_bullet_set_with_high_confidence_passes(
        self, service, mock_bullets, mock_sources
    ):
        """High confidence results pass verification."""
        result = service.verify_bullet_set(
            mock_bullets, mock_sources, confidence_threshold=0.8
        )
        assert result.passed is True
        assert result.confidence >= 0.8
```

### Step 5: Verify Tests Fail Correctly

```bash
# Run tests - should FAIL with NotImplementedError
pytest tests/test_bullet_verification_service.py -v

# Expected output:
# FAILED - NotImplementedError: ... not implemented
```

**Checkpoint #3**: Tests fail with NotImplementedError (not import errors)

---

## Stage G: GREEN Phase

### Step 1: Implement Minimal Code

Focus on making tests pass, not perfect code:

```python
def verify_bullet_set(
    self,
    bullets: List[BulletPoint],
    sources: List[Artifact],
    confidence_threshold: float = 0.8
) -> VerificationResult:
    """Verify bullet set against sources."""
    if not sources:
        raise InsufficientSourcesError("Sources list cannot be empty")

    # Minimal implementation to pass tests
    confidence = self._calculate_confidence(bullets, sources)

    return VerificationResult(
        passed=confidence >= confidence_threshold,
        confidence=confidence,
        issues=[]
    )
```

### Step 2: Check for Contract Changes

If you discover you need to change:
- Function signatures
- API endpoints
- Database schemas
- External dependencies

**STOP** and follow Stage G.1 Protocol.

### Step 3: Run Tests

```bash
pytest tests/test_bullet_verification_service.py -v

# Expected: ALL PASS
```

---

## Stage G.1: Design Changes Protocol

If implementation reveals contract changes:

### 1. STOP Immediately

Do not continue implementation. Commit current work as WIP if needed.

### 2. Document the Issue

Note what change is needed and why.

### 3. Update SPEC

- Update affected SPEC file
- Increment version
- Update architecture diagram if topology changed

### 4. Update Feature Spec

- Update API Design section
- Update any affected signatures

### 5. Update Tests

- Update test expectations
- May need to add new tests
- Tests should be back to RED (failing)

### 6. Resume Implementation

Return to Stage G with updated contracts.

---

## Stage H: REFACTOR Phase

### Step 1: Write Integration Tests

For I/O operations identified in feature:

```python
# tests/integration/test_bullet_verification_integration.py

import pytest
from django.test import TestCase


@pytest.mark.integration
@pytest.mark.generation
class TestBulletVerificationIntegration(TestCase):
    """Integration tests for bullet verification.

    Tests real database operations and mocked LLM calls.
    """

    @pytest.fixture
    def real_artifacts(self, db):
        """Create real artifacts in test database."""
        return Artifact.objects.create(...)

    def test_verify_bullets_with_database_sources(
        self, real_artifacts
    ):
        """Verify with real database sources."""
        service = BulletVerificationService()
        bullets = create_test_bullets()

        result = service.verify_bullet_set(bullets, [real_artifacts])

        assert result.passed
        # Verify database state if applicable
```

### Step 2: Pass Integration Tests

Implement any missing integration code. Run tests.

### Step 3: Refactor

With all tests green:

- Remove code duplication
- Improve naming
- Optimize algorithms
- Enhance error handling
- Add documentation

Run tests after each refactor to ensure they stay green.

### Step 4: Quality Validation (H.4)

Complete the checklist:

**Organization:**
- [ ] Files follow naming conventions
- [ ] Test classes have descriptive names
- [ ] Test methods use `test_<what>_<condition>_<expected>`
- [ ] Related tests grouped
- [ ] Unit/integration separated

**Usefulness:**
- [ ] Tests based on acceptance criteria
- [ ] All acceptance criteria covered
- [ ] Tests validate behavior
- [ ] Happy path, edge cases, errors tested

**Code Quality:**
- [ ] External deps mocked in unit tests
- [ ] Test data uses factories/fixtures
- [ ] AAA pattern clear
- [ ] No commented/skipped tests without reason

**Categorization:**
- [ ] Speed/scope tags on all tests
- [ ] Module tags on all tests
- [ ] No real API calls in "unit" tests

**Reliability:**
- [ ] Unit tests < 1s each
- [ ] Integration tests < 5s each
- [ ] Run 3x - all pass consistently

Count violations and check quality gate:
- 0-2 minor: PASS
- 3-5: CONDITIONAL
- 6+ OR 2+ major: FAIL

---

## Common Pitfalls

### 1. Tests Don't Fail

**Problem:** Tests pass before implementation
**Fix:** Ensure stubs raise NotImplementedError

### 2. Import Errors

**Problem:** Tests fail with import errors, not NotImplementedError
**Fix:** Create stub files before writing tests

### 3. Tests Coupled to Implementation

**Problem:** Tests break when refactoring
**Fix:** Test behavior (inputs → outputs), not internal details

### 4. Slow Unit Tests

**Problem:** Unit tests take seconds
**Fix:** Mock all external dependencies

### 5. Flaky Tests

**Problem:** Tests pass/fail randomly
**Fix:** Use deterministic data, don't share mutable state
