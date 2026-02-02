# Project Workflow — Single Source of Truth

## Purpose and Scope
- This is the **top governance rule**. All development activities must conform.
- **Docs-first mandate:** **Generate or update required docs _before_ generating code.** Code must **follow** the documented contracts, topology, framework roles, and SLOs.
- **Stage gating & human review:** At **each stage**, the assistant **generates the required file(s)** and **stops for human review/approval** before moving to the next stage.
- **Rule Compliance:** Each stage must follow its corresponding rule format and standards.


## Authoritative Paths & Naming
- **PRD** → `docs/prds/prd.md` (single PRD file per project; edit directly for all changes)
- **SPEC (TECH SPEC)** → `docs/specs/spec-<spec>.md` (no subdirs; `<spec>` in `{system, api, frontend, llm, ...}`; maintain `docs/specs/index.md`)
  - **Architecture section contains only:** (1) **comprehensive diagram** (frameworks + relationships) and (2) **component inventory table**.
  - Minor edits → update file; material contract/SLO/framework/topology change → **increment version** + Git tag.
- **ADR** → `docs/adrs/adr-<ID>-<slug>.md` (non-trivial decisions; lifecycle: Draft → Accepted | Rejected | Superseded)
- **FEATURE** → `docs/features/ft-<ID>-<slug>.md` (+ keep `docs/features/schedule.md`)
- **OP-NOTE (Runbook)** → `docs/op-notes/op-<ID>-<slug>.md` **or** `docs/op-notes/op-release-<semver>.md` (+ `docs/op-notes/index.md`)
- **Trace IDs:** use ticket/feature ID like `ft-123` in files/branches/PRs/commits.


## Size-Based Workflow Tracks

Not all changes require the full workflow. Choose the appropriate track based on scope:

| **Track** | **Scope** | **Required Stages** | **Example** |
|-----------|-----------|---------------------|-------------|
| **Micro** | Bug fix, typo, small refactor | F → G (TDD only) | Fix typo in error message, update config value |
| **Small** | Single feature, no contracts | E → F → G → H | Add field to existing form, UI polish |
| **Medium** | Multi-component, no new services | B → C → D → E → F → G → H → I → J | New API endpoint using existing services |
| **Large** | System change, new contracts/services | Full A → L | New LLM integration, new auth system |

## Review Checkpoint Strategy

Instead of 12 individual stops, reviews are grouped into **6 strategic checkpoints**:

1. **Planning Complete** (after Stage D): PRD + Discovery + SPECs + ADRs reviewed together
2. **Design Complete** (after Stage E): FEATURE spec reviewed
3. **Tests Complete** (after Stage F): Failing tests reviewed
4. **Implementation Complete** (after Stage H): Working + refactored code reviewed
5. **Release Ready** (after Stage J): OP-NOTE reviewed
6. **Deployed** (after Stage L): Post-deployment verification

**Note:** Teams can opt into more granular stops if needed, but default is these 6 checkpoints.

## End-to-End Pipeline

