# ADR: [Decision Title]

**File:** docs/adrs/adr-[ID]-[slug].md
**Status:** Draft | Accepted | Rejected | Superseded
**Date:** YYYY-MM-DD
**Decision Makers:** [Names]

## Context

[Describe the situation that requires a decision:]

- What is the technical/business context?
- What problem are we trying to solve?
- What constraints exist?
- What prompted this decision now?

## Decision

[State the decision clearly:]

We will adopt **[solution/approach]** because [primary reason].

[Elaborate on the decision:]
- Key aspects of the solution
- How it will be implemented at a high level
- Any important details or constraints

## Consequences

### Positive

+ [Benefit 1]
+ [Benefit 2]
+ [Benefit 3]

### Negative

− [Tradeoff/cost 1]
− [Tradeoff/cost 2]

### Neutral

* [Observation that is neither positive nor negative]

## Alternatives Considered

### Alternative 1: [Name]

**Description:** [Brief description]

**Pros:**
- [Pro 1]

**Cons:**
- [Con 1]

**Why not chosen:** [Reason]

### Alternative 2: [Name]

**Description:** [Brief description]

**Pros:**
- [Pro 1]

**Cons:**
- [Con 1]

**Why not chosen:** [Reason]

## Rollback Plan

[Describe how to reverse this decision if needed:]

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Estimated rollback effort:** [Low/Medium/High]
**Data considerations:** [Any data migration/compatibility notes]

## Links

**PRD:** [Link to PRD]
**TECH-SPECs:** [Links to affected specs]
**FEATUREs:** [Links to related features]
**Related ADRs:** [Links to related decisions]

---

## ADR Status Lifecycle

```
Draft → Accepted | Rejected
         ↓
    Superseded (by ADR-XXX)
```

**Status Definitions:**
- **Draft:** Under discussion, not yet decided
- **Accepted:** Decision made, implementation can proceed
- **Rejected:** Decision considered but not adopted
- **Superseded:** Replaced by a newer decision (link to replacement)

---

## When to Create an ADR

Create an ADR for:
- New external dependencies (libraries, services)
- Architecture pattern changes
- Storage pattern changes
- Authentication/authorization changes
- API versioning decisions
- SLO changes
- Security posture changes
- Any non-trivial choice that affects contracts

Do NOT create an ADR for:
- Implementation details within established patterns
- Bug fixes
- Routine refactoring
- Documentation updates
