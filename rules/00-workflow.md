# Project Workflow — Single Source of Truth

## Purpose and Scope
- This is the **top governance rule**. All development activities must conform.
- **Docs-first mandate:** **Generate or update required docs _before_ generating code.** Code must **follow** the documented contracts, topology, framework roles, and SLOs.
- **Stage gating & human review:** At **each stage**, the assistant **generates the required file(s)** and **stops for human review/approval** before moving to the next stage.
- **Rule Compliance:** Each stage must follow its corresponding rule format and standards.


## Authoritative Paths & Naming
- **PRD** → `docs/prds/prd.md` (single PRD file per project; edit directly for all changes; maintain changelog within the file)
- **SPEC (TECH SPEC)** → `docs/specs/spec-<spec>.md` (no subdirs; `<spec>` in `{system, api, frontend, llm, ...}`; maintain `docs/specs/index.md`)
  - **Architecture section contains only:** (1) **comprehensive diagram** (frameworks + relationships) and (2) **component inventory table**.
  - Minor edits → update + **Changelog**; material contract/SLO/framework/topology change → **increment version** + Git tag (prior marked **Superseded**).
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
| **Medium** | Multi-component, no new services | B → C → D → E → F → G → H → I | New API endpoint using existing services |
| **Large** | System change, new contracts/services | Full A → K | New LLM integration, new auth system |

## Review Checkpoint Strategy

Instead of 11 individual stops, reviews are grouped into **6 strategic checkpoints**:

1. **Planning Complete** (after Stage C): PRD + Discovery + SPECs + ADRs reviewed together
2. **Design Complete** (after Stage E): FEATURE spec reviewed
3. **Tests Complete** (after Stage F): Failing tests reviewed
4. **Implementation Complete** (after Stage H): Working + refactored code reviewed
5. **Release Ready** (after Stage I): OP-NOTE reviewed
6. **Deployed** (after Stage K): Post-deployment verification

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
- **Action:** Search and analyze existing codebase **before** designing new solutions. Follow comprehensive discovery checklist:
  1. **Test Impact Analysis** (identify affected tests early)
     - Identify existing tests affected by the planned change
     - Mark tests to update/remove/keep (create test update checklist)
     - Map test coverage of code to be modified (coverage %, gaps)
     - Document test coverage gaps that need to be addressed
  2. **Dependency & Side Effect Mapping**
     - Trace all dependencies (imports, function calls, data flows)
     - Identify side effects (state changes, external calls, database operations)
     - Map impact on other components/features
     - Identify high-risk areas (high-impact + low-test-coverage)
  3. **Reusable Component Discovery**
     - **Search for similar features** using Grep, Glob, Read tools
     - **Identify reusable services/components** (e.g., patterns in `llm_services/`, `generation/services/`)
     - **Map existing architecture patterns** and layer assignments
     - **Check for duplicate implementations** that can be consolidated
- **Output (structured format):** Discovery findings with:
  - **Test update checklist** (tests to update/remove/add) with file paths
  - **Test coverage report** (coverage %, gaps, untested paths affected)
  - List of reusable components/services with file paths
  - **Dependency graph** (what depends on what, impact radius)
  - **Side effects inventory** (what changes where, state/DB/API impacts)
  - Architecture patterns to follow (reference: `docs/architecture/patterns.md`)
  - Code that should be refactored/consolidated
  - Layer assignment for new code (base/core/infrastructure/reliability)
  - **Risk areas** (high-impact + low-test-coverage zones)