### Stage A — **Initiate**
- **Input:** Problem or idea.
- **Action:** If scope affects product goals/metrics → create/update **PRD** (`prd.md`). Minor bug/chores can skip to Stage E with a short note in PR.
- **Output (generate file):** `docs/prds/prd.md` (or link existing).
- **Rule Compliance:** Generated PRD must follow `rules/01-prd.md format and standards.
- **Exit Gate:** PRD exists **or** justified exemption noted in PR.

### Stage B — **Codebase Discovery**
- **Input:** PRD and initial requirements.
- **Action:** Search and analyze existing codebase **before** designing new solutions. Follow **spec-driven discovery** approach (specs first, then code validation).
- **Discovery Phases:** (See `rules/02-discovery/policy.md` for comprehensive guidance)
  0. **Spec Discovery** (mandatory first) - Analyze existing specs, extract contracts and patterns
  1. **Spec-Code Validation** - Verify specs match reality, assess confidence, document drift
  2. **Test Impact Analysis** - Identify affected tests, create test update checklist, map coverage gaps
  3. **Dependency & Side Effect Mapping** - Trace dependencies, identify side effects, map impact radius
  4. **Reusable Component Discovery** - Find similar features, identify reusable patterns, prevent duplication
- **Output (generate file):** `docs/discovery/disco-<ID>.md` with:
  - **Spec discovery results** (affected specs, confidence assessment, patterns to follow)
  - **Spec-code validation results** (discrepancies found, required spec updates)
  - **Test update checklist** (tests to update/remove/add) with file paths
  - **Test coverage report** (coverage %, gaps, untested paths affected)
  - **Dependency map** (inbound/outbound dependencies, impact radius)
  - **Side effects inventory** (database, API, cache, queue operations)
  - **Reusable component inventory** (services/patterns to use)
  - **Risk assessment** (risk level, key risks, mitigations, go/no-go recommendation)
- **Rule Compliance:** Discovery document must follow `rules/02-discovery/policy.md` format and standards.
- **Exit Gate:** Discovery document created at `docs/discovery/disco-<ID>.md` with all phases completed, risk assessment, and confirmation that no duplicate functionality will be created.

### Stage C — **Specify (TECH SPECS)**
- **Action:** Update existing SPECs first, create new only if needed. Use versioned single files: `spec-<spec>.md`.
- **Pre-Check (mandatory):**
  1. List all existing specs from `docs/specs/index.md`
  2. For each existing spec, check if change affects it (contracts/topology/framework roles/SLOs)
  3. **Default: Update existing affected specs FIRST**
  4. Create new spec **only if** scope doesn't fit any existing spec
  5. Document spec update justification (why update vs. create)
- **Architecture (required):** add **diagram (frameworks+relationships)** and **component inventory**; link latest PRD and Stage B discovery findings.
- **Output (generate file):** relevant SPEC(s) `spec-<spec>.md` with:
  - **Architecture:** comprehensive diagram (frameworks + relationships) **and** component inventory table.
  - Links to latest PRD and discovery findings; version number.
  - **Spec update justification** (if creating new spec, explain why existing specs don't fit)
  - **Cross-spec impact summary** (which other specs are affected)
- **Rule Compliance:** Generated SPECs must follow `rules/03-tech_spec.md` format and standards.
- **Exit Gate:** For any change to **contracts/topology/framework roles/SLOs**, SPEC updated with new version and listed as **Current** in `docs/specs/index.md`. Spec update/create decision documented.

### Stage D — **Decide (ADRs)**
- **Action:** For any non-trivial choice (new dependency, auth model, storage pattern, schema versioning, SLO shifts), add **ADR**.
- **Output (generate file):** `docs/adrs/adr-<ID>-<slug>.md` for non-trivial choices (deps, storage, auth, versioning, SLO moves).
- **Rule Compliance:** Generated ADRs must follow `rules/04-adr.md` format and standards.
- **Exit Gate:** PR references ADR(s); code relying on the decision cannot merge without an **Accepted** ADR.
- **REVIEW CHECKPOINT #1:** **Planning Complete** (PRD + Discovery + SPECs + ADRs reviewed together)

### Stage E — **Plan (FEATURE)**
- **Action:** Create **FEATURE** spec `ft-<ID>-<slug>.md`; update `docs/features/schedule.md`.
- **Must include:** Acceptance criteria, design diffs (UI/API/schema), test & eval plan (goldens + thresholds for LLM paths), risks, **existing implementation analysis**, **architecture conformance**.
- **Output (generate file):** `docs/features/ft-<ID>-<slug>.md` (+ update `docs/features/schedule.md`) with:
  - Acceptance criteria; design diffs (UI/API/schema); test & eval plan; risks.
  - **Existing implementation analysis** (from Stage B discovery)
  - **Architecture conformance** (layer assignment, pattern compliance)
- **Rule Compliance:** Generated FEATURE must follow `rules/05-feature.md` format and standards.
- **Exit Gate (DoR):** FEATURE file present with all required sections + links to SPEC + discovery findings + reuse checklist complete.
- **REVIEW CHECKPOINT #2:** **Design Complete** (FEATURE spec reviewed)

### Stage F — **Write Unit Tests First (Hybrid TDD - RED Phase)**
- **Action:** Handle deprecated tests, create implementation stubs from FEATURE spec API design, then write **failing unit tests** for the feature/fix per acceptance criteria.
- **TDD Mandate:** Unit tests MUST be written **before** implementation code. See `rules/06-tdd/policy.md` for detailed Hybrid TDD workflow.
- **Three Substeps:**
  1. **Test Cleanup** (using Stage B test update checklist):
     - Update deprecated tests to align with new feature design
     - Remove obsolete tests that are no longer relevant
     - Document why tests were removed/updated
  2. **Create Implementation Stubs** (from FEATURE spec API design):
     - Extract function/class signatures from FEATURE spec "API Design" section
     - Create stub files with exact function names, parameters, and return types from spec
     - Use "not implemented" markers with helpful messages describing expected behavior
     - Verify stubs are importable (if stub creation reveals naming issues → STOP and update FEATURE spec)
  3. **Write New Failing Unit Tests:**
     - Import stubs to ensure names resolve correctly
     - Write tests using exact signatures from FEATURE spec
     - Use descriptive assertions and verify "not implemented" errors
     - Focus on business logic with all external dependencies mocked
     - Tests should clarify requirements and validate API design
     - Apply proper test categorization tags (unit/fast/module - see `rules/06-tdd/policy.md`)
- **Test Coverage:** Unit tests for business logic with all external dependencies mocked. **Defer integration tests to Stage H.**
- **LLM Paths:** For LLM/prompt changes, create unit tests with mocked LLM responses (goldens + eval harness deferred to Stage H).
- **Output (generate files):**
  - Updated/cleaned up test files (deprecated tests handled)
  - Implementation stub files with function signatures and "not implemented" markers
  - New unit test files with failing tests that define expected behavior and use proper tags
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/06-tdd/policy.md`.
- **Exit Gate:** All deprecated tests handled (updated/removed with justification) + implementation stubs created with correct function signatures from FEATURE spec + new failing unit tests exist that use actual implementation names, have proper categorization tags, and fully specify expected behavior + new tests verified failing when run in isolation.
- **REVIEW CHECKPOINT #3:** **Unit Tests Complete** (test cleanup + stubs + failing unit tests reviewed)

