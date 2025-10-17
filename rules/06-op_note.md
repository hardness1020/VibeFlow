# OP-NOTE — Operator Notes / Runbooks

## When to use
- At release time or when deployment/runtime behavior changes (flags, env vars, migrations, scaling, monitoring).

## Key Rules
- **Path:** `docs/op-notes/`
- **Naming (choose one):**  
  - Per feature: `op-<ID>-<slug>.md`  
  - Per release: `op-release-<semver>.md`
- **Index:** keep `docs/op-notes/index.md` linking latest notes.
- **Content must include:**
  - **Header:** file, date, FEATUREs
  - **Preflight:** prerequisites, approvals, migrations, feature flags, env vars (no secrets)  
  - **Deploy Steps:** ordered commands + verification checks  
  - **Monitoring:** dashboards, alerts, SLOs/SLIs  
  - **Runbook/Playbooks:** symptom → diagnose → remediate  
  - **Rollback:** precise steps; data compatibility notes  
  - **Post-Deploy Checks:** smoke tests, owners/on-call, timestamp
- **Gates:** No production deploy without an OP-NOTE covering the change.

## Example
```md
# OP-NOTE — release v1.3.0
**File:** docs/op-notes/op-note-release-1.3.0.md  
**Date:** 2025-08-22  
**Features:** `ft-001-hover-badge.md`, `ft-002-explain-tooltip.md`

## Preflight
- DB migration `20250822_add_scores.sql` applied in staging
- Set `LLM_MODEL=vX` in prod; ensure `feature.hover_badge=false`

## Deploy Steps
1) Build & push image `credibility:1.3.0`  
2) `kubectl set image scorer=credibility:1.3.0`  
3) Verify health: `/healthz` 200 within 60s

## Monitoring
Dashboards: latency p95, error rate; SLO 99.9%/400ms

## Runbook
Symptom: spike in 5xx  
Diagnose: check scorer pods logs; roll back model `vX→vW` if LLM errors

## Post-Deploy Checks
Run smoke `/v1/score` on 3 known URLs; confirm p95<400ms; set `feature.hover_badge=true` to 10% canary
```