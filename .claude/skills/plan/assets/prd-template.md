# PRD — [Project/Feature Name]

**Version:** v1.0.0
**File:** docs/prds/prd.md
**Owners:** PM ([Name]), Eng ([Name])
**Last_updated:** YYYY-MM-DD

## Summary

[3-5 lines describing: the problem, target users, and expected outcome]

## Problem & Context

[Describe the problem with evidence:]
- What evidence shows this is a problem? (KPIs, user feedback, metrics)
- What constraints exist? (technical, business, regulatory)
- What is the current state?

## Users & Use Cases

**Primary Users:**
- [User Type 1]: [Description and key jobs-to-be-done]
- [User Type 2]: [Description and key jobs-to-be-done]

**Key Use Cases:**
1. [Use case 1]
2. [Use case 2]

## Scope (MoSCoW)

**Must Have:**
- [Requirement 1]
- [Requirement 2]

**Should Have:**
- [Requirement 1]
- [Requirement 2]

**Could Have:**
- [Requirement 1]

**Won't Have (this version):**
- [Explicit exclusion 1]
- [Explicit exclusion 2]

## Success Metrics

**Primary Metrics:**
| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| [Metric 1] | [Current value] | [Target value] | [Date] |
| [Metric 2] | [Current value] | [Target value] | [Date] |

**Guardrail Metrics:**
- [Metric that must not regress]
- [SLO that must be maintained]

## Non-Goals

[Explicitly state what this PRD does NOT cover:]
- [Non-goal 1]
- [Non-goal 2]

## Requirements

### Functional Requirements

**User Stories:**
- As a [user], I can [action] so that [benefit]
- As a [user], I can [action] so that [benefit]

**Acceptance Criteria:**
- [Testable criterion 1]
- [Testable criterion 2]

### Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Latency | [e.g., p95 < 400ms] |
| Availability | [e.g., 99.9%] |
| Privacy | [e.g., No PII stored] |
| Security | [e.g., Auth required] |

## Dependencies

**Data Dependencies:**
- [Data source 1]

**Service Dependencies:**
- [Service 1]

**Legal/Policy:**
- [Any compliance requirements]

**Third-Party:**
- [External service 1]

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High | Medium | [Mitigation strategy] |
| [Risk 2] | Medium | Low | [Mitigation strategy] |

## Analytics & Telemetry

**Events to Track:**
- `event_name`: [Description, when fired]

**Dashboards:**
- [Dashboard 1]: [Purpose]

**Alerts:**
- [Alert condition 1]: [Threshold]

---

> **Note:** Implementation details (framework choices, specific technologies) belong in TECH-SPEC and ADRs, not in the PRD.