### Stage G — **Implement to Pass Unit Tests (Hybrid TDD - GREEN Phase)**
- **Action:** Write **minimal code** to make **unit tests** pass (TDD green phase).
- **Rules:** Do **not** change public contracts without SPEC/ADR updates already in place.
- **Docs-first enforcement:** If contracts change unexpectedly, **stop** and update SPEC/ADR first.
- **Reuse enforcement:** Leverage components identified in Stage B; avoid duplicating existing code.
- **Output:** Implementation code that makes all unit tests pass.
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/06-tdd/policy.md`.
- **Exit Gate:** All unit tests green; no regressions; code follows established patterns from Stage B discovery. **Integration tests not required yet.**

### Stage G.1 — **Handling Design Changes During Implementation**

If implementation reveals design flaws or better approaches, follow this protocol to maintain docs-first discipline.

**Purpose:** Ensure design changes are documented before code is written, maintaining contract integrity and traceability.

**Immediate Stop Conditions (BLOCK and go back):**

Contract changes require stopping implementation and updating documentation first:
- **API/Interface signatures** (function names, parameters, return types, error handling)
- **Database schemas** (tables, columns, relationships, indexes exposed to other services)
- **Event formats** (message structure, event types, payload schemas)
- **External service contracts** (webhook formats, API endpoints, authentication flows)
- **New external dependencies** (libraries, services, APIs requiring approval/licensing)
- **SLO changes** (performance targets, availability requirements, error rate thresholds)

**Allowed Without Blocking (handle in Stage I):**

These changes are internal implementation details that don't affect contracts:
- Internal algorithms and data structures
- Private function/method names and signatures
- Error handling improvements (within existing error taxonomy)
- Performance optimizations (within SLO bounds)
- Code organization and refactoring (no public API changes)
- Internal helper functions and utilities

**Protocol for Contract Changes:**

1. **STOP implementation immediately**
   - Do not write more code
   - Commit current work if needed (mark as WIP)
   - Document the discovered issue/better approach

2. **Update SPEC first:**
   - Document new contract design in affected SPEC file
   - Increment SPEC version (follow change-control tripwires)
   - Update architecture diagram if topology changed
   - Link to ADR if new dependency/framework involved
   - Set "Last Verified" date and confidence level

3. **Create/Update ADR if needed:**
   - Non-trivial decisions require ADR (new dependency, storage pattern change, etc.)
   - Document why change is necessary
   - Consider alternatives and trade-offs
   - Mark as "Accepted" before proceeding

4. **Update tests next (return to Stage F):**
   - Update failing tests to reflect new contract
   - Ensure tests still use "not implemented" markers (back to RED)
   - Update test documentation with design change rationale
   - Update stub implementations if function signatures changed
   - Apply proper test categorization if test type changed

5. **Resume implementation (Stage G):**
   - Implement to pass updated tests
   - Follow new contract from updated SPEC
   - Reference SPEC version in code comments

**Note:** See `rules/06-tdd/policy.md` for detailed examples of handling design changes during implementation.

**Decision Matrix:**

| Change Type | Example | STOP? | Update Order | Stage |
|-------------|---------|-------|--------------|-------|
| API signature | Function params/return type changed | YES | SPEC → ADR → Tests → Code | G.1 → F → G |
| Database schema | New table/column exposed to API | YES | SPEC → Migration → Tests → Code | G.1 → F → G |
| Event format | Message structure changed | YES | SPEC → ADR → Tests → Code | G.1 → F → G |
| New dependency | Adding Redis, Kafka, new library | YES | ADR → SPEC → Tests → Code | G.1 → F → G |
| SLO change | Latency target changed | YES | SPEC → Tests → Code | G.1 → F → G |
| Algorithm change | Different sorting approach | NO | Code → Stage I reconciliation | Continue G |
| Error handling | Better error messages | NO | Code → Stage I reconciliation | Continue G |
| Private function | Internal helper renamed | NO | Code only | Continue G |
| Performance opt | Caching added (within SLO) | NO | Code → Stage I reconciliation | Continue G |

**Enforcement:**

The workflow will BLOCK if:
- Contract changes detected during implementation without SPEC update
- SPEC version not incremented for material contract changes
- ADR missing for non-trivial decisions (new dependencies, storage changes)
- Tests not updated to reflect new contract

**Benefits:**
- Maintains docs-first discipline even when design flaws discovered late
- Clear decision trail for why contracts changed
- Tests always reflect current contract specification
- No divergence between documentation and implementation

### Stage H — **Write Integration Tests & Refactor (Hybrid TDD - REFACTOR Phase)**
- **Action:** Write integration tests for I/O boundaries, pass them, refactor code, then validate test quality before completion.
- **Four Substeps:**
  1. **Write Integration Tests:** For API endpoints, database operations, external service calls, LLM pipelines, file I/O (see `rules/06-tdd/policy.md` for mandatory list) with proper categorization tags
  2. **Pass Integration Tests:** Implement any missing integration code to make integration tests green, verify new integration tests pass in isolation before running full suite
  3. **Refactor:** Clean up code while keeping all tests (unit + integration) green
  4. **Test Quality Validation (MANDATORY):** Complete Stage H.4 quality checklist from `rules/06-tdd/policy.md` - validate test organization, usefulness, code quality, categorization, and reliability
- **Clean Code:** Remove duplication, improve naming, optimize algorithms, enhance error handling.
- **Documentation:** Add inline docs, update API docs if needed.
- **Pattern Compliance:** Verify code follows architecture patterns identified in Stage B.
- **Output:** Refactored code with all tests (unit + integration) passing and validated for quality.
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/06-tdd/policy.md`.
- **Exit Gate:** All tests (unit + integration) green + new tests verified passing in isolation before full suite run + Stage H.4 test quality validation completed with fewer than 3 violations + code meets quality standards + performance acceptable.
- **REVIEW CHECKPOINT #4:** **Implementation Complete** (working + refactored code with full test coverage and validated test quality reviewed)

