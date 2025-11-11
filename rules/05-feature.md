# FEATURE — Executable Spec per Deliverable

## When to use
- For every ticket/deliverable before starting branch/PR; update during development.

## Key Rules

### Path & Naming (mandatory)
- **Path:** `docs/features/`
- **Naming:** `ft-<ID>-<slug>.md` (e.g., `ft-001-hover-badge.md`)
- **Schedule file:** `docs/features/schedule.md` (IDs, titles, status; keep in sync)

### Linking & Traceability
- Each feature file must link its upstream artifacts:
  - **TECH-SPECs:** `docs/specs/spec-<spec>.md` (with version number, e.g., v1.3)
  - **Stage B Discovery Findings:** Reference codebase analysis from Stage B

### Required sections (must include)
  - **Header:** ID, file, owner, TECH-SPECs
  - **Stage B Discovery Findings** (from Stage B codebase discovery) — for Medium/Large features
    - **Test Impact Analysis** (test update checklist, coverage gaps)
    - **Existing Implementation Analysis** (reusable components, similar features)
    - **Dependency & Side Effect Mapping** (dependencies, side effects, risk areas)
  - **Architecture Conformance** (layer assignment, pattern compliance) — for all features
  - **Acceptance Criteria** (clear, testable; Gherkin or checklist)
  - **Design Changes** (UI/API/schema diffs; examples)
  - **Test & Eval Plan** (unit/integration + AI eval thresholds & goldens)
  - **Telemetry & Metrics to watch** (dashboards, alerts)
  - **Edge Cases & Risks**
- **Traceability:** Use `<ID>` in branch (`feat/<ID>-slug`), PR title `[<ID>]`, and commits `... (#<ID>)`.


## Example

### Example 1: Medium Feature (with discovery analysis)
```md
# Feature — 001 hover-badge
**File:** docs/features/ft-001-hover-badge.md
**Owner:** Marcus
**TECH-SPECs:** `spec-api.md` (v1.3), `spec-frontend.md` (v2.1)

## Stage B Discovery Findings

### Test Impact Analysis
**Tests to Update:**
- `tests/llm_services/test_scoring_service.py` - update mocked responses to include rationales
- `tests/generation/test_views.py` - update endpoint response schema assertions

**Tests to Remove:**
- None

**Coverage Gaps:**
- Circuit breaker failure scenarios (coverage: 45%) - need integration tests
- UI component state transitions (coverage: 60%) - need unit tests

**Test Update Checklist:**
- [ ] Update `test_scoring_service.py` for new rationales field
- [ ] Update `test_views.py` for new endpoint response
- [ ] Add circuit breaker integration tests (Stage H)
- [ ] Add UI state transition unit tests (Stage F)

### Existing Implementation Analysis
**Similar Features:**
- `llm_services/services/core/tailored_content_service.py` - existing LLM scoring pattern
- `generation/services/bullet_generation_service.py` - retry logic with circuit breaker

**Reusable Components:**
- `llm_services/services/reliability/circuit_breaker.py` - use for external API calls
- `llm_services/services/infrastructure/model_selector.py` - for model selection

**Patterns to Follow:**
- Service layer pattern: base → core → infrastructure → reliability (see `docs/architecture/patterns.md`)
- Task executor with retries from `llm_services/services/base/task_executor.py`

**Code to Refactor:** None (new feature)

### Dependency & Side Effect Mapping
**Dependencies:**
- `EmbeddingService` for semantic similarity
- `CircuitBreaker` for LLM API fault tolerance
- `ModelSelector` for model routing

**Side Effects:**
- Database writes to `scores` table (new table, no impact on existing)
- Redis cache writes with TTL 24h (no impact on existing cache keys)

**Impact Radius:**
- Frontend: New UI component (isolated, no impact on existing components)
- Backend: New endpoint (no changes to existing endpoints)

**Risk Areas:**
- Circuit breaker state management (low test coverage) - HIGH RISK
- LLM API timeout handling (untested) - MEDIUM RISK

## Architecture Conformance
**Layer Assignment:**
- New service in `llm_services/services/core/credibility_service.py` (core layer)
- API endpoint in `generation/views.py` (interface layer)

**Pattern Compliance:**
- Follows llm_services service structure ✓
- Uses circuit breaker for external calls ✓
- Implements retry logic via task executor ✓

**Dependencies:**
- `llm_services.services.base.BaseService` (inheritance)
- `llm_services.services.reliability.CircuitBreaker` (composition)
- `llm_services.services.infrastructure.ModelSelector` (composition)

## Acceptance Criteria
- [ ] Badge shows G/Y/R ≤200ms with cache hit
- [ ] Tooltip lists top-3 rationales
- [ ] Works on en/zh pages; degrades gracefully if scores missing
- [ ] Circuit breaker activates after 5 consecutive failures
- [ ] Retries up to 3 times with exponential backoff

## Design Changes
Endpoint `/v1/score` + new UI component `<CredBadge />`
Schema diff: add `rationales[]: string[≤3]`

## Test & Eval Plan
- Unit: score mapper, UI renders states, circuit breaker logic
- Integration: end-to-end DOM test, database persistence
- AI eval: goldens v0.4, F1≥0.72 must pass

## Telemetry
Dashboards: badge latency p95, error rate, circuit breaker state; alert >2% errors

## Edge Cases & Risks
Very long articles; unsupported langs → fallback "Check Article"
Circuit breaker open → serve stale cached results or neutral state
```

### Example 2: Small Feature (minimal discovery)
```md
# Feature — 015 export-filename
**File:** docs/features/ft-015-export-filename.md
**Owner:** Sarah
**TECH-SPECs:** `spec-api.md` (v1.3)

## Architecture Conformance
**Layer Assignment:** Update to existing `export/services/document_service.py`
**Pattern Compliance:** Follows existing export service pattern ✓
**Dependencies:** None (isolated change)

## Acceptance Criteria
- [ ] User can specify custom filename for exported CV
- [ ] Default filename includes date: `CV_YYYY-MM-DD.pdf`
- [ ] Filename sanitized to prevent path traversal

## Design Changes
Add `filename` optional param to `POST /api/v1/export`

## Test & Eval Plan
- Unit: filename sanitization, date formatting
- Integration: end-to-end export with custom filename

## Telemetry
Monitor export success rate (should remain stable)

## Edge Cases & Risks
Special characters in filename → sanitize to alphanumeric + dash/underscore
```