# TECH-SPEC — System/Component Engineering Plan

## Purpose and Scope
- Before building a new system/component or changing **interfaces, data flow, storage, frameworks, or SLOs**.
- Whenever a PR changes **contracts** (API/event/schema), **topology**, **framework roles** (e.g., Django, Redis, React), or **security posture**.

## Key Rules

### Path & Naming (mandatory)
- **Path:** `docs/specs/`
- **Filename pattern:** `spec-<spec>.md` (single living document per scope, no dates)
  - `<spec>` is a short slug describing the scope. Common values:
    - `system` (end-to-end overview)
    - `api` (backend: Django/DRF, DB, Redis, Celery)
    - `frontend` (React/Vite)
    - `llm` (models/prompts/evals)
    - others allowed (e.g., `data`, `infra`) when needed
- **Examples:**
  - `docs/specs/spec-system.md`
  - `docs/specs/spec-api.md`
  - `docs/specs/spec-frontend.md`
  - `docs/specs/spec-llm.md`

### Versioning policy (Git-based)
- **Use semantic versioning** in the file header: `v1.0.0`, `v2.0.0`, etc.
- **Minor editorial fixes:** update the current file + add to **Changelog** (no version bump).
- **Material changes** (contracts/SLOs/framework roles/topology):
  - **Increment version** (e.g., v1.3.0 → v2.0.0 for breaking changes)
  - Update **Changelog** with dated entry
  - **Tag in Git**: `git tag spec-api-v2.0.0`
  - Mark prior version as **Superseded** in changelog
- **Scope changes:** use a new `<spec>` slug (e.g., split `system` into `api`/`frontend`/`llm`).
- **Git provides history:** Use `git log`, `git blame`, `git diff` for change tracking.

### Required sections (must include)
- **Header** — version, file, status, FEATUREs (link its upstream artifacts), Contract Versions
- **Overview & Goals** (link Latest PRD)  
- **Architecture (Detailed)** — must meet *Architecture Requirements* below  
- **Interfaces & Data Contracts** (endpoints/events, schemas, error taxonomy, versioning)  
- **Data & Storage** (tables/indexes/migrations/retention)  
- **Reliability & SLIs/SLOs** (timeouts/retries/backpressure/limits)  
- **Security & Privacy** (authn/z, PII, secrets, logging)  
- **Evaluation Plan** (datasets, metrics, thresholds, test harness)  
- **Changelog** (dated bullets of changes)

### Architecture Requirements (be explicit)
- **Comprehensive diagram** that explicitly **names each framework** and shows their **relationships** (edges, protocols, sync/async if relevant) and **trust boundaries** (public/private).  
   *Call out frameworks like: Django/DRF, Redis, Celery, Postgres, React, Nginx/CDN, LLM provider, etc.*
- **Component inventory (table)** listing, for every box in the diagram: **framework/runtime**, purpose, **interfaces (in/out)**, direct dependencies, scale/HA notes, and owner.

## Example
``` md
# Tech Spec — api
**Version**: v2.1.0
**File:** docs/specs/spec-api.md
**Status:** Current
**PRD:** `prd.md` (v1.2)
**Contract Versions:** API v1.3  •  Schema v1.1  •  Prompt Set v1.4
**Git Tag:** `spec-api-v2.1.0`

## Overview & Goals
Serve article credibility scores with p95 ≤ 400ms on cache hit, ≥99.9% availability.
Links: PRD v1.2, Stage B discovery findings (reusing llm_services patterns)

## Architecture (Detailed)

### Topology (frameworks)
[Diagram showing Django DRF → Redis → Celery → LLM API flow]

### Component Inventory
| Component  | Framework/Runtime        | Purpose                           | Interfaces (in/out)                            | Depends On        | Scale/HA            | Owner |
|------------|--------------------------|-----------------------------------|------------------------------------------------|-------------------|---------------------|-------|
| Frontend   | React (Vite, TS)         | SPA UI                            | In: HTTPS via CDN; Out: `GET/POST /api/*`      | CDN/Ingress       | Edge cached         | FE    |
| API        | Django DRF (Gunicorn)    | REST endpoints, auth, policy      | In: `/api/v1/*`; Out: Redis, Postgres, Celery  | Redis, Postgres   | 3 replicas, HPA     | BE    |
| Cache/Broker| Redis 7                 | Low-latency cache + Celery broker | `GET/SETEX score:*`, Celery queues             | —                 | Primary+replica     | SRE   |
| Workers    | Celery (Python)          | Async scoring/enrichment          | In: queue; Out: LLM HTTP, Redis, Postgres      | Redis, LLM, DB    | Autoscale by depth  | BE    |
| DB         | Postgres 15              | Durable storage                   | SQL                                            | —                 | Primary + PITR      | SRE   |
| LLM API    | HTTP client (requests)   | External scoring                  | HTTPS to provider                              | Provider          | External            | BE    |

## Interfaces & Data Contracts
POST `/api/v1/score` body `{url|string, lang?}` → `ScoreV1` | 202 w/ `task_id`
Errors: 400 invalid, 422 unsupported, 429 throttled, 500 server.

## Data & Storage
Table `scores(id, url_hash, label, scores_json, created_at idx)`. Migration `20250822_add_scores.sql`.

## Reliability & SLOs
SLIs: availability, p95 latency; SLOs: 99.9% / 400ms. Circuit breaker on LLM ≥5% errors.

## Security & Privacy
No PII stored; redact URLs; keys via env; structured audit logs.

## Evaluation Plan
Goldens v0.4; F1 ≥ 0.72 gate in CI. Regression suite on PR.

## Changelog
- **2025-09-15 [v2.1.0]**: Added circuit breaker integration; improved retry logic
- **2025-09-01 [v2.0.0]**: Breaking: New schema with rationales array; API v1.3 (supersedes v1.x)
- **2025-08-22 [v1.0.0]**: Initial version; API v1.0; Redis TTL 24h; Celery retry policy

**Note:** For full version history, use `git log docs/specs/spec-api.md` or `git diff spec-api-v1.0.0..spec-api-v2.1.0`
```