### Stage I — **Spec Reconciliation**
- **Purpose:** Update specs if implementation deviated from design. Ensure specs reflect actual implementation.
- **Action:** Review implementation against original specs from Stage C; document and justify architectural deviations; update affected specs.
- **Checklist:**
  1. **Review implementation vs. design:** Compare final code to specs created in Stage C
  2. **Identify architectural deviations:**
     - Interface signatures changed from spec design?
     - New dependencies added not in original spec?
     - Configuration schemas extended beyond spec definition?
     - Performance characteristics different from SLOs?
  3. **Decision matrix for each deviation:**
     - Was deviation necessary? (Document reason - becomes ADR if non-trivial)
     - Should spec be updated? (YES if contract/topology changed)
     - Should implementation be revised? (YES if violated architectural principles)
  4. **Update affected specs if contract changes occurred:**
     - Increment spec version per change-control tripwires
     - Update "Last Verified" metadata to today (if spec includes confidence tracking)
     - Set confidence level to HIGH (just verified)
  5. **Update discovery document** (`docs/discovery/disco-<ID>.md`):
     - Add "Post-Implementation Notes" section
     - Document lessons learned for future similar changes
     - Assess discovery accuracy (predictions vs. reality)
  6. **Update architecture patterns** (`docs/architecture/patterns.md`) if new pattern emerged
