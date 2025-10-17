# Project Requirement Files Authoring Rule

## Purpose and Scope
- Create/update a PRD **before** major work begins or when business goals/scope change.
- Use PRDs to define **problem, users, scope, success metrics, risks, and timeline**—not implementation details.

## Key Rules

### Path & Naming (mandatory)
- **Path:** `docs/prds/`
- **Naming:** `prd.md` (single PRD file per project)
  - **Edit the existing PRD** file directly; maintain only one PRD file per project.

### Versioning policy
- **All changes:** update the current file + add to **Changelog** section.
- **Major updates:** increment version number in header and document changes in changelog.

### Content Requirements (must include)
- **Header** — version, file, owners, last_updated
- **Summary** — 3–5 lines: problem, target users, outcome.
- **Problem & Context** — evidence, KPIs affected, constraints.
- **Users & Use Cases** — personas, key jobs-to-be-done.
- **Scope (MoSCoW)** — Must/Should/Could/Won't; crisp, testable statements.
- **Success Metrics** — baseline → target; primary & guardrail metrics.
- **Non-Goals** — what this PRD explicitly excludes.
- **Requirements** — functional (user stories/acceptance), non-functional (latency, availability, privacy).
- **Dependencies** — data, services, legal/policy, 3rd-party.
- **Risks & Mitigations** — top risks, detection, fallback.
- **Analytics & Telemetry** — events, dashboards, alert thresholds.
- **Changelog**

> **Guardrail:** Implementation choices (e.g., Django vs FastAPI) belong in TECH-SPEC/ADRs, not PRD.


## Example
```md
# PRD — Article Credibility Score
**Version:** v1.0.0
**File:** docs/prds/prd.md  
**Owners:** PM (A. Lee), Eng (M. Chang)  
**Last_updated:** 2025-08-22  

## Summary
Help readers quickly judge an article's credibility with a G/Y/R badge and short rationale, targeting p95 ≤ 400ms and ≥10% reduction in bounce on news pages.

## Problem & Context
Users struggle to assess quality; high bounce and low trust. Current tools are slow and opaque.

## Users & Use Cases
- News readers: want a fast, explainable signal
- Researchers: want consistent scoring across sources

## Scope (MoSCoW)
**Must:** Badge + rationale (≤3), EN/ZH support, cache, rate-limits  
**Should:** Evidence links, accessibility (WCAG AA)  
**Could:** User feedback thumbs, export JSON  
**Won't:** Source reputation scoring (future PRD)

## Success Metrics
Primary: CTR on "Explain" +2pp (baseline 6% → 8% by 2025-09-15)  
Guardrails: p95 API latency ≤400ms; 5xx ≤0.5%; false-positive rate ≤8% on goldens v0.4

## Non-Goals
No browser extension v1; no multilingual beyond EN/ZH.

## Requirements
### Functional
- As a reader, I see a badge within 200ms on cache hit with up to 3 rationales.
- If scoring is unavailable, I see a neutral "Check Article" state.
### Non-Functional
- Availability ≥99.9%; PII: none stored; data retention 30 days for logs.

## Dependencies
Model access via provider X; content extraction service; privacy review.

## Risks & Mitigations
LLM drift → nightly evals & alerts; scraping failures → fallback to paste-text UI.

## Analytics & Telemetry
Events: view_badge, open_explain, error_score; dashboards for latency, errors, eval F1.

## Changelog
```