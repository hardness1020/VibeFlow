# Discovery Document Guide

Complete codebase discovery before designing new solutions (Stage C).

**Required for:** Medium and Large changes
**Optional for:** Micro and Small changes

## Document Template

```markdown
# Discovery: <ID> - <Title>

**ID:** <ID>
**Type:** Feature | Fix | Chore
**Date:** YYYY-MM-DD
**Size Track:** Micro | Small | Medium | Large
**Author:** [Name]

## Summary

[1-2 paragraph summary of what was discovered]
```

## Phase 0: Spec Discovery (Mandatory First)

**Goal:** Understand existing architecture through specs BEFORE diving into code.

### Checklist

1. **List all existing specs** from `docs/specs/`
2. **Identify affected specs** — Which specs cover the area you're changing?
3. **Extract patterns to follow:**
   - Contracts (APIs, schemas, events)
   - Service layer structure
   - Configuration schemas
4. **Note spec metadata:**
   - Last verified date
   - Confidence level (HIGH/MEDIUM/LOW)

### Output Template

```markdown
## Phase 0: Spec Discovery Results

### Affected Specs
- **spec-[name].md** (v[X.Y.Z]) - [Scope description]

### Spec-Defined Patterns to Follow

**Contracts:**
- API endpoints: [list from spec]
- Data schemas: [list from spec]

**Service Layer:**
- Layer assignment: [where new code should go]
- Parent class: [if applicable]
- Pattern: [architecture pattern to follow]

### Spec Confidence Assessment
- **spec-[name].md**: [HIGH/MEDIUM/LOW] - [Notes]

### Spec Update Checklist (for Stage C)
- [ ] **spec-[name].md** → v[X.Y.Z]
  - Reason: [Why update needed]
  - Update: [What to change]
```

## Phase 1: Spec-Code Validation

**Goal:** Verify specs match actual code. Detect drift.

### Checklist

1. **Validate contracts** — Do API endpoints match spec?
2. **Validate schemas** — Do data models match spec?
3. **Validate interfaces** — Do service signatures match?
4. **Document discrepancies**

### Output Template

```markdown
## Phase 1: Spec-Code Validation Results

### Discrepancies Found
1. **spec-[name].md** (Line [X]): [Issue]
   - Impact: [MINOR/MEDIUM/MAJOR]
   - Action: [What to do]

### Spec Confidence Assessment (Post-Validation)
- **spec-[name].md**: [VERIFIED/HIGH/MEDIUM/LOW]
  - Status: [What was validated]
  - Recommendation: [How to proceed]

### Required Spec Updates (Before Stage C)
🔴 CRITICAL: [List critical updates]
🟡 HIGH: [List high priority]
🟢 MEDIUM: [List can defer]
```

## Phase 2: Test Impact Analysis

**Goal:** Identify tests affected by the change.

### Checklist

1. **Find affected test files**
2. **Categorize each test:** KEEP / UPDATE / REMOVE / ADD
3. **Map test coverage** — What's the current coverage?
4. **Identify coverage gaps**

### Output Template

```markdown
## Phase 2: Test Impact Analysis

### Affected Test Files

**Direct Impact:**
- `[path/to/test_file.py]` ([N] tests) - Reason

**Indirect Impact:**
- `[path/to/test_file.py]` ([N] tests) - Reason

### Test Update Checklist

**[path/to/test_file.py]:**
- ✅ KEEP: `test_[name]` (still valid)
- 🔄 UPDATE: `test_[name]` ([reason])
- ❌ REMOVE: `test_[name]` ([reason])
- ➕ ADD: `test_[name]` ([purpose])

**Summary:**
- Keep: [N] tests
- Update: [N] tests
- Remove: [N] tests
- Add: [N] new tests

### Test Coverage Report

| Module | Current Coverage | Gaps |
|--------|-----------------|------|
| [module] | [X]% | [Lines] |

### Coverage Gaps to Address
1. [Gap description] - [Priority]
```

## Phase 3: Dependency & Side Effect Mapping

**Goal:** Understand impact radius.

### Checklist

1. **Trace inbound dependencies** — What depends on this code?
2. **Trace outbound dependencies** — What does this code depend on?
3. **Identify side effects:**
   - Database operations
   - External API calls
   - Cache operations
   - Message queue
   - Metrics/logging
4. **Map impact radius** — Diagram of affected components

### Output Template

```markdown
## Phase 3: Dependency & Side Effect Mapping

### Dependency Map

**Inbound (depends on this):**
- `[file]` - [How it uses this code]

**Outbound (this depends on):**
- `[file/service]` - [How this code uses it]

### Side Effects Inventory

**Database:**
- Creates: [Table/records]
- Updates: [Fields]
- Reads: [Queries]

**External APIs:**
- [API name]: [Operations, cost, latency]

**Cache:**
- [Operations, TTL]

**Message Queue:**
- [Tasks, queues]

### Impact Radius
[ASCII diagram or list of affected components by layer]

### High-Risk Areas
| Component | Impact | Coverage | Risk |
|-----------|--------|----------|------|
| [name] | HIGH | [X]% | 🔴 |
```

## Phase 4: Reusable Component Discovery

**Goal:** Find existing code to reuse. Prevent duplication.

### Checklist

1. **Search for similar features**
2. **Identify reusable services/patterns**
3. **Map architecture patterns to follow**
4. **Check for duplicate implementations**

### Output Template

```markdown
## Phase 4: Reusable Component Discovery

### Similar Feature Search Results
1. `[path/to/file]`
   - Pattern: [What pattern it uses]
   - Reusable: [What can be reused]

### Reusable Component Inventory

| Component | Location | Provides | Usage |
|-----------|----------|----------|-------|
| [Name] | [Path] | [Features] | [How to use] |

### Architecture Patterns to Follow
1. **[Pattern Name]**
   - Source: [Reference location]
   - Apply to: [How to apply]

### Duplicate Implementation Check
✅ NO DUPLICATES FOUND / ⚠️ POTENTIAL DUPLICATE: [Details]
```

## Risk Assessment

```markdown
## Risk Assessment & Recommendations

### Overall Risk Level
**Risk Level:** 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

**Justification:**
- Positive factors: [List]
- Risk factors: [List]

### Key Risks
1. **[Risk name]**
   - Impact: [Severity]
   - Probability: [Likelihood]
   - Mitigation: [Strategy]

### Go/No-Go Recommendation
✅ **GO** - Proceed to Stage C

**Conditions:**
- [Condition 1]
- [Condition 2]
```

## Post-Implementation Notes

Added in Stage I after implementation:

```markdown
## Post-Implementation Notes

### What Actually Happened
- [Deviations from plan]

### Lessons Learned
- What went well: [List]
- Challenges: [List]
- For future: [Recommendations]

### Discovery Accuracy
- ✅ Accurate: [Predictions that matched]
- ❌ Missed: [What discovery missed]
```