- **Output:**
  - Updated specs (if contracts/topology changed)
  - ADRs for non-trivial architectural decisions made during implementation
  - Updated discovery document with post-implementation notes
  - Updated architecture patterns (if applicable)
- **Enforcement:**
  - **BLOCK:** Contract changes without spec version update
  - **BLOCK:** Significant architectural deviation without ADR justification
  - **BLOCK:** Spec marked as affected in Stage C but not reviewed in Stage I
- **Exit Gate:** All specs updated to reflect final implementation; discovery document includes post-implementation notes; architectural decisions documented.

### Stage J — **Release Preparation (OP-NOTE)**
- **Action:** Write **OP-NOTE** (per feature or release). Include preflight (migrations/env/flags), deploy steps, monitoring, playbooks, rollback, post-deploy checks.
- **Output (generate file):** `docs/op-notes/op-<ID>-<slug>.md` or `op-release-<semver>.md` with preflight, deploy steps, monitoring, playbooks, rollback, post-deploy checks.
- **Rule Compliance:** Generated OP-NOTE must follow `rules/07-op_note.md` format and standards.
- **Exit Gate:** OP-NOTE complete with all deployment steps documented.
- **REVIEW CHECKPOINT #5:** **Release Ready** (OP-NOTE reviewed)

### Stage K — **Deploy & Verify**
- **Action:** Follow OP-NOTE; canary if specified; run smoke tests; watch dashboards/alerts.
- **Exit Gate:** Post-deploy checks passed; toggle flags as per OP-NOTE; `docs/op-notes/index.md` updated.

### Stage L — **Close Loop**
- **Action:** Update `docs/specs/index.md` (mark Current version); ensure PRD/FEATURE/ADR links are reciprocal; tag release; **close issues with "Closes #<ID>"**.
- **Exit Gate:** Schedule shows **Done**; retrospective TODOs captured (if any).
- **REVIEW CHECKPOINT #6:** **Deployed** (post-deployment verification)


## Stage Gating & Review Requirements
- **Strategic Checkpoints:** The workflow uses **6 grouped review checkpoints** (see "Review Checkpoint Strategy" above).
- **Rule Compliance:** Each generated file must follow its corresponding rule format and standards.
- **Checkpoint Stops:** The agent must stop at each of the 6 review checkpoints and wait for human approval.
- **Granular Option:** Teams can request additional stops between stages if needed, but default is 6 checkpoints.
- **No Auto-Advance:** The agent is **forbidden** from automatically proceeding past a checkpoint without explicit human approval.


## Change-Control Tripwires (version update triggers)
- **Contracts:** API/GraphQL/webhook/event schemas, headers, status/error taxonomy, DB schemas exposed to others, model/prompt I/O.
- **Topology:** components/paths/protocols/trust boundaries (e.g., adding Redis/Celery, async flows).
- **Framework roles:** Django/DRF, React, Redis (cache vs broker), Celery, Postgres, gateways, SSR/SPA changes.
- **SLOs:** availability/latency/error-rate/freshness targets.
→ If any tripwire is hit, **increment SPEC version** (e.g., v1.0.0 → v2.0.0), update index, tag in Git, and reference ADRs.


## Git Control Guidelines (User-Driven)
**Note:** Version control is managed by the user. These are recommended conventions to maintain traceability:

