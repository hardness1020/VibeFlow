# ADRs — Architectural Decision Records

## Purpose and Scope
- Whenever you introduce a new dependency, change an architecture pattern, alter API/DB schemas, security posture, or SLOs.
- Before implementing non-trivial changes; reference ADRs in PRs.

## Key Rules
- **Path:** `docs/adrs/`
- **Naming:** `adr-<ID>-<slug>.md` (lowercase, kebab-case slug; unique per decision)
- **Status lifecycle:** Draft → Accepted | Rejected
- **Content must include:** Header, Context, Decision, Consequences (±), Alternatives, Rollback Plan, Links (PRD/ADR/FEATURE references)
- **Discipline:** If a public API/contract changes without an ADR → block merge until ADR exists.

## Example
```md
# ADR: Choose Django DRF over FastAPI
**File:** docs/adrs/adr-001-backend-framework.md  
**Status:** Accepted  

## Context
Team prefers async, but we need admin tooling, auth, and browsable API quickly.

## Decision
Adopt **Django DRF** for unified auth/admin and stable ORM.

## Consequences
+ Faster CRUD/admin + RBAC; stable ecosystem  
− Slightly heavier; async requires DRF+ASGI config

## Alternatives
FastAPI (lighter, but re-implement admin/auth), Flask (+plugins)

## Rollback Plan
Keep service boundaries; if DRF blocks latency goals, rebase views to FastAPI gateway.

## Links
- PRD: `prd.md`
- TECH-SPECs: `spec-frontend.md`
- FEATUREs: `ft-001-hover-badge.md`, `ft-002-explain-tooltip.md`
```