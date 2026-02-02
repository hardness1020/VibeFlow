# Discovery: <ID> - <Title>

**ID:** <ID> (e.g., 030, 031, 032)
**Type:** Feature | Fix | Chore
**Date:** YYYY-MM-DD
**Size Track:** Micro | Small | Medium | Large
**Author:** <name> or "Claude Code"

## Summary

[1-2 paragraph summary of what was discovered]

[Example:]
This discovery analyzed the codebase before implementing anti-hallucination verification for bullet generation. Key findings: identified reusable BaseLLMService pattern from llm_services/, validated spec-llm.md accuracy (HIGH confidence with minor pricing drift), and created test update checklist for 35 affected tests. Risk level: MEDIUM due to new service with 0% initial coverage. Recommendation: Proceed to Stage C with comprehensive unit test plan.

---

## Phase 0: Spec Discovery Results

### Affected Specs

[List all specs that relate to this change, with versions and scope]

[Example:]
- **spec-llm.md** (v4.2.0) - LLM service interfaces, model registry, circuit breaker patterns
- **spec-api.md** (v4.2.0) - Backend REST API endpoints and schemas
- **spec-system.md** (v1.4.0) - System topology and service relationships
- **spec-cv-generation.md** (v1.0.0) - CV generation pipeline and bullet generation

### Spec-Defined Patterns to Follow

[Extract contracts, interfaces, and configurations from specs]

**Contracts to Follow:**
[Example:]
- API endpoints: POST /api/v1/generations/ (request/response schema from spec-api.md)
- Data schemas: BulletPoint model (fields: content, confidence, source_id)
- Event definitions: [if applicable]

**Service Layer Structure:**
[Example:]
- Layer assignment: generation/services/core/ (business logic layer)
- Parent class: BaseLLMService (from llm_services/services/base/base_service.py)
- Interface signatures:
  ```python
  class BaseLLMService:
      async def execute_with_retry(self, task: Task) -> Result:
          """Execute task with retry logic and circuit breaker."""
  ```
- Dependencies: CircuitBreaker, PerformanceTracker (reliability layer)

**Configuration Schemas:**
[Example:]
- Model registry: Add to MODEL_CONFIGS dict in model_registry.py
- Required fields: model_id, provider, context_window, pricing, temperature

### Spec Confidence Assessment

[Assess risk level of spec accuracy - do we trust these specs?]

[Example:]
- **spec-llm.md** (v4.2.0): Last verified 2025-11-04, confidence HIGH 🟢
  - Trust level: Can rely on interface signatures and schemas
  - Known drift areas: Model pricing may need verification (noted in spec)
  - Risk: LOW - Safe to use for design

- **spec-api.md** (v4.2.0): Last verified 2025-10-15, confidence MEDIUM 🟡
  - Trust level: Validate endpoint counts and recent schema changes
  - Known drift areas: Recent migrations may have added fields
  - Risk: MEDIUM - Needs validation in Phase 1

- **spec-system.md** (v1.4.0): No last verified date, confidence LOW 🔴
  - Trust level: Validate component topology before relying on it
  - Known drift areas: Service count, deployment architecture
  - Risk: HIGH - Requires thorough validation in Phase 1

### Spec Update Checklist (for Stage C)

[Based on change-control tripwires, identify which specs need updates]

[Example:]
- [ ] **spec-llm.md** → Likely v4.2.0 → v4.3.0 (non-breaking)
  - Reason: Adding new BulletVerificationService interface
  - Update sections: Service Layer Architecture (add interface signature)
  - Version bump: Minor (new interface, no breaking changes to existing contracts)
  - Estimated lines added: ~50 lines (interface + examples)

- [ ] **spec-api.md** → Likely v4.2.0 → v5.0.0 (breaking)
  - Reason: Adding review workflow endpoints with new response schema
  - Update sections: API Endpoints (add POST /api/v1/bullets/{id}/review/)
  - Version bump: Major (response schema adds required 'confidence' field)
  - Estimated lines added: ~30 lines (endpoint + schema)

- [ ] **spec-cv-generation.md** → Likely v1.0.0 → v2.0.0 (breaking)
  - Reason: Integrate verification into generation pipeline
  - Update sections: Pipeline Architecture (add verification step)
  - Version bump: Major (changes generation flow topology)
  - Estimated lines added: ~40 lines (flow diagram + description)

---

## Phase 1: Spec-Code Validation Results

### Discrepancies Found

[Document all spec-code mismatches discovered during validation]

[Example:]
1. **spec-api.md** (Line 234): Claims 47 endpoints, actual count is 51
   - Impact: MINOR - 4 undocumented endpoints added in recent PRs
   - Affected files: generation/urls.py (+2), export/urls.py (+2)
   - Root cause: Endpoints added without spec update
   - Action: Update spec endpoint count and add missing endpoint documentation

2. **spec-llm.md** (Line 797): Model pricing outdated for GPT-4
   - Impact: MINOR - Pricing info is $15/$30, actual OpenAI pricing is $10/$20
   - Affected files: model_registry.py (has correct values)
   - Root cause: OpenAI changed pricing, spec not updated
   - Action: Update model_registry.py pricing table in spec

3. **spec-database-schema.md**: Missing 'confidence' field on BulletPoint model
   - Impact: MEDIUM - New field added in migration 0024_add_confidence_field
   - Affected files: generation/models.py (BulletPoint model)
   - Root cause: Migration created without spec update
   - Action: Update ERD diagram and BulletPoint table definition

4. **spec-system.md**: Service count shows 5 services, actual count is 7
   - Impact: MEDIUM - Component inventory outdated
   - Affected files: Multiple (2 new services: verification, enrichment)
   - Root cause: Spec hasn't been updated since v1.4.0
   - Action: Update component inventory table and topology diagram

### Spec Confidence Assessment (Post-Validation)

[Update confidence levels after validation]

