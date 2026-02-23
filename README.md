# VibeFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hardness1020/VibeFlow?style=social)](https://github.com/hardness1020/VibeFlow/stargazers)

A docs-first, TDD-driven workflow template for AI-assisted software engineering.

---

## Using VibeFlow in your project? Open a PR to add it here! 🤩

| Project | Description |
|:---:|---|
| <a href="https://github.com/hardness1020/CV-Tailor"><img src="assets/CV-Tailor.png" width="200" /></a> | **[CV-Tailor](https://github.com/hardness1020/CV-Tailor)** — A full-stack app that transforms work artifacts (GitHub repos, PDFs, web content) into customized, job-specific CVs and cover letters using OpenAI API. |

---

## Benefits

- **Branch-locked development**: Hooks block all prompts unless you're on a `feat/<slug>` branch for an active work item
- **Docs-before-code workflow**: Planning stages A-E produce documentation; implementation stages F-H must conform to it
- **Checkpoint gates prevent shortcuts**: Orchestrator validates checkpoints before advancing; hook blocks advance/close prompts as a safety net
- **Living documentation**: Auto-validate hook checks doc-code sync after every edit
- **Decisions are traceable**: IDs link docs → branches → PRs → code across the full lifecycle

---

## Workflow Pipeline

```
                        WORKFLOW PIPELINE
                        =================

     PLANNING           DESIGN    IMPLEMENTATION         RELEASE (optional)
  ┌─────────────────┐  ┌─────┐  ┌───────────────┐  ┌─────────────────────┐
  │                  │  │     │  │               │  │                     │
  A → B → C → D ──────► E ──────► F → G → H ──────► I → J → K → L
  │         │ CP#1  │  │CP#2 │  │  CP#3   CP#4 │  │        CP#5   CP#6 │
  └─────────────────┘  └─────┘  └───────┬───────┘  └─────────────────────┘
                                        │
                                        └──► DONE (close without release)

  TRACKS (define planning depth, release is always optional):
  ─────────────────────────────────────────────────────────────
  Large:   A ─────────────────────────────────────────────► H → DONE or I-L
  Medium:      B ─────────────────────────────────────────► H → DONE or I-L
  Small:                 E ───────────────────────────────► H → DONE or I-L
  Micro:                           F ─────────────────────► G → DONE

  CHECKPOINTS:
  ────────────
  #1 Planning Complete .... after D    #4 Implementation Complete .. after H
  #2 Design Complete ...... after E    #5 Release Ready ........... after J
  #3 Tests Complete ....... after F    #6 Deployed ................ after L

  BRANCH LIFECYCLE:
  ─────────────────
  Register ──► git checkout -b feat/<slug>
     │              │
     │         (all work on this branch)
     │              │
     └──► Close/Done ──► merge feat/<slug> → main
```



| Stage | Name | Output |
|-------|------|--------|
| A | Initiate | PRD with goals and success metrics |
| B | Discovery | Codebase analysis, impact mapping |
| C | Specify | Tech specs with architecture diagrams |
| D | Decide | ADRs for non-trivial choices |
| | **CHECKPOINT #1** | **Planning Complete** |
| E | Plan | Feature spec with acceptance criteria |
| | **CHECKPOINT #2** | **Design Complete** |
| F | Test (RED) | Failing unit tests define behavior |
| | **CHECKPOINT #3** | **Tests Complete** |
| G | Implement (GREEN) | Minimal code to pass tests |
| H | Refactor | Integration tests + clean code |
| | **CHECKPOINT #4** | **Implementation Complete** |
| I | Reconcile | Sync specs with implementation |
| J | Prepare | OP-NOTE deployment runbook |
| | **CHECKPOINT #5** | **Release Ready** |
| K | Deploy | Follow OP-NOTE, verify in production |
| L | Close | Update indices, tag release |
| | **CHECKPOINT #6** | **Deployed** |

---

## Usage

### Getting Started

```bash
git clone https://github.com/hardness1020/VibeFlow.git
```

Start with `/vibeflow-orchestrator` to navigate the workflow.

```
/vibeflow-orchestrator register "<description>" <ID> <track>
/vibeflow-orchestrator status [<ID>]
/vibeflow-orchestrator advance <ID>
/vibeflow-orchestrator close <ID>
/vibeflow-orchestrator next <ID>
```

### Quick Workflow

```
/vibeflow-orchestrator register "Add search feature" 1 small
/vibeflow-feature-spec 1 add-search-feature
/vibeflow-validate checkpoint 2
/vibeflow-tdd-implementation red
/vibeflow-tdd-implementation green
/vibeflow-tdd-implementation refactor
/vibeflow-validate checkpoint 4
/vibeflow-orchestrator close 1
```

### Workflow Tracks

| Track | Scope | Stages | Release | Example |
|-------|-------|--------|---------|---------|
| **Micro** | Bug fix, typo | F → G → DONE | No | Fix typo, update config |
| **Small** | Single feature | E → F → G → H → DONE | Optional (I-L) | Add form field, UI polish |
| **Medium** | Multi-component | B → C → D → E → F → G → H → DONE | Optional (I-L) | New API endpoint |
| **Large** | System change | A → B → C → D → E → F → G → H → DONE | Optional (I-L) | New auth system |

---

## Skills

| Skill | Purpose | Stages |
|-------|---------|--------|
| `/vibeflow-orchestrator` | Select workflow track, navigate between stages, coordinate handoffs, enforce stage gates | All |
| `/vibeflow-planning` | Create PRDs with success metrics, run spec-driven codebase discovery, write tech specs with diagrams, document ADRs with trade-offs | A-D |
| `/vibeflow-feature-spec` | Generate feature specs with acceptance criteria, design API contracts, create test plans with golden files | E |
| `/vibeflow-tdd-implementation` | Write failing unit tests first (RED), implement minimal code (GREEN), add integration tests and refactor (REFACTOR) | F-H |
| `/vibeflow-release` | Reconcile specs with implementation, create OP-NOTE deployment runbooks, deploy and verify, close loop and tag release | I-L |
| `/vibeflow-validate` | Verify checkpoint completion, enforce blockers, check doc-code sync, validate test coverage | 1-6 |

---

## Enforcement (Hooks)

Hooks run automatically and deterministically — all are read-only (no file mutations). Two block invalid actions, four provide context/feedback. All fail open.

| Hook | Trigger | Fires On | Outcome | Reads |
|------|---------|----------|---------|-------|
| `workflow-state-inject.py` | Every prompt | `UserPromptSubmit` | Injects `[VibeFlow] Active: <slug> (Stage X, feat/<slug>)` | Manifest |
| `workitem-branch-guard.py` | Every prompt | `UserPromptSubmit` | **Blocks** if branch ≠ active `feat/<slug>` (orchestrator commands exempt) | Manifest |
| `checkpoint-gate.py` | Every prompt | `UserPromptSubmit` | **Blocks** advance/close if checkpoint not passed | Manifest + `validate_checkpoint.py` |
| `auto-validate.sh` | Conversation end | `Stop` | Shows doc validation pass/fail feedback | Validation scripts |
| `doc-path-tracker.py` | Conversation end | `Stop` | **Warns** if document paths missing from manifest | Manifest |
| `stage-transition-update.py` | Conversation end | `Stop` | Reminds to advance if artifacts exist | Manifest |

---

```
  User Prompt
       │
       ▼
  ┌─ Hooks (UserPromptSubmit) ───────────────────────────┐
  │  state-inject │ branch-guard │ checkpoint-gate       │
  └───────────────────────┬──────────────────────────────┘
                          ▼
  ┌─ Skills (on demand) ─────────────────────────────────┐
  │  orchestrator │ planning │ feature-spec │ tdd │ …    │
  └───────────────────────┬──────────────────────────────┘
                          ▼
  ┌─ Hooks (Stop) ───────────────────────────────────────┐
  │  auto-validate │ doc-path-tracker │ stage-transition │
  └──────────────────────────────────────────────────────┘
```

---

## Contributing

Contributions welcome. Follow the workflow when contributing, add examples, and test your changes.

## License

[MIT](LICENSE)