### Branch Naming
- **Feature:** `feat/<ID>-<slug>` or `feat/ft-<ID>-<slug>`
- **Bug Fix:** `fix/<ID>-<slug>` or `fix/bug-<ID>-<slug>`
- **Chore/Refactor:** `chore/<ID>-<slug>`
- **Hotfix:** `hotfix/<ID>-<slug>`

### Commit Conventions (Conventional Commits)
- **Format:** `<type>(scope): subject (#<ID>)`
- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **Examples:**
  - `feat(api): add user authentication endpoint (#ft-123)`
  - `fix(ui): resolve dropdown rendering issue (#bug-456)`
  - `test(auth): add unit tests for JWT validation (#ft-123)`

### When to Commit (Recommendations)
- After writing failing tests (TDD red phase)
- After making tests pass (TDD green phase)
- After refactoring (TDD refactor phase)
- When switching context or taking a break
- Before any risky changes

## Traceability (IDs everywhere)
- **Documentation:** `ft-123-<slug>.md`, `op-123-<slug>.md`, `adr-<ID>-<slug>.md`
- **Git (user-controlled):** Branch `feat/ft-123-<slug>` • PR `[ft-123] <title>` • Commits `<type>(scope): subject (#ft-123)`
- **Code Comments:** Reference ticket/feature IDs in TODOs and FIXMEs


## Enforcement (automatic blockers)
- Code generated **before** required docs exist/updated → **block** and generate the missing doc file(s) first.
- **Stage B (Codebase Discovery) skipped for Medium/Large changes** → **block** and perform discovery analysis first.
- **Stage B without test impact analysis for Medium/Large** → **block** and complete test impact checklist (affected tests, coverage gaps, test update plan).
- **Stage B without dependency & side effect mapping for Medium/Large** → **block** and document dependencies, side effects, and risk areas.
- **Duplicate code created when reusable components exist** → **block** and refactor to use existing components.
- **Stage C creating new spec before checking existing specs** → **block** and review existing specs from `docs/specs/index.md` first; update existing if applicable.
- **Stage F without handling deprecated tests first** → **block** and complete test cleanup (update/remove deprecated tests from Stage B checklist).
- **Implementation code written before unit tests** → **block** and write failing unit tests first (Hybrid TDD violation).
- **Unit tests not failing initially** → **block** and verify tests specify new behavior.
- **Stage E (FEATURE) without API Design section** → **block** and add function/class signatures with exact names, parameters, and return types.
- **Stage F without creating implementation stubs** → **block** and create stub files with function signatures from FEATURE spec before writing tests.
- **Stage F tests without proper categorization tags** → **block** and add speed/scope tags (unit/integration/e2e) + module tags (see `rules/06-tdd/policy.md`).
- **Stage F tests using names not in FEATURE spec or stubs** → **block** and update FEATURE spec or use correct stub names.
- **Stage G contract changes without following Stage G.1 protocol** → **block** and update SPEC → ADR → Tests before resuming implementation.
- **Stage H without integration tests for I/O operations** → **block** and write integration tests first (see mandatory list in `rules/06-tdd/policy.md`).
- **Stage H without test quality validation (Stage H.4)** → **block** and complete quality checklist before proceeding to Stage I.
- **Stage H test quality validation with 6+ violations or 2+ major violations** → **block** and refactor tests before proceeding to Stage I.
- Public **contracts** changed with no SPEC update → **block merge**.
- Material changes with no SPEC **version increment** → **block merge**.
- Non-trivial choices with no **ADR** → **block merge**.
- Feature work with no **FEATURE** file → **block merge**.
- **FEATURE missing discovery findings or reuse analysis** (for Medium/Large) → **block** and complete Stage B first.
- **FEATURE missing test impact analysis** (for Medium/Large) → **block** and add test update checklist from Stage B.
- Production-impacting changes with no **OP-NOTE** → **block deployment**.
- PR missing links (PRD/SPEC/ADR/FEATURE) → request changes.
- **PR without tests (unit + integration) for new code** → **block merge**.
- **Checkpoint skipping without approval** → **block and return to previous checkpoint**.
- **Non-compliant file formats** → **block and regenerate following rules**.