[Example:]
- **spec-llm.md** (v4.2.0): ⭐⭐⭐⭐ HIGH (4/5)
  - Status: Interfaces match code exactly, minor pricing drift only
  - Last validated: Today (2025-11-06)
  - Recommendation: Safe to use for design, update pricing in Stage C
  - Action: Use interface signatures as-is, verify pricing values

- **spec-api.md** (v4.2.0): ⭐⭐⭐ MEDIUM (3/5)
  - Status: Endpoint count drift, schemas generally accurate
  - Last validated: Today (2025-11-06)
  - Recommendation: Use with caution, manually verify endpoint list
  - Action: Cross-check endpoint schemas before relying on them

- **spec-database-schema.md**: ⭐⭐⭐⭐ HIGH (4/5)
  - Status: Missing recent field additions, but ERD structure accurate
  - Last validated: Today (2025-11-06)
  - Recommendation: Safe to use for schema design, add missing fields
  - Action: Use ERD as base, validate recent migrations for new fields

- **spec-system.md** (v1.4.0): ⭐⭐ LOW (2/5)
  - Status: Component count outdated, topology needs verification
  - Last validated: Today (2025-11-06)
  - Recommendation: Use for high-level understanding only, validate details
  - Action: Verify component relationships before architectural decisions

### Required Spec Updates (Before Stage C)

[Prioritize spec updates by urgency]

[Example:]
🔴 **CRITICAL - Update BEFORE Stage C design:**
- NONE (all critical contracts are documented accurately)

🟡 **HIGH - Update DURING Stage C:**
- spec-api.md: Add 4 missing endpoints, correct endpoint count from 47 to 51
- spec-database-schema.md: Add 'confidence' field to BulletPoint table definition
- spec-system.md: Update component inventory (5 → 7 services)

