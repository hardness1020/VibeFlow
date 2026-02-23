# VibeFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hardness1020/VibeFlow?style=social)](https://github.com/hardness1020/VibeFlow/stargazers)

A docs-first, TDD-driven workflow template for AI-assisted software engineering.

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
/vibeflow-orchestrator next <ID>
```

### Workflow Tracks

| Track | Scope | Stages | Example |
|-------|-------|--------|---------|
| **Micro** | Bug fix, typo | F → G | Fix typo, update config |
| **Small** | Single feature | E → F → G → H | Add form field, UI polish |
| **Medium** | Multi-component | B → C → D → E → F → G → H → I → J | New API endpoint |
| **Large** | System change | Full A → L | New auth system |

---

## Workflow Pipeline

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

## Benefits

- **Docs stay current**: Living documentation synchronized with code
- **Tests catch regressions**: TDD ensures comprehensive coverage
- **AI stays aligned**: Structured skills prevent common pitfalls
- **Decisions are traceable**: IDs link docs → branches → PRs → code
- **Reviews are strategic**: 6 checkpoints instead of constant interruption

---

## Contributing

Contributions welcome. Follow the workflow when contributing, add examples, and test your changes.

## License

[MIT](LICENSE)
