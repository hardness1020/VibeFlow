# Checkpoint Validation Criteria

Detailed validation criteria for each VibeFlow checkpoint.

## Checkpoint #1: Planning Complete (After Stage D)

**Validates:** PRD + Discovery + SPECs + ADRs

### PRD Validation (`docs/prds/prd.md`)

**Required Sections:**
- [ ] Header (version, file, owners, last_updated)
- [ ] Summary (3-5 lines)
- [ ] Problem & Context
- [ ] Users & Use Cases
- [ ] Scope (MoSCoW format)
- [ ] Success Metrics (baseline → target)
- [ ] Non-Goals
- [ ] Requirements (functional + non-functional)
- [ ] Dependencies
- [ ] Risks & Mitigations
- [ ] Analytics & Telemetry

**Quality Checks:**
- No implementation details (belongs in TECH-SPEC/ADRs)
- Success metrics have measurable targets
- Scope uses MoSCoW format (Must/Should/Could/Won't)

### Discovery Validation (`docs/discovery/disco-<ID>.md`)

**Required for:** Medium and Large changes only

**Required Sections:**
- [ ] Header (ID, Type, Date, Size Track, Author)
- [ ] Summary
- [ ] Phase 0: Spec Discovery Results
- [ ] Phase 1: Spec-Code Validation Results
- [ ] Phase 2: Test Impact Analysis
- [ ] Phase 3: Dependency & Side Effect Mapping
- [ ] Phase 4: Reusable Component Discovery
- [ ] Risk Assessment & Recommendations
- [ ] Go/No-Go Recommendation

**Quality Checks:**
- All 5 phases completed for Medium/Large changes
- Spec confidence levels documented
- Test update checklist created
- No duplicate functionality will be created

### Tech Spec Validation (`docs/specs/spec-<name>.md`)

**Required Sections:**
- [ ] Header (version, file, status, PRD link, contract versions)
- [ ] Overview & Goals
- [ ] Architecture (topology diagram + component inventory)
- [ ] Interfaces & Data Contracts
- [ ] Data & Storage
- [ ] Reliability & SLIs/SLOs
- [ ] Security & Privacy
- [ ] Evaluation Plan

**Quality Checks:**
- Table of Contents present if >800 lines
- No implementation code (interface signatures only)
- Architecture has both topology diagram AND component inventory
- Version incremented for contract/SLO/framework changes

### ADR Validation (`docs/adrs/adr-<ID>-<slug>.md`)

**Required Sections:**
- [ ] Title with decision summary
- [ ] Header (File, Status)
- [ ] Context
- [ ] Decision
- [ ] Consequences (+/-)
- [ ] Alternatives
- [ ] Rollback Plan
- [ ] Links (PRD/SPEC/FEATURE references)

**Quality Checks:**
- Status is Draft, Accepted, or Rejected
- Non-trivial decisions have ADRs (new deps, storage patterns, auth changes)
- Consequences include both positive and negative

---

## Checkpoint #2: Design Complete (After Stage E)

**Validates:** FEATURE spec

### Feature Spec Validation (`docs/features/ft-<ID>-<slug>.md`)

**Required Sections:**
- [ ] Header (ID, File, Owner, TECH-SPECs)
- [ ] Stage B Discovery Findings (for Medium/Large)
  - [ ] Test Impact Analysis
  - [ ] Existing Implementation Analysis
  - [ ] Dependency & Side Effect Mapping
- [ ] Architecture Conformance
- [ ] API Design (function/class signatures)
- [ ] Acceptance Criteria
- [ ] Design Changes
- [ ] Test & Eval Plan
- [ ] Telemetry & Metrics
- [ ] Edge Cases & Risks

**API Design Requirements:**
- [ ] Exact function/class names specified
- [ ] Parameters with types and defaults
- [ ] Return types with structure
- [ ] API endpoints if applicable (method, path, schemas)

**Quality Checks:**
- Links to TECH-SPECs with version numbers
- Acceptance criteria are testable (can be Gherkin or checklist)
- API Design section present with exact signatures
- `docs/features/schedule.md` updated

---

## Checkpoint #3: Tests Complete (After Stage F)

**Validates:** Failing unit tests with implementation stubs

### Test Files Validation

**Requirements:**
- [ ] Implementation stubs exist with function signatures from FEATURE spec
- [ ] Stubs raise "not implemented" errors with helpful messages
- [ ] Unit test files exist for new functionality
- [ ] Tests import actual implementation stubs (not mock names)
- [ ] Tests have proper categorization tags (unit/integration + module)

**Test Quality Checks:**
- [ ] All tests currently FAIL (RED phase)
- [ ] Tests fail with "not implemented" errors (not import errors)
- [ ] External dependencies are mocked
- [ ] Test names follow pattern: `test_<what>_<condition>_<expected>`
- [ ] Tests validate behavior from acceptance criteria

### Deprecated Test Handling

**Requirements:**
- [ ] Stage B test update checklist reviewed
- [ ] Deprecated tests updated or removed with justification
- [ ] No obsolete tests remaining

---

## Checkpoint #4: Implementation Complete (After Stage H)

**Validates:** Passing tests + refactored code + quality validation

### Test Status Validation

**Requirements:**
- [ ] All unit tests PASS (GREEN)
- [ ] Integration tests written for I/O boundaries
- [ ] All integration tests PASS
- [ ] No test regressions

### Stage H.4 Quality Validation

**Test Organization:**
- [ ] File structure follows conventions
- [ ] Test classes have descriptive names
- [ ] Test methods use `test_<what>_<condition>_<expected>`
- [ ] Related tests grouped together
- [ ] Unit and integration tests separated

**Test Usefulness:**
- [ ] Tests based on acceptance criteria
- [ ] All acceptance criteria have tests
- [ ] Tests validate behavior, not implementation
- [ ] Happy path, edge cases, and error cases tested

**Test Code Quality:**
- [ ] External dependencies mocked in unit tests
- [ ] Test data uses factories/fixtures
- [ ] Arrange-Act-Assert pattern clear
- [ ] No commented-out or skipped tests without justification

**Test Categorization:**
- [ ] All tests have speed/scope tags
- [ ] All tests have module tags
- [ ] No real API calls in "unit" or "fast" tests

**Performance & Reliability:**
- [ ] Unit tests run <1s each
- [ ] Integration tests run <5s each
- [ ] Tests pass consistently (no flaky tests)

**Quality Gate:**
- 0-2 minor violations: PASS
- 3-5 violations: CONDITIONAL (fix critical first)
- 1 major violation: CONDITIONAL (fix major, review all)
- 6+ violations OR 2+ major: FAIL (refactor tests)

---

## Checkpoint #5: Release Ready (After Stage J)

**Validates:** OP-NOTE + Spec Reconciliation

### Spec Reconciliation (Stage I)

**Requirements:**
- [ ] Implementation vs design reviewed
- [ ] Architectural deviations documented
- [ ] Affected specs updated with new versions
- [ ] Discovery document has Post-Implementation Notes
- [ ] ADRs created for non-trivial implementation decisions

### OP-NOTE Validation (`docs/op-notes/op-<ID>-<slug>.md`)

**Required Sections:**
- [ ] Header (File, Date, Features)
- [ ] Preflight (prerequisites, migrations, flags, env vars)
- [ ] Deploy Steps (ordered commands + verification)
- [ ] Monitoring (dashboards, alerts, SLOs)
- [ ] Runbook/Playbooks (symptom → diagnose → remediate)
- [ ] Rollback (steps + data compatibility)
- [ ] Post-Deploy Checks (smoke tests, owners)

**Quality Checks:**
- [ ] No secrets in env vars section
- [ ] Migrations tested in staging
- [ ] Rollback steps are precise
- [ ] `docs/op-notes/index.md` updated

---

## Checkpoint #6: Deployed (After Stage L)

**Validates:** Deployment verified + indices updated

### Deployment Verification

**Requirements:**
- [ ] OP-NOTE steps followed
- [ ] Post-deploy checks passed
- [ ] Canary (if specified) successful
- [ ] Dashboards show healthy metrics
- [ ] No alerts triggered

### Index Updates

**Requirements:**
- [ ] `docs/specs/index.md` - Current version marked
- [ ] `docs/features/schedule.md` - Status shows Done
- [ ] `docs/op-notes/index.md` - Latest note linked
- [ ] PRD/FEATURE/ADR links are reciprocal

### Close Loop

**Requirements:**
- [ ] Release tagged in Git
- [ ] Issues closed with "Closes #<ID>"
- [ ] Retrospective TODOs captured (if any)
- [ ] Feature flags toggled as per OP-NOTE

---

## Validation Matrix Summary

| Checkpoint | Required Artifacts | Blocking Criteria |
|------------|-------------------|-------------------|
| #1 Planning | PRD, Discovery*, SPECs, ADRs | Missing required sections, no architecture diagram |
| #2 Design | FEATURE with API Design | Missing API signatures, no acceptance criteria |
| #3 Tests | Stubs + Failing unit tests | Tests don't fail, import errors, missing categorization |
| #4 Implementation | Passing tests + H.4 quality | Tests failing, 6+ quality violations |
| #5 Release | OP-NOTE + reconciled specs | Missing runbook/rollback, specs not updated |
| #6 Deployed | Verified + indices updated | Post-deploy checks failed, indices not updated |

*Discovery required for Medium/Large changes only