🟢 **MEDIUM - Can defer to Stage I (Spec Reconciliation):**
- spec-llm.md: Update model pricing table (cosmetic, doesn't affect design)
- spec-system.md: Update deployment architecture section (informational)

---

## Phase 2: Test Impact Analysis

### Affected Test Files

[List all test files that will be impacted by the change]

[Example:]
**Direct Impact (will definitely need updates):**
- `backend/generation/tests/test_bullet_generation.py` (35 tests)
  - Reason: Adds verification step to generation flow
- `backend/generation/tests/test_bullet_validation.py` (28 tests)
  - Reason: Validation service will call new verification service
- `backend/llm_services/tests/test_base_service.py` (42 tests)
  - Reason: New service inherits BaseLLMService patterns

**Indirect Impact (may need updates):**
- `backend/generation/tests/test_tasks.py` (12 tests, Celery tasks)
  - Reason: Tasks may need to handle verification results
- `backend/generation/tests/test_api.py` (18 tests, endpoint integration)
  - Reason: API responses will include new 'confidence' field
- `backend/export/tests/test_pdf_generation.py` (8 tests)
  - Reason: PDF export may need to display confidence indicators

**No Impact (confirmed safe):**
- `backend/accounts/tests/` (authentication tests unaffected)
- `backend/artifacts/tests/` (artifact upload tests unaffected)

### Test Update Checklist

[Categorize each test: KEEP/UPDATE/REMOVE/ADD]

[Example:]
**backend/generation/tests/test_bullet_generation.py:**
- ✅ KEEP: `test_generate_bullets_with_mock_llm` (still valid, core logic unchanged)
- ✅ KEEP: `test_generation_respects_artifact_selection` (unaffected)
- 🔄 UPDATE: `test_bullet_generation_schema` (schema adds 'confidence' field)
  - Change: Add assertion for confidence field in response
  - Estimated effort: 5 minutes
- 🔄 UPDATE: `test_generation_with_retry` (retry logic changes with verification)
  - Change: Mock verification service, verify retry behavior
  - Estimated effort: 15 minutes
- 🔄 UPDATE: `test_generation_creates_bullet_points` (BulletPoint model adds field)
  - Change: Assert confidence field saved to database
  - Estimated effort: 10 minutes
- ❌ REMOVE: `test_old_validation_logic` (replaced by new verification service)
  - Reason: Validation logic moved to separate service
  - Estimated effort: 2 minutes
- ❌ REMOVE: `test_manual_hallucination_check` (automated by verification service)
  - Reason: Manual check no longer needed
  - Estimated effort: 2 minutes
- ➕ ADD: `test_bullet_generation_with_verification` (new integration test)
  - Purpose: Test generation + verification integration
  - Estimated effort: 30 minutes
- ➕ ADD: `test_generation_handles_verification_failure` (error handling)
  - Purpose: Test graceful degradation when verification fails
  - Estimated effort: 20 minutes
- ➕ ADD: `test_confidence_score_in_response` (new feature test)
  - Purpose: Verify confidence score calculation and serialization
  - Estimated effort: 15 minutes

**backend/generation/tests/test_api.py:**
- ✅ KEEP: `test_create_generation_endpoint` (endpoint signature unchanged)
- ✅ KEEP: `test_generation_requires_authentication` (auth unchanged)
- 🔄 UPDATE: `test_generation_response_schema` (response adds confidence field)
  - Change: Assert 'confidence' field in JSON response
  - Estimated effort: 5 minutes
- ➕ ADD: `test_review_workflow_endpoint` (new endpoint for review)
  - Purpose: Test POST /api/v1/bullets/{id}/review/
  - Estimated effort: 25 minutes

**Summary:**
- Total existing tests affected: 35
- ✅ Keep: 18 tests (51%)
- 🔄 Update: 12 tests (34%)
- ❌ Remove: 5 tests (14%)
- ➕ Add: 15 new tests
- **Estimated test update effort:** ~3 hours

### Test Coverage Report

[Current test coverage of code to be modified]

[Example:]
**Current Coverage (before changes):**
```
Module                                        Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
generation/services/bullet_generation.py        613     37    94%   234-248, 401-408
generation/services/bullet_validation.py        495     54    89%   178-192, 378-402
generation/models.py                            127      0   100%
generation/views.py                             234      0   100%
generation/serializers.py                       156      3    98%   45-47
---------------------------------------------------------------------------
TOTAL                                          1625     94    94%
```

**Coverage Gaps (high-risk untested paths):**
1. `bullet_generation_service.py:234-248` - Circuit breaker error handling
   - Risk: HIGH - External API failure handling
   - Lines: 15 lines untested
   - Priority: Must test in Stage F

2. `bullet_validation_service.py:378-402` - Retry logic edge cases
   - Risk: MEDIUM - Retry exhaustion behavior
   - Lines: 25 lines untested
   - Priority: Should test in Stage F

3. `serializers.py:45-47` - Error serialization for new field
   - Risk: LOW - Simple serialization logic
   - Lines: 3 lines untested
   - Priority: Nice to have in Stage F

**Target Coverage (after changes):**
- Overall target: ≥95% (maintain or improve current 94%)
- New code target: ≥90% (all new services/features)
- Critical paths target: 100% (error handling, external APIs)

### Test Coverage Gaps to Address

[High priority areas that need new tests]

[Example:]
**High Priority (affects change, must test):**

1. **Circuit breaker error handling** (lines 234-248)
   - Gap: What happens when circuit opens during generation?
   - Tests needed:
     - `test_generation_with_circuit_open` - Verify graceful degradation
     - `test_circuit_breaker_recovery` - Verify half-open state behavior
     - `test_circuit_metrics_tracking` - Verify failure rate calculation
   - Estimated effort: 1 hour

2. **Retry logic edge cases** (lines 378-402)
   - Gap: Max retries exceeded behavior
   - Tests needed:
     - `test_retry_exhaustion_handling` - Verify error message and logging
     - `test_retry_with_different_error_types` - Verify retry vs fail-fast
     - `test_exponential_backoff_timing` - Verify backoff intervals
   - Estimated effort: 45 minutes

3. **Verification service integration** (NEW code, 0% coverage)
   - Gap: Complete new service needs comprehensive tests
   - Tests needed:
     - `test_verify_bullet_against_sources` - Core verification logic
     - `test_verification_with_multiple_sources` - Multi-source handling
     - `test_verification_confidence_calculation` - Confidence scoring
     - `test_verification_handles_llm_errors` - Error handling
     - `test_verification_performance_tracking` - Metrics tracking
   - Estimated effort: 3 hours

**Medium Priority (good to have):**

4. **Performance under load**
   - Gap: No load testing for concurrent generations
   - Tests needed:
     - `test_concurrent_bullet_generations` - 100 concurrent requests
     - `test_memory_usage_with_large_artifacts` - Memory leak detection
   - Estimated effort: 1.5 hours

5. **Database transaction handling**
   - Gap: Transaction rollback on verification failure
   - Tests needed:
     - `test_generation_rollback_on_verification_failure`
     - `test_partial_bullet_save_prevention`
   - Estimated effort: 45 minutes

**Low Priority (defer to future):**

6. **Edge case input validation**
   - Gap: Unusual input formats (emoji-only, unicode edge cases)
   - Tests needed:
     - `test_generation_with_emoji_input`
     - `test_generation_with_rtl_text`
   - Estimated effort: 30 minutes

**Total Additional Test Effort:** ~7.5 hours

---

## Phase 3: Dependency & Side Effect Mapping

### Dependency Map

[Inbound and outbound dependencies]

[Example:]
**Inbound Dependencies (what depends on this - will break if we change):**
- `generation/views.py` (API layer)
  - Imports: `from generation.services.bullet_generation_service import BulletGenerationService`
  - Usage: Creates service instance, calls `generate_bullets()`
  - Impact: HIGH - API endpoints directly depend on service interface

- `generation/tasks.py` (Celery layer)
  - Imports: `from generation.services.bullet_generation_service import BulletGenerationService`
  - Usage: Async task wrapper for bullet generation
  - Impact: HIGH - Background job processing depends on service

- `generation/tests/test_bullet_generation.py` (Test layer)
  - Imports: Service class and all related models
  - Usage: 35 unit tests mock and test service behavior
  - Impact: HIGH - 35 tests must be updated

- `generation/tests/test_api.py` (Integration test layer)
  - Imports: Indirect via API endpoints
  - Usage: 18 integration tests call endpoints that use service
  - Impact: MEDIUM - Schema changes affect response assertions

**Outbound Dependencies (what this depends on - changes here affect us):**
- `llm_services.services.base.BaseLLMService` (Parent class)
  - Usage: Inheritance, provides retry logic, circuit breaker, performance tracking
  - Impact: HIGH - Breaking changes in base class affect us
  - Stability: HIGH - Well-tested, stable interface

- `llm_services.services.core.TailoredContentService` (LLM calls)
  - Usage: Calls `generate_content()` for bullet generation
  - Impact: HIGH - LLM service changes affect generation behavior
  - Stability: MEDIUM - Prompts may evolve

- `llm_services.services.reliability.CircuitBreaker` (Fault tolerance)
  - Usage: Automatic failure detection for OpenAI API calls
  - Impact: MEDIUM - Circuit breaker config affects reliability
  - Stability: HIGH - Stable reliability pattern

- `artifacts.models.Artifact` (Data access)
  - Usage: Reads artifact content for context
  - Impact: MEDIUM - Schema changes affect query code
  - Stability: HIGH - Stable model, infrequent changes

- `generation.models.BulletPoint, BulletGenerationJob` (Data models)
  - Usage: Creates and updates model instances
  - Impact: HIGH - Schema changes require code updates
  - Stability: MEDIUM - Active development, fields may be added

**External Dependencies (third-party):**
- OpenAI API (`openai` package)
  - Usage: GPT-4 model for bullet generation
  - Impact: CRITICAL - API outages block generation
  - Mitigation: Circuit breaker pattern, fallback handling

- PostgreSQL (via Django ORM)
  - Usage: Persist BulletPoint and BulletGenerationJob records
  - Impact: CRITICAL - Database outages block persistence
  - Mitigation: Transaction handling, retry on deadlock

- Redis (via Django cache)
  - Usage: Cache artifact content, generation results
  - Impact: MEDIUM - Cache misses slow performance, not critical
  - Mitigation: Graceful degradation if cache unavailable

### Side Effects Inventory

[Document all state changes and external interactions]

[Example:]
**Database Operations:**
- **Creates:** `BulletGenerationJob` records (1 per request)
  - Table: generation_bulletgenerationjob
  - Frequency: Per API request (~10-100/day)
  - Size: ~500 bytes per record
  - Retention: Permanent (for audit trail)

- **Updates:** `BulletGenerationJob.status` field (state machine)
  - Transitions: pending → running → completed/failed
  - Frequency: 3 updates per job
  - Concurrency: Row-level locking via Django ORM

- **Creates:** `BulletPoint` records (5-10 per generation)
  - Table: generation_bulletpoint
  - Frequency: 50-1000/day (10-100 jobs × 5-10 bullets)
  - Size: ~200 bytes per record
  - Retention: Permanent (user data)

- **Reads:** `Artifact` records (selected artifacts for context)
  - Query: `Artifact.objects.filter(id__in=artifact_ids).select_related('user')`
  - Frequency: Per generation (1 query, 1-10 artifacts)
  - Performance: Indexed on id, <10ms query time

**External API Calls:**
- **OpenAI API:** GPT-4 model for bullet generation
  - Endpoint: `https://api.openai.com/v1/chat/completions`
  - Model: `gpt-4` (128K context window)
  - Frequency: 1-2 calls per generation
  - Cost: ~$0.10-0.50 per generation ($10/1M input tokens, $20/1M output)
  - Latency: 2-10 seconds per call (P95: 8s)
  - Failure mode: Circuit breaker opens after 5 consecutive failures
  - Retry: 3 attempts with exponential backoff (2s, 4s, 8s)
  - Timeout: 30 seconds per call

**Cache Operations:**
- **Redis GET:** Artifact content cache (read-through)
  - Key pattern: `artifact:content:{artifact_id}`
  - Frequency: 1-10 reads per generation
  - Hit rate: ~80% (artifacts frequently reused)
  - Latency: <5ms for hits, ~100ms for misses (DB fetch)

- **Redis SET:** Generation result cache
  - Key pattern: `generation:result:{job_id}`
  - Frequency: 1 write per generation
  - TTL: 1 hour (results cached for quick re-fetch)
  - Size: ~2KB per cached result

**Message Queue:**
- **Celery task dispatch:** `process_bullet_generation_task`
  - Queue: `generation` (priority: medium)
  - Broker: Redis (reliable, persistent)
  - Frequency: Per async generation request (~50-80/day)
  - Retry: 3 attempts with exponential backoff (60s, 300s, 900s)
  - Timeout: 5 minutes per task
  - Dead letter queue: Failed tasks logged to `generation_failed` queue

**Metrics/Logging:**
- **Performance tracking:**
  - Metric: `llm.generation.duration_seconds` (histogram)
  - Metric: `llm.generation.cost_dollars` (counter)
  - Metric: `llm.generation.tokens_used` (counter)
  - Destination: PerformanceTracker → CloudWatch Metrics

- **Error logging:**
  - Event: Hallucination detection failures
  - Event: Circuit breaker state changes (closed → open → half-open)
  - Level: ERROR for failures, INFO for state changes
  - Destination: Django logger → CloudWatch Logs

- **Business metrics:**
  - Metric: `bullets.generated.count` (counter)
  - Metric: `bullets.verification.pass_rate` (gauge)
  - Metric: `generations.per_user` (histogram)
  - Destination: Custom metrics → CloudWatch Dashboard

**File System Operations:**
- NONE (no file writes in this service)

**Email/Notifications:**
- NONE (no emails sent by this service)

### Impact Radius

[Diagram/list of all affected components by layer]

[Example:]
```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (React) - INDIRECT IMPACT                          │
│ ├── BulletGeneration.tsx (display confidence indicators)    │
│ ├── ReviewWorkflow.tsx (NEW - review UI)                    │
│ └── API client (handle new response schema)                 │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP API calls
┌─────────────────────────────────────────────────────────────┐
│ API Layer (Django) - DIRECT IMPACT                          │
│ ├── generation/views.py (handle verification results)       │
│ ├── generation/serializers.py (serialize confidence)        │
│ └── generation/urls.py (add review endpoint) [NEW]          │
└─────────────────────────────────────────────────────────────┘
                          ↓ calls services
┌─────────────────────────────────────────────────────────────┐
│ Service Layer - MAIN IMPACT ZONE                            │
│ ├── bullet_generation_service.py (MODIFY - add verify step) │
│ ├── bullet_verification_service.py (NEW)                    │
│ └── bullet_validation_service.py (call verification)        │
└─────────────────────────────────────────────────────────────┘
                          ↓ uses
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure Layer - INDIRECT IMPACT                       │
│ ├── llm_services/services/base/ (BaseLLMService)           │
│ ├── llm_services/services/reliability/ (CircuitBreaker)    │
│ └── llm_services/services/reliability/ (PerformanceTracker)│
└─────────────────────────────────────────────────────────────┘
                          ↓ stores in
┌─────────────────────────────────────────────────────────────┐
│ Data Layer (Models) - DIRECT IMPACT                         │
│ ├── BulletPoint model (ADD confidence field) [MIGRATION]    │
│ ├── BulletGenerationJob model (track verification)          │
│ └── ExtractedContent model (ADD source_url) [MIGRATION]     │
└─────────────────────────────────────────────────────────────┘
                          ↓ persists to
┌─────────────────────────────────────────────────────────────┐
│ Database (PostgreSQL) - SCHEMA CHANGES                      │
│ ├── Table: generation_bulletpoint (add column)              │
│ ├── Table: generation_bulletgenerationjob (add column)      │
│ └── Table: artifacts_extractedcontent (add column)          │
└─────────────────────────────────────────────────────────────┘
```

**Critical Path (will break if not updated together):**
1. Data models (add fields) + migrations
2. Service layer (generate with verification)
3. Serializers (serialize new fields)
4. API views (handle new response)
5. Frontend (display new data)

**Affected Path (may need updates):**
6. Celery tasks (handle verification results)
7. Performance tracking (track verification metrics)
8. Tests (update for schema changes)

**Monitoring Path (must observe):**
9. CloudWatch metrics (verification rates)
10. Error logs (verification failures)
11. Cost tracking (LLM call costs)

### High-Risk Areas

[Risk matrix: Impact × Test Coverage]

[Example:]
| Component | Impact | Test Coverage | Risk Level | Mitigation |
|-----------|--------|--------------|------------|------------|
| bullet_verification_service.py (NEW) | HIGH | 0% (new) | 🔴 HIGH | Write comprehensive unit tests FIRST (Stage F) |
| bullet_generation_service.py | HIGH | 94% | 🟡 MEDIUM | Add tests for new verify step |
| Circuit breaker error paths | MEDIUM | 67% | 🟡 MEDIUM | Add error path tests |
| generation/views.py | HIGH | 100% | 🟢 LOW | Add tests for new response schema only |
| generation/models.py | HIGH | 100% | 🟢 LOW | Migration-only change, well-tested pattern |
| Database migrations | HIGH | N/A | 🟡 MEDIUM | Test migration up/down, backup before deploy |
| OpenAI API integration | CRITICAL | 85% | 🟡 MEDIUM | Existing circuit breaker mitigates, monitor closely |

**Detailed Risk Analysis:**

**🔴 HIGH RISK:**
1. **bullet_verification_service.py** (NEW service, 0% coverage)
   - **Why high risk:** Core verification logic, no tests yet, critical path
   - **Impact if fails:** Hallucinations not detected, user trust damaged
   - **Mitigation:**
     - Write comprehensive unit tests FIRST (Stage F, before implementation)
     - Integration tests with real LLM calls (Stage H, tagged as slow)
     - Manual testing with diverse bullet examples
     - Staged rollout (canary 10% of users first)

**🟡 MEDIUM RISK:**
2. **bullet_generation_service.py** (94% coverage, adding new logic)
   - **Why medium risk:** High coverage but adding new verification step
   - **Impact if fails:** Degraded user experience, no verification performed
   - **Mitigation:**
     - Add tests for verification integration (Stage F)
     - Test error handling when verification fails
     - Monitor verification pass rate in production

3. **Circuit breaker error paths** (67% coverage)
   - **Why medium risk:** Error handling partially untested
   - **Impact if fails:** Cascading failures, poor error messages
   - **Mitigation:**
     - Add tests for circuit open state (Stage F)
     - Add tests for half-open recovery (Stage F)
     - Monitor circuit breaker metrics in production

4. **Database migrations** (schema changes)
   - **Why medium risk:** Schema changes always risky, hard to rollback
   - **Impact if fails:** Deployment blocked, potential data loss
   - **Mitigation:**
     - Test migration up/down on staging environment
     - Backup production database before migration
     - Use zero-downtime migration pattern (add nullable field first)

**🟢 LOW RISK:**
5. **generation/views.py** (100% coverage)
   - **Why low risk:** Well-tested, simple schema addition
   - **Impact if fails:** API returns 500, caught by tests
   - **Mitigation:** Add tests for new response field (quick, low effort)

---

## Phase 4: Reusable Component Discovery

### Similar Feature Search Results

[What similar features exist in the codebase?]

[Example:]
**Found Similar Patterns:**

1. **artifacts/services/artifact_enrichment_service.py**
   - **Pattern:** Service orchestrator (coordinates multiple sub-services)
   - **Similarity:** Calls multiple LLM services, aggregates results
   - **Lines:** 284 lines, well-structured
   - **Reusable:** Orchestration pattern with retry logic
   - **How to apply:** Use similar pattern for verification orchestration

2. **llm_services/services/core/evidence_content_extractor.py**
   - **Pattern:** LLM-based extraction with source attribution
   - **Similarity:** Extracts structured data from unstructured content, tracks sources
   - **Lines:** 367 lines, includes source tracking
   - **Reusable:** Source attribution logic (ExtractedContent dataclass)
   - **How to apply:** Extend ExtractedContent for verification sources

3. **generation/services/bullet_validation_service.py**
   - **Pattern:** Input validation with multi-criteria checks
   - **Similarity:** Validates bullets against criteria, returns pass/fail with reasons
   - **Lines:** 495 lines, comprehensive validation
   - **Reusable:** Multi-criteria validation pattern
   - **How to apply:** Use similar structure for verification criteria

4. **llm_services/services/reliability/circuit_breaker.py**
   - **Pattern:** Fault tolerance for external APIs
   - **Similarity:** Detects failures, prevents cascading errors
   - **Lines:** 187 lines, production-tested
   - **Reusable:** Circuit breaker pattern (already available via BaseLLMService)
   - **How to apply:** Inherit BaseLLMService for automatic circuit breaker

**No Similar Features Found For:**
- Bullet verification against source documents (NEW feature, no duplication)
- Hallucination detection for generated content (NEW feature, no duplication)

### Reusable Component Inventory

[Table of reusable services/patterns with usage guidance]

[Example:]
| Component | Location | Reusable Pattern | Provides | How to Use | Documentation |
|-----------|----------|-----------------|----------|------------|---------------|
| `BaseLLMService` | `llm_services/services/base/base_service.py` | LLM service base class | Retry logic, circuit breaker, performance tracking, exception handling | Inherit: `class BulletVerificationService(BaseLLMService):` | spec-llm.md:450-500 |
| `CircuitBreaker` | `llm_services/services/reliability/circuit_breaker.py` | Fault tolerance | Failure detection (5 consecutive failures), auto-recovery (60s), metrics | Automatic via BaseLLMService | spec-llm.md:650-700 |
| `TaskExecutor` | `llm_services/services/base/task_executor.py` | Unified task execution | Retry with exponential backoff, timeout handling, error reporting | `executor.execute_with_retry(task)` | spec-llm.md:550-600 |
| `PerformanceTracker` | `llm_services/services/reliability/performance_tracker.py` | Cost and latency tracking | LLM call duration, token count, cost calculation, CloudWatch metrics | `@track_performance` decorator | spec-llm.md:700-750 |
| `ExtractedContent` | `llm_services/services/core/evidence_content_extractor.py` | Source attribution | Dataclass with source_type, source_url, confidence fields | Extend for verification: add verification_result field | spec-llm.md:366-410 |
| `ModelRegistry` | `llm_services/services/infrastructure/model_registry.py` | Model configuration | Model IDs, pricing, context windows, temperature defaults | Add verification model to `MODEL_CONFIGS` dict | spec-llm.md:797-850 |

**Detailed Usage Examples:**

**1. BaseLLMService (MUST USE for all LLM services)**
```python
from llm_services.services.base.base_service import BaseLLMService

class BulletVerificationService(BaseLLMService):
    """Verify generated bullets against source documents."""

    async def verify_bullet_set(
        self,
        bullets: List[Dict[str, Any]],
        artifact_content: str,
        extracted_evidence: ExtractedContent
    ) -> VerificationResult:
        """Verify all bullets in a set against sources."""
        # Circuit breaker, retry, and performance tracking automatic
        result = await self.execute_with_retry(
            task=VerificationTask(bullets, artifact_content, extracted_evidence)
        )
        return result
```
**Benefits:** Automatic retry, circuit breaker, performance tracking, error handling
**Documentation:** See spec-llm.md lines 450-500 for complete interface

**2. CircuitBreaker (Automatic via BaseLLMService)**
No manual usage needed - inheriting BaseLLMService provides circuit breaker automatically.

**Configuration:**
- Failure threshold: 5 consecutive failures
- Recovery timeout: 60 seconds (half-open state)
- Metrics: Tracked in PerformanceTracker

**3. PerformanceTracker (Track verification metrics)**
```python
from llm_services.services.reliability.performance_tracker import track_performance

class BulletVerificationService(BaseLLMService):
    @track_performance(operation="bullet_verification")
    async def verify_bullet_set(self, ...):
        # Metrics automatically tracked:
        # - Duration: Time for verification
        # - Cost: OpenAI API cost
        # - Tokens: Input/output token count
        # - Success: Pass/fail status
        pass
```
**Metrics sent to:** CloudWatch Metrics (namespace: CVTailor/LLM)

**4. ExtractedContent (Source attribution pattern)**
```python
from llm_services.services.core.evidence_content_extractor import ExtractedContent

# Existing usage (for reference)
extracted_content = ExtractedContent(
    source_type='pdf',
    source_url='s3://bucket/file.pdf',
    success=True,
    data={'content': '...'},
    confidence=0.95
)

# Extend for verification (new field)
# Add to ExtractedContent dataclass:
verification_result: Optional[VerificationResult] = None
```
**Pattern:** Always track source URLs for attribution and verification

### Architecture Patterns to Follow

[Established patterns from docs/architecture/patterns.md]

[Example:]
**1. Service Layer Pattern (MANDATORY)**
- **Source:** llm_services/ app structure (reference implementation)
- **Documentation:** docs/architecture/patterns.md, spec-llm.md
- **Layers:** base → core → infrastructure → reliability
- **Apply to:** New bullet verification service

**Layer Assignment:**
```
generation/services/
├── base/                          # IF needed (shared base for generation services)
│   └── base_generation_service.py  # Base class for all generation services
├── core/                          # Business logic (MAIN)
│   ├── bullet_generation_service.py  # Existing
│   ├── bullet_validation_service.py  # Existing
│   └── bullet_verification_service.py  # NEW - Add here
├── infrastructure/                # IF needed (config, helpers)
└── reliability/                   # IF needed (custom fault tolerance)
```

**Decision:** Place BulletVerificationService in `generation/services/core/` (business logic layer)

**2. Circuit Breaker Pattern (MANDATORY for external APIs)**
- **Source:** llm_services/services/reliability/circuit_breaker.py
- **Documentation:** spec-llm.md:650-700
- **Apply to:** All OpenAI API calls for verification
- **Implementation:** Inherit BaseLLMService (includes circuit breaker automatically)

**Configuration:**
- Failure threshold: 5 consecutive failures
- Open duration: 60 seconds
- Half-open state: Single test request after recovery timeout

**3. Performance Tracking Pattern (MANDATORY for LLM calls)**
- **Source:** llm_services/services/reliability/performance_tracker.py
- **Documentation:** spec-llm.md:700-750
- **Apply to:** Track verification call costs and latency
- **Implementation:** Use `@track_performance` decorator on verification methods

**Metrics to track:**
- Verification duration (histogram)
- Verification cost (counter)
- Verification pass rate (gauge)
- Tokens used per verification (histogram)

**4. TDD Pattern (MANDATORY)**
- **Source:** rules/05-tdd.md
- **Apply to:** Write failing tests BEFORE implementation
- **Sequence:**
  1. Stage F: Write failing unit tests (mocked LLM)
  2. Stage G: Implement to pass unit tests
  3. Stage H: Write integration tests (real LLM calls), refactor

**Test Coverage Targets:**
- Unit tests: ≥90% (all business logic paths)
- Integration tests: Critical paths (LLM integration, error handling)
- Load tests: Performance under concurrent load

**5. Error Handling Pattern (from llm_services)**
- **Source:** llm_services/services/base/exception_handler.py
- **Pattern:** Specific exceptions with clear error messages
- **Apply to:** Verification service error cases

**Exception Hierarchy:**
```python
class VerificationError(Exception):
    """Base class for verification errors."""

class VerificationTimeoutError(VerificationError):
    """Verification took too long."""

class VerificationAPIError(VerificationError):
    """OpenAI API error during verification."""

class VerificationInsufficientSourcesError(VerificationError):
    """Not enough source documents for verification."""
```

### Duplicate Implementation Check

[Verify no duplicate functionality will be created]

[Example:]
✅ **NO DUPLICATES FOUND**

**Verification Process:**

**1. Searched for existing "verification" services:**
```bash
$ grep -r "verification" backend/ --include="*.py" | grep -i service
# Results: NONE - No existing verification services found
```

**2. Searched for "hallucination detection" features:**
```bash
$ grep -r "hallucination" backend/ --include="*.py"
# Results: Comments mentioning hallucination risk, but no detection implementation
```

**3. Checked pending PRs and branches:**
```bash
$ git branch -r | grep verification
# Results: NONE - No branches working on verification
```

**4. Reviewed recent ADRs for related decisions:**
- ADR-031: Recommends implementing verification service (this change)
- ADR-032: Chose LLM-based verification over rule-based
- ADR-033: Defined verification confidence scoring approach
- ADR-034: Selected source attribution strategy

**5. Checked for similar functionality in different modules:**
- `bullet_validation_service.py` - INPUT validation only (length, format checks)
  - **Different concern:** Validation = check input format, Verification = detect hallucinations
  - **No duplication:** These are complementary, not duplicate
- `evidence_content_extractor.py` - Extracts content, doesn't verify accuracy
  - **Different concern:** Extraction = get content, Verification = check truthfulness
  - **No duplication:** Extraction provides input for verification

**Existing Related Code (to extend, not duplicate):**

| Component | Purpose | Relationship to New Verification Service |
|-----------|---------|----------------------------------------|
| `bullet_validation_service.py` | Input validation | Will CALL verification service (consumer) |
| `bullet_generation_service.py` | Generate bullets | Will CALL verification service (consumer) |
| `evidence_content_extractor.py` | Extract source content | Provides INPUT to verification (dependency) |
| `BaseLLMService` | LLM service base class | Parent class for verification (inheritance) |

**Decision:** ✅ Safe to create new `BulletVerificationService` - no duplication risk

**Rationale:**
- No existing verification service found
- ADRs explicitly recommend creating new service
- Existing validation service has different concern (input format vs. content accuracy)
- New service will be consumed by existing services (proper separation of concerns)

---

## Risk Assessment & Recommendations

### Overall Risk Level

[LOW / MEDIUM / HIGH with justification]

[Example:]
**Risk Level:** 🟡 **MEDIUM**

**Justification:**
- ➕ **Positive factors (reduce risk):**
  - Strong reusable patterns identified (BaseLLMService, CircuitBreaker)
  - High test coverage in existing code (94% in generation services)
  - Well-defined specs with high confidence (spec-llm.md: HIGH)
  - Clear architecture patterns to follow (llm_services structure)
  - Comprehensive discovery completed (all phases)

- ➖ **Risk factors (increase risk):**
  - New service with 0% initial coverage (needs comprehensive tests)
  - Database migrations required (schema changes always risky)
  - External API dependency (OpenAI API, though mitigated by circuit breaker)
  - Affects critical user path (bullet generation, high visibility)
  - Spec updates required for 3 specs (coordination needed)

**Risk Trend:** ⬇️ **DECREASING** (mitigations in place, TDD approach will improve confidence)

### Key Risks

[Top 3-5 risks identified during discovery]

[Example:]
**1. 🔴 HIGH: New service with zero test coverage**
- **Risk:** BulletVerificationService is NEW code with no tests yet
- **Impact:** Hallucinations not detected, user trust damaged, business reputation risk
- **Probability:** HIGH (new code always has bugs)
- **Severity:** CRITICAL (affects core product value proposition)
- **Risk Score:** 9/10 (HIGH probability × CRITICAL severity)

**2. 🟡 MEDIUM: Database migration complexity**
- **Risk:** Schema changes to 3 tables (BulletPoint, BulletGenerationJob, ExtractedContent)
- **Impact:** Deployment blocked, potential downtime, rollback difficulty
- **Probability:** MEDIUM (migrations sometimes fail in production)
- **Severity:** HIGH (affects all users during deployment)
- **Risk Score:** 6/10 (MEDIUM probability × HIGH severity)

**3. 🟡 MEDIUM: OpenAI API dependency**
- **Risk:** Verification requires OpenAI API calls, external dependency failure risk
- **Impact:** Verification unavailable, degraded user experience
- **Probability:** MEDIUM (OpenAI has ~99.9% uptime, but outages happen)
- **Severity:** MEDIUM (circuit breaker provides graceful degradation)
- **Risk Score:** 5/10 (MEDIUM probability × MEDIUM severity)

**4. 🟢 LOW: Spec drift discovered in Phase 1**
- **Risk:** 4 undocumented API endpoints found, specs slightly outdated
- **Impact:** Design based on outdated specs, minor rework needed
- **Probability:** LOW (already discovered and documented in Phase 1)
- **Severity:** LOW (minor corrections needed, doesn't affect architecture)
- **Risk Score:** 2/10 (LOW probability × LOW severity)

**5. 🟢 LOW: Test update effort (35 affected tests)**
- **Risk:** Significant effort to update existing tests (estimated 3 hours)
- **Impact:** Delayed implementation, potential for missing test updates
- **Probability:** LOW (clear test update checklist created in Phase 2)
- **Severity:** LOW (well-understood changes, clear checklist)
- **Risk Score:** 2/10 (LOW probability × LOW severity)

### Mitigation Strategies

[How to address each risk]

[Example:]
**Risk 1 Mitigation: New service with zero test coverage**
- **Strategy 1:** TDD approach - Write failing tests FIRST (Stage F)
  - Write comprehensive unit tests with mocked LLM responses
  - Target: ≥90% coverage before implementation
  - Estimated effort: 3 hours (15 unit tests identified in Phase 2)

- **Strategy 2:** Integration tests with real LLM calls (Stage H)
  - Test with diverse bullet examples (good, bad, edge cases)
  - Verify hallucination detection accuracy
  - Estimated effort: 1.5 hours (tagged as @slow tests)

- **Strategy 3:** Manual testing with golden dataset
  - Create 20 bullet examples (10 good, 10 with hallucinations)
  - Manually verify detection accuracy
  - Target: ≥90% accuracy on golden dataset

- **Strategy 4:** Staged rollout (canary deployment)
  - Deploy to 10% of users first (canary group)
  - Monitor verification pass rate, error rate
  - Roll back if pass rate <80% or error rate >5%

**Risk 2 Mitigation: Database migration complexity**
- **Strategy 1:** Test migrations on staging environment
  - Run migration up/down on staging database
  - Verify data integrity after migration
  - Estimated time: 30 minutes

- **Strategy 2:** Backup production database before migration
  - Take full database backup
  - Verify backup restoration works
  - Estimated time: 15 minutes (automated script)

- **Strategy 3:** Zero-downtime migration pattern
  - Add fields as nullable first (no default required)
  - Deploy code that handles both null and populated values
  - Backfill data in second deployment (if needed)

- **Strategy 4:** Rollback plan documented in OP-NOTE
  - SQL commands to reverse migration
  - Code rollback procedure
  - Estimated rollback time: 10 minutes

**Risk 3 Mitigation: OpenAI API dependency**
- **Strategy 1:** Circuit breaker (already provided by BaseLLMService)
  - Automatic failure detection (5 consecutive failures)
  - Prevents cascading failures
  - Graceful degradation (return unverified bullets)

- **Strategy 2:** Retry with exponential backoff
  - 3 retry attempts (2s, 4s, 8s delays)
  - Handles transient failures
  - Total retry time: 14s max

- **Strategy 3:** Fallback behavior when API unavailable
  - Return bullets with confidence=null (unverified)
  - Log warning for monitoring
  - User sees bullets with "Verification unavailable" message

- **Strategy 4:** Monitor API health proactively
  - CloudWatch alarm on circuit breaker open state
  - Alert on verification failure rate >10%
  - Dashboard showing API uptime and latency

**Risk 4 Mitigation: Spec drift**
- **Strategy 1:** Update specs during Stage C (Specify)
  - Correct endpoint count (47 → 51)
  - Add missing endpoint documentation
  - Update pricing table

- **Strategy 2:** Add spec validation to CI (future)
  - Automated check: spec endpoint count vs. actual
  - Automated check: spec model configs vs. code
  - Prevents future drift

**Risk 5 Mitigation: Test update effort**
- **Strategy 1:** Follow test update checklist from Phase 2
  - Clear categorization: KEEP/UPDATE/REMOVE/ADD
  - Estimated effort: 3 hours (already planned)

- **Strategy 2:** Update tests incrementally with implementation
  - Update tests as you implement each feature
  - Don't batch all test updates to end

- **Strategy 3:** Automated test verification
  - CI runs all tests, catches missing updates
  - Coverage report shows untested new code

### Go/No-Go Recommendation

[Proceed to Stage C? Or need more investigation?]

[Example:]
**Recommendation:** ✅ **GO - Proceed to Stage C (Specify)**

**Justification:**
- ✅ All 5 discovery phases completed successfully
- ✅ Spec confidence levels assessed (HIGH for critical specs)
- ✅ Clear architecture patterns identified (BaseLLMService, CircuitBreaker)
- ✅ Reusable components documented (no duplication risk)
- ✅ Risk level MEDIUM with effective mitigation strategies
- ✅ Test update checklist created (35 tests mapped)
- ✅ Dependency map complete (impact radius understood)

**Conditions for proceeding:**
1. ✅ Spec updates planned for Stage C (spec-llm.md, spec-api.md, spec-cv-generation.md)
2. ✅ TDD approach committed (write tests FIRST in Stage F)
3. ✅ Risk mitigations documented and understood
4. ✅ Reusable component usage planned (BaseLLMService inheritance)

**Success Criteria for Stage C (next stage):**
- Update 3 affected specs with version increments
- Reference this discovery document from FEATURE spec
- Create ADRs for non-trivial decisions (verification algorithm, confidence scoring)
- Design interfaces following discovered patterns (BaseLLMService inheritance)

**Red Flags (would trigger NO-GO):**
- ❌ Critical spec drift found (contracts don't match code) - NOT FOUND
- ❌ Duplicate functionality exists - NOT FOUND
- ❌ Unknown dependencies discovered - NONE FOUND
- ❌ Risk level assessed as HIGH with no mitigations - NOT APPLICABLE

**Confidence Level:** 🟢 **HIGH** (discovery thorough, risks understood and mitigated)

---

## Post-Implementation Notes

[To be filled in Stage I: Spec Reconciliation]

[This section is completed AFTER implementation (Stage G) and refactoring (Stage H)]

[Example content (for reference - leave blank until Stage I):]

### What Actually Happened During Implementation

- Implementation deviated from design in the following ways:
  - [Describe architectural decisions made during coding]
  - [E.g., "Added caching layer for verification results (not in original design)"]

### Architectural Decisions Made

- [List ADRs created during implementation]
- [E.g., "ADR-035: Verification result caching strategy"]

### Specs Updated

- [List specs updated in Stage I]
- [E.g., "spec-llm.md v4.3.0: Added caching topology to architecture diagram"]

### Lessons Learned

- **What went well:**
  - [E.g., "BaseLLMService inheritance worked perfectly, saved 200 lines of code"]

- **What was challenging:**
  - [E.g., "Verification confidence scoring required 3 iterations to get right"]

- **For future similar changes:**
  - [E.g., "Budget more time for LLM prompt engineering (2x initial estimate)"]

### Discovery Accuracy Assessment

- **Discovery predictions vs. reality:**
  - ✅ Accurate: Test count estimate (35 tests, actual: 37)
  - ✅ Accurate: Risk level (MEDIUM, confirmed)
  - ❌ Underestimated: Prompt engineering effort (estimated 2h, actual 4h)

- **What discovery missed:**
  - [E.g., "Caching requirement not identified in Phase 3 (side effects)"]

- **Improvements for next discovery:**
  - [E.g., "Add explicit prompt engineering effort estimation in Phase 4"]
