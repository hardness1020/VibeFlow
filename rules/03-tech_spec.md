# TECH-SPEC — System/Component Engineering Plan

## Purpose and Scope
- Before building a new system/component or changing **interfaces, data flow, storage, frameworks, or SLOs**.
- Whenever a PR changes **contracts** (API/event/schema), **topology**, **framework roles** (e.g., Django, Redis, React), or **security posture**.

## Table of Contents
- [Purpose and Scope](#purpose-and-scope)
- [Quick Reference](#quick-reference)
- [Pre-Creation Workflow](#pre-creation-workflow)
- [Key Rules](#key-rules)
  - [Path & Naming](#path--naming-mandatory)
  - [Versioning Policy](#versioning-policy-git-based)
  - [Spec Lifecycle States](#spec-lifecycle-states)
- [Required Sections](#required-sections-must-include)
- [Required Section Order](#required-section-order-recommended-sequence)
- [Architecture Requirements](#architecture-requirements-be-explicit)
- [Code Detail Level](#code-detail-level-what-not-to-include)
  - [Common Violations](#common-violations-real-examples)
  - [Tech Spec vs Feature Spec Decision Guide](#tech-spec-vs-feature-spec-decision-guide)
  - [Code Detail Decision Tree](#code-detail-decision-tree)
  - [Section Size Guidelines](#section-size-guidelines)
  - [Section Size Red Flags](#section-size-red-flags)
- [Table of Contents Requirement](#table-of-contents-requirement)
- [Example](#example)
- [References Section](#references-section-optional-but-recommended)
- [Reference Strategy](#reference-strategy---single-source-of-truth)
- [Quality & Submission Checklist](#quality--submission-checklist)
  - [Cross-Spec Consistency](#1-cross-spec-consistency)
  - [Size Validation](#2-size-validation)
  - [Required Elements](#3-required-elements)
  - [Git Compliance](#4-git-compliance)
- [Minimal Spec Template](#quick-reference-minimal-spec-template)

## Quick Reference

**Common tasks (quick links):**
- **[Pre-creation checklist](#pre-creation-workflow-mandatory)** - Decide whether to update existing spec or create new one
- **[Required sections](#required-sections-must-include)** - What must be included in every spec
- **[Example spec](#example)** - See complete reference example with all sections
- **[Minimal template](#quick-reference-minimal-spec-template)** - Copy-paste starting point for new specs
- **[Architecture requirements](#architecture-requirements-be-explicit)** - Topology diagrams and component inventory
- **[Code detail guidelines](#code-detail-level-what-not-to-include)** - What belongs in tech specs vs. feature specs

## Pre-Creation Workflow

**Before creating OR updating a spec, follow this checklist:**

1. **List existing specs** from `docs/specs/` directory
2. **For each existing spec**, check if your change affects:
   - Contracts (API/schema/events)
   - Topology (components/protocols)
   - Framework roles (Django/React/Redis)
   - SLOs (latency/availability targets)
3. **Decision matrix:**
   - ✅ **Update existing spec** if change fits within existing scope
   - ✅ **Create new spec** only if:
     - Scope doesn't fit any existing spec (e.g., new infrastructure layer)
     - Existing spec would become >1500 lines with addition
     - Change represents new architectural boundary (e.g., splitting monolith)
4. **Document justification** in spec header

**Anti-patterns to avoid:**
- ❌ Creating `spec-bullet-generation.md` when bullets already covered in `spec-llm.md`
- ❌ Creating `spec-database.md` when database already documented in `spec-api.md`
- ✅ GOOD: Extract `spec-database-schema.md` when database section grows to >150 lines

**Default assumption:** Update existing spec FIRST. Only create new spec when justified by criteria above.

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
- **Minor editorial fixes:** update the current file (no version bump).
- **Material changes** (contracts/SLOs/framework roles/topology):
  - **Increment version** (e.g., v1.3.0 → v2.0.0 for breaking changes)
  - **Tag in Git**: `git tag spec-api-v2.0.0`
- **Scope changes:** use a new `<spec>` slug (e.g., split `system` into `api`/`frontend`/`llm`).
- **Git provides history:** Use `git log`, `git blame`, `git diff` for change tracking.

### Spec Lifecycle States

**State transitions:**
```
Draft → Current → Superseded → Archived
```

**State definitions:**

| State | Meaning | Status Marker | Git Tag | When to Use |
|-------|---------|--------------|---------|-------------|
| **Draft** | Work in progress | `[DRAFT]` in header | No tag | Initial creation, not yet reviewed |
| **Current** | Active and authoritative | `Current` in header | Tagged | Accepted and in production |
| **Superseded** | Replaced by newer version | `⚠️ Superseded by vX.Y.Z` | Keep old tag | Breaking change created new version |
| **Archived** | No longer relevant | `❌ Archived (reason)` | Keep all tags | Component removed, architecture changed |

**Retirement criteria:**

Retire a spec when:
1. **Architecture removed:** Component/service no longer exists (e.g., removed embeddings → archive old spec)
2. **Scope merged:** Multiple specs consolidated into one (e.g., split specs merged into `spec-system.md`)
3. **Replaced by new approach:** ADR documents decision to supersede (e.g., ADR-028: keyword ranking replaces semantic search)

**Retirement process:**
1. Update spec header with archived status and reason
2. Keep file in repo for historical reference (do not delete)
3. Link to successor spec or ADR explaining replacement

**Example (archived spec header):**
```markdown
**Status:** ❌ ARCHIVED - Superseded by spec-llm.md v3.3.0 (ADR-028: removed embeddings)
**Archived Date:** 2025-10-16
**Reason:** Embedding-based ranking removed in favor of keyword-based approach
**Successor:** See `spec-llm.md` v3.3.0+ for current artifact ranking architecture
```

### Required sections (must include)
- **Header** — version, file, status, FEATUREs (link its upstream artifacts), Contract Versions
- **Overview & Goals** (link Latest PRD)
- **Architecture (Detailed)** — must meet *Architecture Requirements* below
- **Interfaces & Data Contracts** (endpoints/events, schemas, error taxonomy, versioning)
- **Data & Storage** (tables/indexes/migrations/retention)
- **Reliability & SLIs/SLOs** (timeouts/retries/backpressure/limits)
- **Security & Privacy** (authn/z, PII, secrets, logging)
- **Evaluation Plan** (datasets, metrics, thresholds, test harness)

### Required section order (recommended sequence)

**Mandatory sections** (must appear in this order):
1. **Header** - Version, status, contracts, tags
2. **Table of Contents** (if spec >800 lines)
3. **Overview & Goals** - What and why
4. **Architecture** - How it's structured

**Flexible middle sections** (order by domain logic):

**Backend/API specs (spec-api.md pattern):**
- Interfaces & Data Contracts → Data & Storage → Security → Reliability → Evaluation

**Frontend specs (spec-frontend.md pattern):**
- Authentication Integration → User Interface → Performance → Security

**LLM specs (spec-llm.md pattern):**
- Service Layer → Model Configuration → Anti-Hallucination → Reliability

**General guideline:** Order sections from high-level (what/why) to detailed (how/when).

**Rationale:** This order presents information logically, matching typical reader questions. Each section builds on previous context: understanding the purpose enables comprehending the architecture, which enables using the interfaces, etc.

**Anti-patterns:**
- ❌ Implementation details before interfaces (show contract first)
- ❌ Security after Evaluation (cross-cutting concerns should group together)

### Architecture Requirements (be explicit)

**Two mandatory deliverables:**

1. **Topology Diagram** - Shows frameworks, protocols, and relationships
   - **Format:** Mermaid, ASCII art, or visual diagram
   - **Must include:** Framework names (Django/Redis/React), protocols (HTTP/REST/WebSocket), trust boundaries
   - **Example formats:**
     - ASCII topology (spec-api.md): Shows API Gateway → Django → Redis → Celery flow
     - Mermaid dependency graph (spec-llm.md): Shows service dependencies with arrows

2. **Component Inventory Table** - Lists all components with metadata
   - **Required columns:** Component, Framework/Runtime, Purpose, Interfaces, Dependencies, Scale/HA, Owner
   - **See:** spec-api.md for reference format

**Optional but recommended:**
- **ERD (Entity Relationship Diagram):** Required if spec defines >5 database tables
  - Extract to `spec-database-schema.md` if ERD >50 lines
- **Service Dependency Graph:** Useful for service-oriented architectures (see spec-llm.md)
- **Sequence Diagrams:** For complex multi-step workflows

### Code Detail Level (what NOT to include)

**PROHIBITED in TECH SPECs** (move to FEATURE specs instead):
- ❌ **Full service/class implementations** with method bodies containing business logic
- ❌ **Business logic implementations** (use pseudocode, sequence diagrams, or high-level descriptions instead)
- ❌ **Validation logic implementations** (keep validation criteria lists/tables only)
- ❌ **Frontend component implementations** (React components, hooks with full implementations)
- ❌ **State management implementations** (Redux reducers, Zustand stores with logic)
- ❌ **CSS/styling code** (keep design system references only)
- ❌ **Detailed algorithms** with step-by-step code (use algorithmic descriptions or pseudocode)
- ❌ **Retry logic, circuit breaker implementations** (describe patterns, don't implement)
- ❌ **Code comments/docstrings** explaining "how" implementation works
- ❌ **Exhaustive field-level ERD documentation** (keep entity relationships only, not all field details)

**ALLOWED in TECH SPECs** (contracts and architecture only):
- ✅ **Interface signatures** (method/function names, parameters, return types — NO BODIES)
- ✅ **Data schemas** (dataclass/TypeScript type field definitions, JSON schemas)
- ✅ **API contracts** (HTTP endpoint paths, methods, request/response formats in HTTP notation)
- ✅ **Database schemas** (SQL DDL for tables, indexes, foreign keys)
- ✅ **Configuration tables** (model configs, strategy enums, feature flags)
- ✅ **Architecture diagrams** (component diagrams, sequence diagrams, data flow diagrams)
- ✅ **Entity relationship diagrams** (show table relationships and key fields, not exhaustive field documentation)
- ✅ **Error taxonomy** (error codes, error messages, HTTP status codes)
- ✅ **SLI/SLO thresholds** (latency targets, availability targets, rate limits)

**Example - Interface Signature (ALLOWED):**
```python
class ArtifactRankingService:
    """Ranks artifacts by relevance to job posting."""

    def rank_artifacts(
        self,
        artifacts: List[Artifact],
        job_posting: JobPosting
    ) -> List[RankedArtifact]:
        """Returns artifacts ranked by keyword overlap score."""
        # NO IMPLEMENTATION CODE HERE - this goes in feature specs
```

**Example - Full Implementation (PROHIBITED):**
```python
# ❌ DON'T include this in TECH SPEC
class ArtifactRankingService:
    def rank_artifacts(self, artifacts, job_posting):
        scores = []
        job_keywords = self._extract_keywords(job_posting.description)
        for artifact in artifacts:
            artifact_keywords = self._extract_keywords(artifact.content)
            overlap = len(job_keywords & artifact_keywords)
            score = overlap / len(job_keywords) if job_keywords else 0
            scores.append((artifact, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)
```

### Common Violations (Real Examples)

Based on actual spec cleanup (spec-llm.md v4.2.0), here are common violations to avoid:

#### ❌ VIOLATION: Full Configuration Dictionaries

```python
# DON'T: 45-line configuration dict with all parameters
DOCUMENT_STRATEGIES = {
    'resume': {
        'max_chunks': 50,
        'max_chars': 50_000,
        'sampling': 'full',
        'summary_tokens': 1_000,
        'chunk_selection': 'sequential',
        'map_reduce': False
    },
    # ... 4 more document types with full configs
}
```

**DO INSTEAD:** Condensed table + code reference
```markdown
| Category | Max Chars | Sampling | Tokens | Map/Reduce |
|----------|-----------|----------|--------|------------|
| Resume | 50K | full | 1K | No |
| Certificate | 10K | full | 500 | No |

**Source:** See `backend/.../pdf_document_classifier.py` for complete configuration.
```

#### ❌ VIOLATION: Full Prompt Templates

```python
# DON'T: 60-line prompt template with complete text
EXTRACTION_PROMPT = """Analyze this document...
{full_text}

CRITICAL RULES:
1. Extract ONLY...
2. Do NOT infer...
[...50 more lines of detailed instructions and examples...]
"""
```

**DO INSTEAD:** Prompt structure only
```python
# Input: {full_text}
# Output: JSON with {summary, technologies, achievements}
# Rules: Extract only explicit info, include source quotes, confidence scores
# See: feature spec ft-030 for complete template
```

#### ❌ VIOLATION: Reliability Pattern Implementations

```python
# DON'T: Full circuit breaker implementation
class LLMCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        # ... state variables ...

    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            # ... 20 lines of state management logic ...
```

**DO INSTEAD:** Pattern description
```markdown
**Circuit Breaker Pattern:**
- Failure threshold: 5 consecutive failures → OPEN state
- Timeout: 60s recovery window
- States: CLOSED → OPEN → HALF_OPEN → CLOSED
- See: `backend/llm_services/services/reliability/circuit_breaker.py`
```

#### ❌ VIOLATION: Cost Optimization Lists

```markdown
# DON'T: Operational guidance in tech spec
**Cost Optimization Strategies:**
1. Use caching for repeated artifact analysis
2. Tier by task criticality: extraction uses gpt-5, generation uses gpt-5-mini
3. Monitor reasoning token ratio
[...7 detailed optimization techniques...]
```

**DO INSTEAD:** Keep only architectural thresholds
```markdown
**Monitoring Thresholds:**
- Per artifact processing: $1.00 maximum
- Per CV generation: $0.50 target
- Daily budget: $50 (assuming ~200 generations/day)
```

#### ❌ VIOLATION: Scattered Related Content

**DON'T:** Spread related content across multiple top-level sections

```markdown
## Architecture
[Service overview only]

## PDF Document Classification
[PDFDocumentClassifier interface - 30 lines]

## Anti-Hallucination Architecture
[BulletVerificationService interface - 60 lines]

## Model Registry Configuration
[EvidenceContentExtractor interface - 35 lines]
```

**DO INSTEAD:** Group related content under single section

```markdown
## Architecture

### Service Layer

#### Core Services
- **TailoredContentService**: Job-tailored application generation
- **BulletVerificationService**: Post-generation fact-checking
- **EvidenceContentExtractor**: LLM-based content extraction with source attribution
- **PDFDocumentClassifier**: Document type classification for adaptive processing

[All service interfaces co-located here]

#### Infrastructure Services
- **ModelSelector**: Intelligent model selection with fallback
- **DocumentLoaderService**: Multi-format content extraction
- **CircuitBreaker**: Fault tolerance for external API calls
```

**Rationale:** Readers expect related content to be co-located. Scattered service interfaces force navigation across the document to understand the service architecture. Co-location enables comparison and understanding of relationships.

#### ❌ VIOLATION: Duplicated Performance/Cost Sections

**DON'T:** Repeat performance/cost analysis across multiple sections

```markdown
## PDF Document Classification
### Performance Impact
[PDF processing latency and token costs]

## Anti-Hallucination Architecture
### Performance Impact
[Verification latency and costs]

## Model Registry Configuration
### Performance & Cost Impact
[GPT-5 reasoning mode costs]

## Cost Considerations
[Overall cost estimates and budgets]
```

**DO INSTEAD:** Consolidate into single location

```markdown
## Reliability & SLIs/SLOs

### Performance Characteristics

| Component | Latency (P95) | Cost per Operation | SLO Impact |
|-----------|---------------|-------------------|------------|
| PDF Processing | 5-10s | $0.02 | +10s to extraction |
| Verification | 2-3s | $0.015 | +3s to generation |
| GPT-5 Reasoning (high) | +4-5s | +300% cost | Accuracy-critical only |

**Pipeline Totals:**
- End-to-end generation: 18-23s (within 30s SLO)
- Cost per CV: $0.50 target (3 artifacts + generation + verification)

**Monitoring Thresholds:**
- Per artifact: $1.00 maximum
- Daily budget: $50 (200 CV generations/day)
```

**Alternative:** If performance/cost analysis is large (>50 lines), create dedicated "Performance & Cost Analysis" section after Reliability.

**Rationale:** Duplicated performance data creates maintenance burden (must update multiple locations) and makes it hard to understand overall system performance. Single consolidated view enables holistic analysis.

### Tech Spec vs Feature Spec Decision Guide

| Content Type | Tech Spec | Feature Spec |
|--------------|-----------|--------------|
| Interface signatures (no bodies) | ✅ | ✅ |
| Complete function implementations | ❌ | ✅ |
| Configuration tables (condensed summary) | ✅ | ✅ (detailed) |
| Prompt templates (structure only, <20 lines) | ✅ | ✅ (full template) |
| Algorithms with step-by-step logic | ❌ | ✅ |
| Data schemas (dataclass/type definitions) | ✅ | ✅ |
| Cost optimization strategies | ❌ | ✅ |
| Processing heuristics and rules | ❌ (high-level only) | ✅ |
| Reliability patterns (description) | ✅ | ✅ (implementation) |
| Architecture diagrams | ✅ | ✅ |
| Migration guides (operational) | ❌ | ✅ |

**Rule of Thumb:** If it shows "how" something works, it belongs in a feature spec. If it defines "what" the interface/contract is, it belongs in a tech spec.

### Code Detail Decision Tree

Use this flowchart to decide if code belongs in TECH SPEC vs FEATURE spec:

```
┌─────────────────────────────────────────┐
│ Does this show HOW implementation works?│
└──────────────┬──────────────────────────┘
               │
         ┌─────▼─────┐
         │    YES    │
         └─────┬─────┘
               │
    ┌──────────▼──────────────┐
    │ Move to FEATURE spec    │
    │ (ft-XXX-slug.md)        │
    └─────────────────────────┘

         ┌─────▼─────┐
         │    NO     │
         └─────┬─────┘
               │
    ┌──────────▼────────────────────┐
    │ Does it define WHAT interface │
    │ contract is (signature only)? │
    └──────────┬────────────────────┘
               │
         ┌─────▼─────┐
         │    YES    │
         └─────┬─────┘
               │
    ┌──────────▼──────────────┐
    │ Keep in TECH SPEC       │
    │ (interface signature)   │
    └─────────────────────────┘
```

**Examples:**

| Code Sample | Tech Spec? | Reason |
|-------------|-----------|---------|
| `def rank_artifacts(artifacts, job) -> List[RankedArtifact]:` | ✅ YES | Interface signature only |
| `def rank_artifacts(...): scores = []; for a in artifacts: ...` | ❌ NO | Shows implementation logic |
| `{url: string, evidence_type: "github" \| "document"}` | ✅ YES | Data schema/contract |
| `const rankings = artifacts.map(a => calcScore(a, job))` | ❌ NO | Business logic implementation |
| `POST /api/v1/artifacts/ → 202 {artifact_id, status}` | ✅ YES | API contract |
| Full React component with useState/useEffect | ❌ NO | Implementation code |

### Section Size Guidelines

To prevent bloat and maintain focus on architecture/contracts:

| Section | Recommended Size | Warning Threshold | Action if Exceeded |
|---------|-----------------|-------------------|-------------------|
| Interface definition (per service) | 10-15 lines | >20 lines | Extract to separate service or condense |
| Configuration tables | 15-20 lines | >30 lines | Create summary table, reference code |
| Prompt templates | 15-20 lines (structure) | >40 lines | Move full template to feature spec |
| Algorithm descriptions | 5-10 lines (high-level) | >20 lines | Use pseudocode or move to feature spec |
| Data contracts (per schema) | 10-20 lines | >30 lines | Split into multiple schemas |
| **Total spec size** | **800-1200 lines** | **>1500 lines** | **Review for feature-level detail creep** |

### Section size red flags

If any single section exceeds these thresholds, it likely contains feature-level detail that should move to feature specs:

| Section Type | Critical Size | Red Flag Indicator | Recommended Action |
|--------------|--------------|-------------------|-------------------|
| Service interfaces (all combined) | >100 lines | Multiple subsections >30 lines each | Extract implementation details to feature spec |
| Configuration tables | >60 lines | Full parameter listings | Create summary table + reference code file |
| Prompt templates (all combined) | >80 lines | Complete prompt text with examples | Keep structure only, move templates to feature spec |
| Reliability patterns | >60 lines | Implementation code present | Keep pattern descriptions, reference implementation files |
| Performance/cost analysis | >50 lines | Duplicated across sections | Consolidate into single location (Reliability section) |
| Any single subsection (###) | >100 lines | Dense implementation detail | Split into multiple subsections or extract to feature spec |

**Auto-check command for oversized sections:**

```bash
# Usage: Run from repo root to detect sections exceeding size thresholds
# Replace "spec-llm.md" with your spec filename
grep -n '^## ' docs/specs/spec-llm.md | while IFS=: read -r start rest; do
  section=$(echo "$rest" | sed 's/^## //')
  next=$(grep -n '^## ' docs/specs/spec-llm.md | grep -A1 "^$start:" | tail -1 | cut -d: -f1)
  [ -z "$next" ] && next=$(wc -l < docs/specs/spec-llm.md)
  size=$((next - start))
  [ $size -gt 100 ] && echo "⚠️  $section: $size lines (threshold: 100)" || echo "✅ $section: $size lines"
done
```

**When to run:**
- During spec reviews before merge
- When adding large sections (>50 lines)
- As part of quarterly spec maintenance

**Expected output:**
- ✅ Sections ≤100 lines (acceptable)
- ⚠️ Sections >100 lines (review for feature-level detail, consider extraction)

**Action on violations:** Review flagged sections for implementation details that belong in feature specs.

### Table of Contents requirement

**REQUIRED for specs >800 lines:**

Add `## Table of Contents` immediately after header metadata, before "Overview & Goals" section.

**Format:**
```markdown
## Table of Contents
- [Overview & Goals](#overview--goals)
- [Architecture](#architecture)
  - [Topology and Frameworks](#topology-and-frameworks)
  - [Component Inventory](#component-inventory)
  - [Service Layer](#service-layer)
- [Interfaces & Data Contracts](#interfaces--data-contracts)
  - [Service Interfaces](#service-interfaces)
  - [Data Schemas](#data-schemas)
- [Data & Storage](#data--storage)
- [Reliability & SLIs/SLOs](#reliability--slisslos)
- [Security & Privacy](#security--privacy)
- [Evaluation Plan](#evaluation-plan)
```

**Auto-generation:** Most Markdown editors (VS Code, Typora, etc.) can auto-generate ToC from headings. Use editor tools to keep ToC synchronized with content.

**Why required:** Specs >800 lines are difficult to navigate without ToC. Readers need quick access to specific sections without scrolling through entire document.

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
```

### References section (optional but recommended)

For complex specs with many dependencies or significant feature implementations, add **References** section at the end of the document.

**Structure:**
```markdown
## References

### Related Feature Specs
- **ft-030**: Anti-hallucination improvements (source attribution, verification service)
- **ft-007**: Manual artifact selection (keyword-based ranking)
- **ft-006**: Bullet generation service modernization

### Related ADRs
- **ADR-045**: GPT-5 reasoning mode configuration for high-stakes accuracy
- **ADR-028**: Remove embeddings, implement manual artifact selection
- **ADR-031-034**: Anti-hallucination architecture decisions
- **ADR-022**: GPT-5 model migration strategy

### External Documentation
- [OpenAI GPT-5 API Documentation](https://platform.openai.com/docs/guides/gpt-5)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [LangChain Document Loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/)
```

**When to include:**
- Spec references >3 feature specs or ADRs
- Significant external dependencies (LLM providers, frameworks)
- Complex architectural decisions requiring context from other docs

**Benefits:**
- Helps readers discover related documentation
- Provides context for architectural decisions
- Creates traceable links between specs, features, and decisions

### Reference Strategy - Single Source of Truth

**Principle:** Avoid duplicating content that's better maintained elsewhere.

**Reference Types:**

1. **Code as Authority** (for implementation details)
   ```markdown
   **Source of Truth:** See `backend/llm_services/.../model_registry.py`
   for authoritative model configurations and current pricing.
   ```

2. **Docs as Authority** (for cross-cutting concerns)
   ```markdown
   **Comprehensive Security Documentation:**
   - Frontend security: `docs/security/frontend-security.md`
   - Backend security: `docs/security/backend-security.md`
   ```

3. **Specs as Authority** (for cross-spec dependencies)
   ```markdown
   **See complete schema documentation:** [`docs/specs/spec-database-schema.md`](spec-database-schema.md)
   ```

**When to use each:**

| Content Type | Reference Target | Example |
|--------------|-----------------|---------|
| Live configuration values | Code file | Model pricing → `model_registry.py` |
| Deployment procedures | Docs guide | Deployment steps → `docs/deployment/README.md` |
| Cross-cutting concerns | Docs guide | Security patterns → `docs/security/` |
| Detailed schemas | Separate spec | Database tables → `spec-database-schema.md` |

**Benefits:** Prevents duplication, easier maintenance, single source of truth per topic.

## Quality & Submission Checklist

**Run these checks before submitting your spec for review:**

### 1. Cross-Spec Consistency

**Verify consistency with related specs:**

| Check | Example | Why It Matters |
|-------|---------|----------------|
| **API contracts match** | Frontend `POST /api/v1/artifacts/` matches Backend endpoint | Prevents integration bugs |
| **Schema alignment** | Database schema in `spec-api.md` matches `spec-database-schema.md` | Single source of truth |
| **Version compatibility** | Frontend uses API v4.8 contracts from Backend spec | API versioning |
| **Error codes** | All specs use same error taxonomy | Consistent error handling |
| **SLO alignment** | Frontend P95 <200ms + Backend P95 <500ms = Total <700ms | E2E latency budgets |

**How to check:**
1. List all specs that reference your component: `grep -r "spec-<name>" docs/specs/`
2. Review each reference for contract alignment
3. Update cross-references if contracts changed
4. Add "References" section if >3 related specs

### 2. Size Validation

**Check total spec size:** Aim for 800-1200 lines. If spec exceeds 1500 lines, review for feature-level detail creep and consider extracting to separate specs.

### 3. Required Elements

**Verify all required sections present:**
- ✅ Header (version, status, contracts, git tag)
- ✅ Table of Contents (if spec >800 lines)
- ✅ Overview & Goals (linked to PRD)
- ✅ Architecture (topology diagram + component inventory)
- ✅ Interfaces & Data Contracts
- ✅ Data & Storage
- ✅ Reliability & SLIs/SLOs
- ✅ Security & Privacy
- ✅ Evaluation Plan

### 4. Git Compliance

**Before merge:**
1. ✅ Increment version number if contracts changed
2. ✅ Add git tag: `git tag spec-<name>-vX.Y.Z`

## Quick Reference: Minimal Spec Template

**Copy-paste starting point:**

```markdown
# Tech Spec — <spec-name>

**Version:** v1.0.0
**File:** docs/specs/spec-<spec>.md
**Status:** Current
**PRD:** `prd.md` (vX.Y)
**Contract Versions:** API vX.Y • Schema vX.Y
**Git Tag:** `spec-<spec>-v1.0.0`

## Overview & Goals
[What are we building and why? Link to PRD.]

## Architecture (Detailed)

### Topology (frameworks)
[Diagram showing components + frameworks + protocols]

### Component Inventory
| Component | Framework | Purpose | Interfaces | Depends On | Scale/HA | Owner |
|-----------|----------|---------|------------|------------|----------|-------|
| ...       | ...      | ...     | ...        | ...        | ...      | ...   |

## Interfaces & Data Contracts
[API endpoints, schemas, error taxonomy]

## Data & Storage
[Tables, indexes, migrations, retention]

## Reliability & SLIs/SLOs
[Timeouts, retries, targets, fault tolerance]

## Security & Privacy
[Authn/z, PII, secrets, logging]

## Evaluation Plan
[Datasets, metrics, thresholds, test harness]
```