- **Exit Gate:** Documented analysis with test impact checklist, dependency mapping, and confirmation that no duplicate functionality will be created.

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
  - Links to latest PRD and discovery findings; Changelog entry; version number.
  - **Spec update justification** (if creating new spec, explain why existing specs don't fit)
  - **Cross-spec impact summary** (which other specs are affected)
- **Rule Compliance:** Generated SPECs must follow `rules/02-tech_spec.md` format and standards.
- **Exit Gate:** For any change to **contracts/topology/framework roles/SLOs**, SPEC updated with new version and listed as **Current** in `docs/specs/index.md`. Spec update/create decision documented.

### Stage D — **Decide (ADRs)**
- **Action:** For any non-trivial choice (new dependency, auth model, storage pattern, schema versioning, SLO shifts), add **ADR**.
- **Output (generate file):** `docs/adrs/adr-<ID>-<slug>.md` for non-trivial choices (deps, storage, auth, versioning, SLO moves).
- **Rule Compliance:** Generated ADRs must follow `rules/03-adr.md` format and standards.
- **Exit Gate:** PR references ADR(s); code relying on the decision cannot merge without an **Accepted** ADR.
- **REVIEW CHECKPOINT #1:** **Planning Complete** (PRD + Discovery + SPECs + ADRs reviewed together)

### Stage E — **Plan (FEATURE)**
- **Action:** Create **FEATURE** spec `ft-<ID>-<slug>.md`; update `docs/features/schedule.md`.
- **Must include:** Acceptance criteria, design diffs (UI/API/schema), test & eval plan (goldens + thresholds for LLM paths), risks, **existing implementation analysis**, **architecture conformance**.
- **Output (generate file):** `docs/features/ft-<ID>-<slug>.md` (+ update `docs/features/schedule.md`) with:
  - Acceptance criteria; design diffs (UI/API/schema); test & eval plan; risks.
  - **Existing implementation analysis** (from Stage B discovery)
  - **Architecture conformance** (layer assignment, pattern compliance)
- **Rule Compliance:** Generated FEATURE must follow `rules/04-feature.md` format and standards.
- **Exit Gate (DoR):** FEATURE file present with all required sections + links to SPEC + discovery findings + reuse checklist complete.
- **REVIEW CHECKPOINT #2:** **Design Complete** (FEATURE spec reviewed)

### Stage F — **Write Unit Tests First (Hybrid TDD - RED Phase)**
- **Action:** Handle deprecated tests, then write **failing unit tests** for the feature/fix per acceptance criteria in FEATURE spec.
- **TDD Mandate:** Unit tests MUST be written **before** implementation code. See `rules/05-tdd.md` for detailed Hybrid TDD workflow.
- **Two Substeps:**
  1. **Test Cleanup** (using Stage B test update checklist):
     - Update deprecated tests to align with new feature design
     - Remove obsolete tests that are no longer relevant
     - Document why tests were removed/updated
  2. **Write New Failing Unit Tests:**
     - Use meaningful function names, descriptive assertions, and `NotImplementedError` with helpful messages
     - Focus on business logic with all external dependencies mocked
     - Tests should clarify requirements and design APIs
- **Test Coverage:** Unit tests for business logic with all external dependencies mocked. **Defer integration tests to Stage H.**
- **LLM Paths:** For LLM/prompt changes, create unit tests with mocked LLM responses (goldens + eval harness deferred to Stage H).
- **Output (generate files):**
  - Updated/cleaned up test files (deprecated tests handled)
  - New unit test files with failing tests that define expected behavior
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/05-tdd.md`.
- **Exit Gate:** All deprecated tests handled (updated/removed with justification) + new failing unit tests exist that fully specify the expected behavior.
- **REVIEW CHECKPOINT #3:** **Unit Tests Complete** (test cleanup + failing unit tests reviewed)

### Stage G — **Implement to Pass Unit Tests (Hybrid TDD - GREEN Phase)**
- **Action:** Write **minimal code** to make **unit tests** pass (TDD green phase).
- **Rules:** Do **not** change public contracts without SPEC/ADR updates already in place.
- **Docs-first enforcement:** If contracts change unexpectedly, **stop** and update SPEC/ADR first.
- **Reuse enforcement:** Leverage components identified in Stage B; avoid duplicating existing code.
- **Output:** Implementation code that makes all unit tests pass.
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/05-tdd.md`.
- **Exit Gate:** All unit tests green; no regressions; code follows established patterns from Stage B discovery. **Integration tests not required yet.**

### Stage H — **Write Integration Tests & Refactor (Hybrid TDD - REFACTOR Phase)**
- **Action:** Write integration tests for I/O boundaries, pass them, then refactor code while keeping all tests green.
- **Three Substeps:**
  1. **Write Integration Tests:** For API endpoints, database operations, external service calls, LLM pipelines, file I/O (see `rules/05-tdd.md` for mandatory list)
  2. **Pass Integration Tests:** Implement any missing integration code to make integration tests green
  3. **Refactor:** Clean up code while keeping all tests (unit + integration) green
- **Clean Code:** Remove duplication, improve naming, optimize algorithms, enhance error handling.
- **Documentation:** Add inline docs, update API docs if needed.
- **Pattern Compliance:** Verify code follows architecture patterns identified in Stage B.
- **Output:** Refactored code with all tests (unit + integration) still passing.
- **Rule Compliance:** Tests must follow Hybrid TDD practices in `rules/05-tdd.md`.
- **Exit Gate:** All tests (unit + integration) green; code meets quality standards; performance acceptable.
- **REVIEW CHECKPOINT #4:** **Implementation Complete** (working + refactored code with full test coverage reviewed)

### Stage I — **Release Preparation (OP-NOTE)**
- **Action:** Write **OP-NOTE** (per feature or release). Include preflight (migrations/env/flags), deploy steps, monitoring, playbooks, rollback, post-deploy checks.
- **Output (generate file):** `docs/op-notes/op-<ID>-<slug>.md` or `op-release-<semver>.md` with preflight, deploy steps, monitoring, playbooks, rollback, post-deploy checks.
- **Rule Compliance:** Generated OP-NOTE must follow `rules/06-op_note.md` format and standards.
- **Exit Gate:** OP-NOTE complete with all deployment steps documented.
- **REVIEW CHECKPOINT #5:** **Release Ready** (OP-NOTE reviewed)

### Stage J — **Deploy & Verify**
- **Action:** Follow OP-NOTE; canary if specified; run smoke tests; watch dashboards/alerts.
- **Exit Gate:** Post-deploy checks passed; toggle flags as per OP-NOTE; `docs/op-notes/index.md` updated.

### Stage K — **Close Loop**
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
→ If any tripwire is hit, **increment SPEC version** (e.g., v1.0.0 → v2.0.0), update changelog, update index, tag in Git, and reference ADRs.


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
- **Stage H without integration tests for I/O operations** → **block** and write integration tests first (see mandatory list in `rules/05-tdd.md`).
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