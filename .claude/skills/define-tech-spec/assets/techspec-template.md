# Tech Spec — [spec-name]

**Version:** v1.0.0
**File:** docs/specs/spec-[name].md
**Status:** Current
**PRD:** `prd.md` (vX.Y)
**Contract Versions:** API vX.Y • Schema vX.Y
**Git Tag:** `spec-[name]-v1.0.0`

## Table of Contents

[Required if spec > 800 lines]

- [Overview & Goals](#overview--goals)
- [Architecture](#architecture)
- [Interfaces & Data Contracts](#interfaces--data-contracts)
- [Data & Storage](#data--storage)
- [Reliability & SLIs/SLOs](#reliability--slisslos)
- [Security & Privacy](#security--privacy)
- [Evaluation Plan](#evaluation-plan)

## Overview & Goals

[What are we building and why? Link to PRD and discovery findings.]

**Goals:**
- [Goal 1]
- [Goal 2]

**Links:**
- PRD: [Link to PRD with version]
- Discovery: [Link to discovery document if applicable]

## Architecture

### Topology (Frameworks)

[Diagram showing components, frameworks, and protocols]

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │     Backend     │
│   React/Vite    │────▶│   Django DRF    │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │  Redis   │ │ Postgres │ │  Celery  │
             └──────────┘ └──────────┘ └──────────┘
```

### Component Inventory

| Component | Framework/Runtime | Purpose | Interfaces | Depends On | Scale/HA | Owner |
|-----------|------------------|---------|------------|------------|----------|-------|
| [Name] | [Framework] | [Purpose] | In: [X]; Out: [Y] | [Dependencies] | [Scale info] | [Team] |

## Interfaces & Data Contracts

### API Endpoints

```
POST /api/v1/[endpoint]
  Request:  { field: type }
  Response: { field: type } | 202 { task_id }
  Errors:   400 invalid, 422 unprocessable, 429 throttled, 500 server
```

### Service Interfaces

```python
class ServiceName:
    """[Purpose description]"""

    def method_name(
        self,
        param: ParamType,
    ) -> ReturnType:
        """[Brief description]"""
        # NO IMPLEMENTATION - interface signature only
```

### Data Schemas

```python
@dataclass
class EntityName:
    field1: str
    field2: int
    field3: Optional[str] = None
```

### Error Taxonomy

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | [Description] |
| `NOT_FOUND` | 404 | [Description] |
| `RATE_LIMITED` | 429 | [Description] |

## Data & Storage

### Database Tables

```sql
CREATE TABLE [table_name] (
    id SERIAL PRIMARY KEY,
    [field] [TYPE] [CONSTRAINTS],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_[name] ON [table]([column]);
```

### Migrations

| Migration | Description | Rollback |
|-----------|-------------|----------|
| [YYYYMMDD]_[name].sql | [Description] | [Rollback notes] |

### Data Retention

| Data Type | Retention Period | Cleanup Strategy |
|-----------|-----------------|------------------|
| [Type] | [Period] | [Strategy] |

## Reliability & SLIs/SLOs

### SLIs (Service Level Indicators)

- **Availability:** Percentage of successful requests
- **Latency:** p50, p95, p99 response times
- **Error Rate:** Percentage of 5xx responses

### SLOs (Service Level Objectives)

| SLI | Target | Measurement Window |
|-----|--------|-------------------|
| Availability | 99.9% | 30 days |
| Latency (p95) | < 400ms | 5 minutes |
| Error Rate | < 0.5% | 1 hour |

### Fault Tolerance

**Circuit Breaker:**
- Failure threshold: [N] consecutive failures
- Recovery timeout: [N] seconds
- States: CLOSED → OPEN → HALF_OPEN → CLOSED

**Retry Strategy:**
- Max retries: [N]
- Backoff: exponential ([base]s, [max]s)

**Timeouts:**
- [Operation]: [timeout]

## Security & Privacy

### Authentication/Authorization

- [Auth mechanism]
- [Permission model]

### Data Privacy

| Data Type | Classification | Handling |
|-----------|---------------|----------|
| [Type] | PII/Sensitive/Public | [Rules] |

### Secrets Management

- [How secrets are managed]
- [No secrets in code/docs]

### Audit Logging

- [What is logged]
- [Retention policy]

## Evaluation Plan

### Test Strategy

| Test Type | Scope | Coverage Target |
|-----------|-------|-----------------|
| Unit | [Scope] | [X]% |
| Integration | [Scope] | Critical paths |
| E2E | [Scope] | Key flows |

### Performance Benchmarks

| Operation | Target | Measurement |
|-----------|--------|-------------|
| [Operation] | [Target] | [How measured] |

### Quality Gates

- [Gate 1]: [Threshold]
- [Gate 2]: [Threshold]

---

## References

### Related Specs
- [Other relevant specs]

### Related ADRs
- [ADRs that inform this spec]

### External Documentation
- [Links to external docs]

---

> **Code Detail Guidance:**
> - ✅ Interface signatures (no implementation)
> - ✅ Data schemas and contracts
> - ✅ Configuration tables (summary form)
> - ❌ Full implementations (→ Feature Spec)
> - ❌ Prompt templates (→ Feature Spec)
> - ❌ Algorithms with logic (→ Feature Spec)
