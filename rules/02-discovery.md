# DISCOVERY — Codebase Discovery and Analysis

## Purpose and Scope
- Before designing new solutions (Stage C: TECH SPEC), perform **comprehensive codebase discovery** to prevent duplicate functionality and ensure architectural consistency.
- Required for **Medium** and **Large** changes; optional for **Small** and **Micro** changes.
- Discovery is **spec-driven first** (analyze specs), then **code validation** (verify specs match reality), then **implementation discovery** (find reusable components).

## Table of Contents
- [Purpose and Scope](#purpose-and-scope)
- [Quick Reference](#quick-reference)
- [Overview & Philosophy](#overview--philosophy)
- [Size-Based Application](#size-based-application)
- [Discovery Phases](#discovery-phases)
  - [Phase 0: Spec Discovery](#phase-0-spec-discovery-mandatory-first)
  - [Phase 1: Spec-Code Validation](#phase-1-spec-code-validation-verify-accuracy)
  - [Phase 2: Test Impact Analysis](#phase-2-test-impact-analysis)
  - [Phase 3: Dependency & Side Effect Mapping](#phase-3-dependency--side-effect-mapping)
  - [Phase 4: Reusable Component Discovery](#phase-4-reusable-component-discovery)
- [Discovery Document Output](#discovery-document-output)
  - [Path & Naming](#path--naming-mandatory)
  - [Document Structure](#document-structure-required-sections)
  - [Storage Location](#storage-location)
- [Examples & Best Practices](#examples--best-practices)
- [Enforcement Rules](#enforcement-rules)
- [Quality Checklist](#quality-checklist)

## Quick Reference

**Common tasks (quick links):**
- **[When is discovery required?](#size-based-application)** - Check if your change requires discovery
- **[Phase 0: Spec Discovery](#phase-0-spec-discovery-mandatory-first)** - Start here: analyze existing specs first
- **[Phase 1: Spec-Code Validation](#phase-1-spec-code-validation-verify-accuracy)** - Verify specs match reality
- **[Document template](#document-structure-required-sections)** - Structure for discovery output
- **[Examples](#examples--best-practices)** - See real discovery examples
- **[Enforcement rules](#enforcement-rules)** - What blocks without discovery

## Overview & Philosophy

**Spec-Driven Discovery Principle:**
> "Specs are the primary source of truth about system architecture. Discovery validates specs first, then explores code to find reusable implementations."

**Discovery Flow:**
```
1. SPEC DISCOVERY → Understand contracts and architecture
2. SPEC VALIDATION → Verify specs match code (detect drift)
3. CODE DISCOVERY → Find reusable components and patterns
4. OUTPUT → Document findings for design phase (Stage C)
```

**Key Benefits:**
- ✅ Prevents duplicate functionality (reuse existing components)
- ✅ Ensures architectural consistency (follow established patterns)
- ✅ Detects spec drift early (before implementation)
- ✅ Creates knowledge base (discovery docs become reference)
- ✅ Reduces risk (identify high-impact areas early)

**Relationship to Workflow:**
- **Stage A (Initiate):** Create/update PRD
- **Stage B (Discovery):** ← YOU ARE HERE - Analyze before designing
- **Stage C (Specify):** Create/update TECH SPECs (informed by discovery)
- **Stage D (Decide):** Create ADRs for decisions
- **Stage E (Plan):** Create FEATURE spec

## Size-Based Application

| Track | Discovery Required? | Rationale |
|-------|-------------------|-----------|
| **Micro** | ❌ Optional | Bug fixes, typos, trivial changes unlikely to need discovery |
| **Small** | ❌ Optional | Single component changes, limited scope |
| **Medium** | ✅ **MANDATORY** | Multi-component work requires discovery to prevent issues |
| **Large** | ✅ **MANDATORY** | System-level changes require thorough analysis |

**When in doubt:** If change touches >2 components or affects contracts/topology, **perform discovery**.

**Enforcement:**
- **BLOCK:** Stage B skipped for Medium/Large changes
- **BLOCK:** Discovery without test impact analysis (Phase 2)
- **BLOCK:** Discovery without dependency mapping (Phase 3)
- **BLOCK:** Duplicate code created when reusable components exist

## Discovery Phases

### Phase 0: Spec Discovery (Mandatory First)

**Purpose:** Understand existing architecture through specs BEFORE diving into code.

**Why Spec-First?**
- Specs define contracts and topology (the "what" and "why")
- Code shows implementation (the "how")
- Understanding contracts first prevents architectural violations

**Checklist:**

#### 1. List All Existing Specs
```bash
# Read the spec index
cat docs/specs/index.md

# List all spec files
ls -la docs/specs/
```

**Output:** List of all specs with versions and scope summaries.

#### 2. Identify Affected Specs

For each spec, check if your planned change falls within its scope:

**Review these sections in each spec:**
- **Scope/Covered Areas** - Does this change fit within this spec's scope?
- **Architecture** - Does this change affect topology shown in diagrams?
- **Contracts** - Does this change interact with defined APIs/schemas/events?
- **Changelog** - Have similar changes been made before? Learn from history.

**Common affected specs by change type:**

| Change Type | Likely Affected Specs |
|-------------|---------------------|
| New API endpoint | `spec-api.md`, `spec-system.md` |
| LLM service change | `spec-llm.md`, `spec-system.md` |
| Frontend component | `spec-frontend.md`, `spec-system.md` |
| Database schema | `spec-database-schema.md`, `spec-api.md` |
| Deployment change | `spec-deployment-*.md`, `spec-system.md` |

#### 3. Extract Spec-Defined Architecture Patterns

For each affected spec, document:

**Contracts to Follow:**
```markdown
- API endpoints: [list relevant endpoints from spec-api.md]
- Data schemas: [list relevant schemas with versions]
- Event definitions: [list events if applicable]
```

**Service Layer Structure:**
```markdown
- Layer assignment: [base/core/infrastructure/reliability]
- Interface signatures: [list interfaces to implement/extend]
- Dependencies: [list services this will depend on]
```

**Configuration Schemas:**
```markdown
- Config tables: [list config structures to extend]
- Model registry: [list model configs if LLM-related]
```

**Example (from Phase 0 output):**
```markdown
## Phase 0: Spec Discovery Results

### Affected Specs
- **spec-llm.md** (v4.2.0) - LLM service interfaces and model registry
- **spec-api.md** (v4.2.0) - Generation endpoints and schemas
- **spec-system.md** (v1.4.0) - System topology and service relationships

### Spec-Defined Patterns to Follow

**Service Layer Structure:**
- Layer: `generation/services/core/` (business logic)
- Parent class: `BaseLLMService` (from llm_services/services/base/)
- Pattern: Circuit breaker for external API calls (reliability layer)

**Interface Signatures:**
From `spec-llm.md` (lines 450-472):
```python
class BaseLLMService:
    async def execute_with_retry(self, task: Task) -> Result:
        """Execute task with retry logic and circuit breaker."""
```

**Configuration Schema:**
From `spec-llm.md` Model Registry:
- Add new model to `MODEL_CONFIGS` dict
- Required fields: model_id, provider, context_window, pricing
```

#### 4. Note Spec Metadata

For risk assessment, note:
- **Last Verified Date:** When was spec last validated against code?
- **Confidence Level:** Does spec have confidence metadata? (HIGH/MEDIUM/LOW)
- **Known Drift Areas:** Does spec list areas that need validation?

**Spec Drift Risk Assessment:**

| Risk Level | Indicators | Action Required |
|------------|-----------|----------------|
| 🟢 **LOW** | Last verified <30 days, confidence HIGH | Trust spec, light validation |
| 🟡 **MEDIUM** | Last verified 30-90 days, confidence MEDIUM | Validate key sections in Phase 1 |
| 🔴 **HIGH** | Last verified >90 days, confidence LOW/missing | Full validation in Phase 1 |

**Output Example:**
```markdown
### Spec Confidence Assessment
- **spec-llm.md** (v4.2.0): Last verified 2025-11-04, confidence HIGH 🟢
  - Trust level: Can rely on interface signatures and schemas
  - Known drift: Model pricing may need verification
- **spec-api.md** (v4.2.0): Last verified 2025-10-15, confidence MEDIUM 🟡
  - Trust level: Validate endpoint counts and schemas
  - Known drift: Recent migrations may have added fields
```

#### 5. Create Spec Update Checklist

Based on your planned change, identify which specs will need updates:

**Spec Update Triggers (from Stage 0 workflow.md, lines 188-193):**
- ✅ **Contracts:** API/schema/event definitions
- ✅ **Topology:** Adding/removing components, new protocols
- ✅ **Framework roles:** Django/React/Redis role changes
- ✅ **SLOs:** Performance/availability target changes

**Output Example:**
```markdown
### Spec Update Checklist (for Stage C)

- [ ] **spec-llm.md** → Likely v4.2.0 → v4.3.0 (non-breaking)
  - Reason: Adding new verification service interface
  - Update: Add `BulletVerificationService` interface signature
  - Version bump: Minor (new interface, no breaking changes)

- [ ] **spec-api.md** → Likely v4.2.0 → v4.3.0 (non-breaking)
  - Reason: Adding review workflow endpoints
  - Update: Add `/api/v1/bullets/{id}/review/` endpoint specs
  - Version bump: Minor (new endpoints, backward compatible)
```

---

### Phase 1: Spec-Code Validation (Verify Accuracy)

**Purpose:** Verify that specs accurately reflect current codebase reality. Detect and document drift.

**Why This Matters:**
- Specs may be outdated (code evolved faster than specs)
- Code may contain undocumented features (tech debt)
- Validation builds confidence in using specs as design source

**Checklist:**

#### 1. Validate Spec-Defined Contracts

For each affected spec from Phase 0, verify key contracts:

**API Endpoints (spec-api.md):**
```bash
# Compare spec-claimed endpoint count vs actual
grep "Total Endpoints:" docs/specs/spec-api.md
find backend -name "urls.py" -exec grep -h "path\|re_path" {} \; | wc -l

# Verify specific endpoint signatures
grep "POST /api/v1/generations/" docs/specs/spec-api.md
grep -A 10 "def create_generation" backend/generation/views.py
```

**Data Schemas (spec-api.md, spec-database-schema.md):**
```bash
# Compare spec schema to model definitions
# Read spec schema, then read actual model file
```

**Service Interfaces (spec-llm.md):**
```bash
# Verify interface signatures match spec
grep "class BaseLLMService" docs/specs/spec-llm.md
cat backend/llm_services/services/base/base_service.py
```

**Document discrepancies found:**
```markdown
### Discrepancies Found

1. **spec-api.md** (Line 234): Claims 47 endpoints, actual count is 51
   - Impact: MINOR - 4 undocumented endpoints added
   - Files: generation/urls.py (2 new), export/urls.py (2 new)
   - Action: Update spec endpoint count and add missing endpoints

2. **spec-llm.md** (Line 797): Model pricing outdated for GPT-4
   - Impact: MINOR - Pricing info is $15/$30, actual is $10/$20
   - Action: Update model_registry.py pricing table in spec

3. **spec-database-schema.md**: Missing 'confidence' field on ExtractedContent
   - Impact: MEDIUM - New field added in migration 0024
   - Action: Update ERD diagram and table definition
```

#### 2. Assess Spec Confidence Level

Based on validation, assign confidence to each spec:

**Confidence Scale:**
- ⭐⭐⭐⭐⭐ (5/5) **VERIFIED** - Automated checks pass, verified <30 days
- ⭐⭐⭐⭐ (4/5) **HIGH** - Manual audit <60 days, <5 minor discrepancies
- ⭐⭐⭐ (3/5) **MEDIUM** - Verified <90 days, some known drift areas
- ⭐⭐ (2/5) **LOW** - >90 days since verification, significant drift suspected
- ⭐ (1/5) **UNVERIFIED** - Never verified, or major discrepancies

**Output Example:**
```markdown
### Spec Confidence Assessment (Post-Validation)

- **spec-llm.md** (v4.2.0): ⭐⭐⭐⭐ HIGH (4/5)
  - Status: Interfaces match, minor pricing drift
  - Last validated: Today (2025-11-06)
  - Recommendation: Safe to use for design, update pricing in Stage C

- **spec-api.md** (v4.2.0): ⭐⭐⭐ MEDIUM (3/5)
  - Status: Endpoint count drift, schemas accurate
  - Last validated: Today (2025-11-06)
  - Recommendation: Use with caution, verify endpoint list manually

- **spec-database-schema.md**: ⭐⭐⭐⭐ HIGH (4/5)
  - Status: Missing recent field additions
  - Last validated: Today (2025-11-06)
  - Recommendation: Safe to use, add missing fields in Stage C
```

#### 3. Identify High-Priority Spec Updates

Flag specs that MUST be updated before proceeding to Stage C:

**Update Priority:**

| Priority | Condition | Action |
|----------|----------|--------|
| 🔴 **CRITICAL** | Contract changes not documented | Update spec BEFORE Stage C design |
| 🟡 **HIGH** | Significant drift, affects design decisions | Update during Stage C |
| 🟢 **MEDIUM** | Minor drift, doesn't affect design | Update after implementation (Stage I) |

**Output Example:**
```markdown
### Required Spec Updates (Before Stage C)

🔴 **CRITICAL - Update BEFORE design:**
- NONE (all critical contracts documented)

🟡 **HIGH - Update DURING Stage C:**
- spec-api.md: Add 4 missing endpoints, correct endpoint count
- spec-database-schema.md: Add 'confidence' field to ExtractedContent

🟢 **MEDIUM - Can defer to Stage I:**
- spec-llm.md: Update model pricing table
```

---

### Phase 2: Test Impact Analysis

**Purpose:** Identify existing tests affected by the planned change. Create test update checklist.

**Checklist:**

#### 1. Identify Affected Test Files

Based on planned change, find related tests:

```bash
# Find test files for affected components
find backend -name "test_*.py" -path "*/generation/*"
find backend -name "test_*.py" -path "*/llm_services/*"

# Search for tests by feature name
grep -r "test.*bullet.*generation" backend/*/tests/
```

**Output:**
```markdown
### Affected Test Files

**Direct Impact (will definitely need updates):**
- `backend/generation/tests/test_bullet_generation.py` (35 tests)
- `backend/generation/tests/test_bullet_validation.py` (28 tests)

**Indirect Impact (may need updates):**
- `backend/generation/tests/test_tasks.py` (12 tests, Celery tasks)
- `backend/generation/tests/test_api.py` (18 tests, endpoint integration)
```

#### 2. Create Test Update Checklist

For each affected test file, categorize tests:

**Categories:**
- ✅ **KEEP** - Test still valid, no changes needed
- 🔄 **UPDATE** - Test needs modification for new behavior
- ❌ **REMOVE** - Test obsolete with new implementation
- ➕ **ADD** - New test needed for new functionality

**Output Example:**
```markdown
### Test Update Checklist

**backend/generation/tests/test_bullet_generation.py:**
- ✅ KEEP: `test_generate_bullets_with_mock_llm` (still valid)
- 🔄 UPDATE: `test_bullet_generation_schema` (schema adds confidence field)
- 🔄 UPDATE: `test_generation_with_retry` (new retry logic)
- ❌ REMOVE: `test_old_validation_logic` (replaced by new service)
- ➕ ADD: `test_source_attribution_in_bullets` (new feature)
- ➕ ADD: `test_verification_pass_rate_tracking` (new metric)

**backend/generation/tests/test_api.py:**
- ✅ KEEP: `test_create_generation_endpoint` (endpoint unchanged)
- 🔄 UPDATE: `test_generation_response_schema` (response adds confidence)
- ➕ ADD: `test_review_workflow_endpoint` (new endpoint)

**Summary:**
- Total existing tests affected: 35
- Keep: 18 tests
- Update: 12 tests
- Remove: 5 tests
- Add: 15 new tests
```

#### 3. Map Test Coverage

Identify test coverage of code to be modified:

```bash
# Run coverage report for affected areas
docker-compose exec backend uv run python -m pytest \
  --cov=generation/services \
  --cov-report=term-missing \
  backend/generation/tests/
```

**Output Example:**
```markdown
### Test Coverage Report

**Current Coverage (before changes):**
- `generation/services/bullet_generation_service.py`: 94% (613 lines, 37 missing)
- `generation/services/bullet_validation_service.py`: 89% (495 lines, 54 missing)
- `generation/models.py`: 100% (127 lines, 0 missing)

**Coverage Gaps (high-risk untested paths):**
- bullet_generation_service.py:234-248 (error handling for circuit breaker)
- bullet_validation_service.py:378-402 (retry logic edge cases)

**Action Items:**
- Add tests for circuit breaker error handling (Stage F)
- Add tests for retry edge cases (Stage F)
```

#### 4. Document Test Coverage Gaps

Identify areas that need new tests:

**Output Example:**
```markdown
### Test Coverage Gaps to Address

**High Priority (affects change):**
1. Circuit breaker error handling (lines 234-248)
   - Test: What happens when circuit opens during generation?
   - Test: Verify graceful degradation

2. Retry logic edge cases (lines 378-402)
   - Test: Max retries exceeded behavior
   - Test: Retry with different error types

**Medium Priority (good to have):**
3. Performance under load
   - Load test: 100 concurrent bullet generations
   - Test: Memory usage with large artifacts

**Low Priority (defer):**
4. Edge case input validation
   - Test: Emoji-only input
   - Test: Unicode edge cases
```

---

### Phase 3: Dependency & Side Effect Mapping

**Purpose:** Understand impact radius of planned change. Identify cascading effects.

**Checklist:**

#### 1. Trace Direct Dependencies

Find what the changed code imports and what imports it:

```bash
# What does this file import?
grep "^import\|^from" backend/generation/services/bullet_generation_service.py

# What imports this file?
grep -r "from generation.services import bullet_generation_service" backend/
grep -r "from generation.services.bullet_generation_service import" backend/
```

**Output Example:**
```markdown
### Dependency Map

**Inbound Dependencies (what depends on this):**
- `generation/views.py` (API endpoints)
- `generation/tasks.py` (Celery tasks)
- `generation/tests/test_bullet_generation.py` (unit tests)
- `generation/tests/test_api.py` (integration tests)

**Outbound Dependencies (what this depends on):**
- `llm_services.services.base.BaseLLMService` (parent class)
- `llm_services.services.core.TailoredContentService` (LLM calls)
- `llm_services.services.reliability.CircuitBreaker` (fault tolerance)
- `artifacts.models.Artifact` (data access)
- `generation.models.BulletPoint, BulletGenerationJob` (data models)
```

#### 2. Identify Side Effects

Map state changes and external interactions:

**Side Effect Categories:**
- 🗄️ **Database** - Record creation/updates/deletes
- 🌐 **External API** - HTTP calls to external services
- 💾 **File System** - File reads/writes
- 🔄 **Cache** - Redis cache operations
- 📨 **Message Queue** - Celery task dispatch
- 📊 **Metrics/Logging** - Observability side effects

**Output Example:**
```markdown
### Side Effects Inventory

**Database Operations:**
- Creates: `BulletGenerationJob` records (1 per request)
- Updates: `BulletGenerationJob.status` (pending → running → completed)
- Creates: `BulletPoint` records (5-10 per generation)
- Reads: `Artifact` records (selected artifacts for context)

**External API Calls:**
- OpenAI API: `gpt-4` model (1-2 calls per generation)
  - Cost: ~$0.10-0.50 per generation
  - Latency: 2-10 seconds per call
  - Failure mode: Circuit breaker opens after 5 consecutive failures

**Cache Operations:**
- Redis GET: Artifact content cache (1-5 reads per generation)
- Redis SET: Generation result cache (1 write per generation, TTL 1 hour)

**Message Queue:**
- Celery task: `process_bullet_generation_task` (dispatched for async processing)
  - Queue: `generation` (priority medium)
  - Retry: 3 attempts with exponential backoff

**Metrics/Logging:**
- Performance tracker: LLM call duration, cost tracking
- Error logging: Hallucination detection failures
- Business metrics: Bullets generated count, verification pass rate
```

#### 3. Map Impact Radius

Identify all components affected by this change:

**Layers Affected:**

```
┌─────────────────────────────────────────┐
│ Frontend (indirect impact)              │
│ - BulletGeneration.tsx                  │
│ - ReviewWorkflow.tsx (NEW)              │
└─────────────────────────────────────────┘
              ↓ API calls
┌─────────────────────────────────────────┐
│ API Layer (direct impact)               │
│ - generation/views.py                   │
│ - generation/serializers.py             │
└─────────────────────────────────────────┘
              ↓ calls services
┌─────────────────────────────────────────┐
│ Service Layer (direct impact - MAIN)    │
│ - bullet_generation_service.py (MOD)    │
│ - bullet_validation_service.py (NEW)    │
└─────────────────────────────────────────┘
              ↓ uses
┌─────────────────────────────────────────┐
│ Infrastructure (indirect impact)        │
│ - LLM Services (base, core, reliability)│
│ - Circuit Breaker                       │
│ - Performance Tracker                   │
└─────────────────────────────────────────┘
              ↓ stores in
┌─────────────────────────────────────────┐
│ Data Layer (direct impact)              │
│ - BulletPoint model (ADD confidence)    │
│ - BulletGenerationJob model             │
│ - ExtractedContent model (ADD source)   │
└─────────────────────────────────────────┘
```

**Output Example:**
```markdown
### Impact Radius

**Critical Path (will definitely break if not updated):**
1. `generation/services/bullet_generation_service.py` (MAIN CHANGE)
2. `generation/views.py` (must handle new response schema)
3. `generation/serializers.py` (must serialize confidence field)
4. `generation/models.py` (must add confidence field + migration)

**Affected Path (may need updates):**
5. Frontend `BulletGeneration.tsx` (display confidence indicators)
6. `generation/tasks.py` (Celery tasks may need retry adjustment)
7. `llm_services/performance_tracker.py` (track verification metrics)

**Monitoring Path (must observe):**
8. CloudWatch logs (verification failure rates)
9. Performance metrics (verification latency impact)
```

#### 4. Identify High-Risk Areas

Combine high-impact areas with low-test-coverage areas:

**Risk Matrix:**

| Component | Impact | Test Coverage | Risk Level |
|-----------|--------|--------------|------------|
| bullet_generation_service.py | HIGH | 94% | 🟡 MEDIUM |
| bullet_validation_service.py (NEW) | HIGH | 0% (new) | 🔴 HIGH |
| generation/views.py | HIGH | 100% | 🟢 LOW |
| generation/models.py | HIGH | 100% | 🟢 LOW |
| Circuit breaker error paths | MEDIUM | 67% | 🟡 MEDIUM |

**Output Example:**
```markdown
### High-Risk Areas

🔴 **HIGH RISK (high impact + low coverage):**
- `bullet_validation_service.py` (NEW) - No tests yet, critical path
  - Mitigation: Write comprehensive unit tests FIRST (Stage F)
  - Mitigation: Integration tests with real LLM calls (Stage H)

🟡 **MEDIUM RISK (high impact + medium coverage):**
- `circuit_breaker_service.py` error handling (67% coverage)
  - Mitigation: Add error path tests (Stage F)
  - Mitigation: Load test circuit breaker behavior (Stage H)

🟢 **LOW RISK (high impact + high coverage):**
- `generation/views.py` (100% coverage)
  - Action: Add tests for new response schema only
```

---

### Phase 4: Reusable Component Discovery

**Purpose:** Find existing code that can be reused or extended. Prevent duplicate implementations.

**Checklist:**

#### 1. Search for Similar Features

Use broad searches to find related functionality:

```bash
# Search for similar feature names
grep -r "bullet.*validation" backend/ --include="*.py"
grep -r "verification.*service" backend/ --include="*.py"
grep -r "hallucination.*detection" backend/ --include="*.py"

# Search for similar patterns (services, models, etc.)
find backend -name "*validation*.py"
find backend -name "*verification*.py"
```

**Output Example:**
```markdown
### Similar Feature Search Results

**Found Similar Patterns:**
1. `artifacts/services/artifact_enrichment_service.py`
   - Pattern: Service orchestrator (coordinates multiple sub-services)
   - Reusable: Orchestration pattern with retry logic

2. `llm_services/services/core/evidence_content_extractor.py`
   - Pattern: LLM-based extraction with source attribution
   - Reusable: Source attribution logic

3. `generation/services/bullet_validation_service.py`
   - Status: EXISTS (partially implemented)
   - Action: Extend existing service, don't create duplicate
```

#### 2. Identify Reusable Services/Components

For each reusable component found, document:

**Service Reuse Catalog:**

| Component | Location | Reusable Pattern | How to Use |
|-----------|----------|-----------------|------------|
| `BaseLLMService` | `llm_services/services/base/` | LLM service base class with retry logic | Inherit for new LLM services |
| `CircuitBreaker` | `llm_services/services/reliability/` | Fault tolerance for external APIs | Wrap external calls |
| `TaskExecutor` | `llm_services/services/base/` | Unified retry logic with timeout | Use for task execution |
| `PerformanceTracker` | `llm_services/services/reliability/` | Cost and latency tracking | Track LLM call metrics |

**Output Example:**
```markdown
### Reusable Component Inventory

**1. BaseLLMService (MUST USE)**
- **Location:** `llm_services/services/base/base_service.py`
- **Purpose:** Base class for all LLM-based services
- **Provides:**
  - Retry logic with exponential backoff
  - Circuit breaker integration
  - Performance tracking
  - Exception handling
- **Usage:** `class BulletVerificationService(BaseLLMService):`
- **Documentation:** See spec-llm.md lines 450-500

**2. CircuitBreaker (MUST USE)**
- **Location:** `llm_services/services/reliability/circuit_breaker.py`
- **Purpose:** Prevent cascading failures from external API calls
- **Provides:**
  - Failure threshold detection (5 consecutive failures)
  - Automatic recovery (half-open state after 60s)
  - Metrics tracking (failure rate, open duration)
- **Usage:** Automatically used by BaseLLMService
- **Documentation:** See spec-llm.md lines 650-700

**3. Evidence Content Extractor Pattern**
- **Location:** `llm_services/services/core/evidence_content_extractor.py`
- **Purpose:** Extract content with source attribution
- **Reusable Pattern:** Source URL tracking in ExtractedContent
- **Usage:** Reference for source attribution implementation
```

#### 3. Map Existing Architecture Patterns

Identify established patterns to follow:

**Reference:** `docs/architecture/patterns.md`

**Output Example:**
```markdown
### Architecture Patterns to Follow

**1. Service Layer Pattern (MANDATORY)**
- **Source:** llm_services/ app structure
- **Layers:** base → core → infrastructure → reliability
- **Apply to:** New verification service
- **Structure:**
  ```
  generation/services/
  ├── base/                # IF needed (share with generation services)
  ├── core/
  │   └── bullet_verification_service.py  # NEW
  ├── infrastructure/      # IF needed
  └── reliability/         # IF needed
  ```

**2. Circuit Breaker Pattern (MANDATORY for external APIs)**
- **Source:** llm_services/services/reliability/
- **Apply to:** All OpenAI API calls
- **Implementation:** Inherit BaseLLMService (includes circuit breaker)

**3. Performance Tracking Pattern (MANDATORY for LLM calls)**
- **Source:** llm_services/services/reliability/performance_tracker.py
- **Apply to:** Track verification call costs and latency
- **Implementation:** Use `@track_performance` decorator

**4. TDD Pattern (MANDATORY)**
- **Source:** rules/06-tdd.md
- **Apply to:** Write failing tests BEFORE implementation
- **Sequence:** Test cleanup → Write failing tests → Implement → Refactor
```

#### 4. Check for Duplicate Implementations

Verify no duplicate functionality will be created:

**Anti-Duplication Checklist:**

- [ ] Searched for existing services with similar names
- [ ] Verified feature doesn't exist in different module
- [ ] Checked if existing service can be extended vs creating new
- [ ] Confirmed no pending PRs implement same feature
- [ ] Reviewed recent ADRs for related decisions

**Output Example:**
```markdown
### Duplicate Implementation Check

✅ **NO DUPLICATES FOUND**

**Verification:**
- [x] Searched for "verification" services - Found 0 matches
- [x] Searched for "hallucination detection" - Found 0 matches
- [x] Checked pending PRs - No related PRs
- [x] Reviewed ADRs - ADR-031 recommends new verification service

**Existing Related Code (to extend, not duplicate):**
- `bullet_generation_service.py` - Will call verification service, not duplicate
- `bullet_validation_service.py` - Input validation only, different concern

**Decision:** Safe to create new `BulletVerificationService` - no duplication risk
```

---

## Discovery Document Output

### Path & Naming (Mandatory)

**Path:** `docs/discovery/`

**Filename Pattern:** `disco-<ID>.md`
- `<ID>` matches the feature/fix/chore ID (e.g., `disco-030.md` for `ft-030`)
- Use same ID for feature, fix, or chore work
- One discovery document per change track

**Examples:**
- `docs/discovery/disco-030.md` (for feature ft-030)
- `docs/discovery/disco-031.md` (for fix fix-031)
- `docs/discovery/disco-032.md` (for chore chore-032)

**Storage:**
- Commit discovery documents to Git (part of project documentation)
- Reference from FEATURE specs (link to discovery findings)
- Keep for future reference (similar changes can learn from past discoveries)

### Document Structure (Required Sections)

Discovery documents must include:

```markdown
# Discovery: <ID> - <Title>

**ID:** <ID> (e.g., 030, 031)
**Type:** Feature | Fix | Chore
**Date:** YYYY-MM-DD
**Size Track:** Micro | Small | Medium | Large
**Author:** <name> or "Claude Code"

## Summary

[1-2 paragraph summary of what was discovered]

## Phase 0: Spec Discovery Results

### Affected Specs
[List of specs with versions]

### Spec-Defined Patterns to Follow
[Contracts, interfaces, configurations extracted from specs]

### Spec Confidence Assessment
[Risk assessment of spec accuracy]

### Spec Update Checklist (for Stage C)
[Which specs need updates and why]

## Phase 1: Spec-Code Validation Results

### Discrepancies Found
[List of spec-code mismatches]

### Spec Confidence Assessment (Post-Validation)
[Updated confidence levels after validation]

### Required Spec Updates (Before Stage C)
[Prioritized list of spec updates needed]

## Phase 2: Test Impact Analysis

### Affected Test Files
[List of test files that will need changes]

### Test Update Checklist
[KEEP/UPDATE/REMOVE/ADD for each test]

### Test Coverage Report
[Current coverage percentages and gaps]

### Test Coverage Gaps to Address
[High priority untested paths]

## Phase 3: Dependency & Side Effect Mapping

### Dependency Map
[Inbound and outbound dependencies]

### Side Effects Inventory
[Database, API, cache, queue operations]

### Impact Radius
[Diagram/list of all affected components]

### High-Risk Areas
[Risk matrix of high-impact + low-coverage areas]

## Phase 4: Reusable Component Discovery

### Similar Feature Search Results
[What similar features exist]

### Reusable Component Inventory
[Table of reusable services/patterns]

### Architecture Patterns to Follow
[Established patterns from docs/architecture/patterns.md]

### Duplicate Implementation Check
[Anti-duplication verification]

## Risk Assessment & Recommendations

### Overall Risk Level
[LOW / MEDIUM / HIGH with justification]

### Key Risks
[Top 3-5 risks identified]

### Mitigation Strategies
[How to address each risk]

### Go/No-Go Recommendation
[Proceed to Stage C? Or need more investigation?]

## Post-Implementation Notes

[Added in Stage I: Spec Reconciliation]
[What actually happened during implementation]
[Architectural decisions made]
[Lessons learned for future similar changes]
```

### Storage Location

**Primary Location:** `docs/discovery/`

**Related Files:**
- Reference from FEATURE specs: `docs/features/ft-<ID>-<slug>.md`
- Reference from TECH SPECS: `docs/specs/spec-<spec>.md` (in changelog if applicable)
- Reference from ADRs: `docs/adrs/adr-<ID>-<slug>.md` (if discovery informed decision)

**Example Cross-References:**

In `docs/features/ft-030-anti-hallucination.md`:
```markdown
**Stage B Discovery:** See `docs/discovery/disco-030.md` for comprehensive
discovery findings including spec validation, test impact, and reusable components.
```

In `docs/specs/spec-llm.md` changelog:
```markdown
- **2025-11-04 [v4.0.0]**: Added source attribution architecture
  (disco-030 Phase 1 identified spec-code discrepancies)
```

---

## Examples & Best Practices

### Example 1: Medium Feature Discovery (ft-030)

**Scenario:** Adding anti-hallucination verification to bullet generation

**Phase 0 Output:**
```markdown
## Phase 0: Spec Discovery Results

### Affected Specs
- spec-llm.md (v4.2.0) - LLM service interfaces
- spec-api.md (v4.2.0) - Generation endpoints
- spec-cv-generation.md (v1.0.0) - Generation pipeline

### Spec-Defined Patterns
**Service Layer:**
- Layer: generation/services/core/
- Parent: BaseLLMService
- Pattern: Circuit breaker for API calls

**Interface to Implement:**
```python
class BaseLLMService:
    async def execute_with_retry(self, task: Task) -> Result:
        pass
```

### Spec Confidence
- spec-llm.md: HIGH (verified 2025-11-04)
- spec-api.md: MEDIUM (verified 2025-10-15)

### Spec Updates Needed
- spec-llm.md → v4.3.0 (add BulletVerificationService)
- spec-api.md → v4.3.0 (add review endpoints)
```

**Phase 1 Output:**
```markdown
## Phase 1: Spec-Code Validation Results

### Discrepancies Found
1. spec-api.md: Endpoint count off by 4
2. spec-llm.md: Model pricing outdated

### Spec Confidence (Post-Validation)
- spec-llm.md: HIGH (interfaces match, pricing minor issue)
- spec-api.md: MEDIUM (endpoint count needs update)

### Required Updates
🟡 HIGH: Update spec-api.md endpoint list (during Stage C)
🟢 MEDIUM: Update spec-llm.md pricing (defer to Stage I)
```

**Phase 2-4:** [Similar detailed outputs]

**Result:** Discovery document created at `docs/discovery/disco-030.md` with all findings documented for reference during design (Stage C).

### Example 2: Small Fix Discovery (Optional)

**Scenario:** Fixing a typo in API response field name

**Decision:** Discovery OPTIONAL for Small changes

**If performed:**
```markdown
# Discovery: 031 - Fix API response field typo

**Size Track:** Small
**Discovery Level:** Quick (Phases 0-2 only)

## Summary
Quick discovery for Small fix. Identified affected tests and specs.

## Phase 0: Spec Discovery
- Affected: spec-api.md (response schema typo)
- Update needed: Fix typo in spec

## Phase 2: Test Impact
- Affected: test_api.py (3 tests checking field name)
- Action: Update tests to use correct field name

## Phase 3-4: Skipped (Small change)

## Risk: LOW (simple typo fix, well-tested)
```

**Result:** Lightweight discovery captures essentials without full 5-phase analysis.

### Best Practices

**DO:**
- ✅ Start with Phase 0 (Spec Discovery) - understand contracts first
- ✅ Document spec confidence levels - know which specs to trust
- ✅ Create test update checklist early - prevents forgotten tests
- ✅ Identify reusable components - avoid reinventing the wheel
- ✅ Save discovery document - future changes benefit from your analysis
- ✅ Reference discovery from FEATURE specs - maintain traceability

**DON'T:**
- ❌ Skip Phase 0 and dive into code - you'll miss architectural context
- ❌ Trust outdated specs blindly - always validate in Phase 1
- ❌ Forget to map dependencies - surprises in testing are expensive
- ❌ Create discovery document then ignore it - use findings in Stage C
- ❌ Duplicate existing functionality - search thoroughly in Phase 4

---

## Enforcement Rules

**From rules/00-workflow.md:**

**BLOCK conditions (must stop and complete discovery):**

1. **Stage B skipped for Medium/Large changes**
   - **Block:** Proceed to Stage C without discovery
   - **Action:** Complete all 5 discovery phases, create disco-<ID>.md

2. **Stage B without test impact analysis (Phase 2)**
   - **Block:** Proceed without test update checklist
   - **Action:** Complete Phase 2, document affected tests

3. **Stage B without dependency mapping (Phase 3)**
   - **Block:** Proceed without dependency graph
   - **Action:** Complete Phase 3, document dependencies and side effects

4. **Duplicate code created when reusable components exist**
   - **Block:** Implementation that duplicates existing functionality
   - **Action:** Refactor to use existing components from Phase 4 discovery

5. **Stage C spec updates without Phase 1 validation**
   - **Block:** Update specs without validating current accuracy
   - **Action:** Complete Phase 1, document spec confidence levels

**Exit Gate Criteria (Stage B → Stage C):**

To proceed from Stage B (Discovery) to Stage C (Specify), MUST have:

- [ ] Discovery document created at `docs/discovery/disco-<ID>.md`
- [ ] Phase 0: Affected specs identified with confidence assessment
- [ ] Phase 1: Spec-code validation completed (if MEDIUM/HIGH confidence risk)
- [ ] Phase 2: Test update checklist created
- [ ] Phase 3: Dependency map and side effects documented
- [ ] Phase 4: Reusable components identified, no duplication confirmed
- [ ] Risk assessment completed with mitigation strategies
- [ ] Go/No-Go recommendation documented

**Review Checkpoint:**

Stage B is part of **REVIEW CHECKPOINT #1: Planning Complete**
- PRD + Discovery + SPECs + ADRs reviewed together
- Discovery findings inform SPEC design in Stage C

---

## Quality Checklist

### Before Marking Discovery Complete

**Completeness:**
- [ ] All 5 phases completed (for Medium/Large changes)
- [ ] Discovery document created with all required sections
- [ ] Spec confidence levels assessed and documented
- [ ] Test impact checklist created
- [ ] Dependency map complete with side effects
- [ ] Reusable components identified
- [ ] Risk assessment with mitigation strategies

**Accuracy:**
- [ ] Spec-code validation performed (Phase 1)
- [ ] Discrepancies documented with line numbers
- [ ] File paths correct and verified
- [ ] Test counts accurate
- [ ] Dependency graph matches actual imports

**Actionability:**
- [ ] Spec update checklist has clear priority levels
- [ ] Test update checklist has KEEP/UPDATE/REMOVE/ADD categories
- [ ] Reusable component inventory has "How to Use" guidance
- [ ] Risk mitigation strategies are specific and actionable
- [ ] Go/No-Go recommendation is clear

**Traceability:**
- [ ] Discovery document references PRD (Stage A)
- [ ] Discovery document will be referenced by FEATURE spec (Stage E)
- [ ] Discovery document will be referenced by TECH SPECs (Stage C)
- [ ] Cross-references include file paths and line numbers

**Storage:**
- [ ] Discovery document saved to `docs/discovery/disco-<ID>.md`
- [ ] Discovery document committed to Git
- [ ] Discovery document mentioned in commit message

---

## Summary

**Key Takeaways:**

1. **Spec-First Philosophy:** Always start with Phase 0 (Spec Discovery) - specs define contracts and architecture
2. **Validate Before Trusting:** Phase 1 (Spec-Code Validation) detects drift - don't assume specs are perfect
3. **Test Impact Early:** Phase 2 identifies affected tests - prevents surprises in Stage F (Write Tests)
4. **Know Your Impact:** Phase 3 maps dependencies - understand cascade effects
5. **Reuse, Don't Reinvent:** Phase 4 finds existing components - avoid duplicate implementations

**Discovery Flow:**
```
SPEC DISCOVERY → SPEC VALIDATION → TEST IMPACT → DEPENDENCIES → REUSABLE COMPONENTS
     ↓                ↓                 ↓               ↓                ↓
  Contracts      Confidence         Test Plan     Impact Map      Reuse Plan
     ↓                ↓                 ↓               ↓                ↓
                      Stage C (Specify - informed by discovery)
```

**Remember:** Discovery is an investment that pays off during implementation. Time spent in discovery prevents duplication, reduces risk, and accelerates development.
