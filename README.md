# VibeFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hardness1020/VibeFlow?style=social)](https://github.com/hardness1020/VibeFlow/stargazers)

**A comprehensive, docs-first development workflow template for AI-assisted software engineering.**

Transform chaotic AI-assisted development into a structured, predictable process. VibeFlow provides battle-tested workflow rules, documentation templates, and TDD practices that keep your AI assistant aligned with your goals from planning through deployment.

---

## Why VibeFlow?

### The Problem

Working with AI coding assistants like Claude Code is powerful but chaotic:
- Code changes without documentation become technical debt
- AI assistants jump straight to coding without understanding requirements
- Test coverage gaps emerge because tests are written after code
- Contract changes break dependencies silently
- No clear handoff points for human review
- Living docs drift from implementation reality

### The Solution

VibeFlow enforces a **docs-first, TDD-driven workflow** with:

- **Living Documentation**: PRDs, Tech Specs, ADRs, and Feature specs that stay synchronized with code
- **Hybrid TDD**: Unit tests written before code (RED), integration tests during refactor (REFACTOR)
- **Smart Workflow Tracks**: Choose Micro/Small/Medium/Large based on change scope
- **Strategic Review Checkpoints**: 6 grouped checkpoints instead of 11 individual stops
- **Automatic Enforcement**: Built-in blockers prevent common mistakes (code before docs, implementation before tests)
- **Traceability**: IDs link docs → branches → PRs → commits → code

---

## Key Features

### Docs-First Development
- **PRD** defines business goals and success metrics before any code
- **Tech Specs** document contracts, topology, and SLOs with versioning
- **ADRs** capture architectural decisions with context and trade-offs
- **Feature Specs** provide implementation blueprints with test plans
- **Runbooks** ensure smooth deployments and operations

### Hybrid TDD Workflow
- **RED Phase**: Write failing unit tests first to clarify requirements and design APIs
- **GREEN Phase**: Implement minimal code to make unit tests pass
- **REFACTOR Phase**: Add integration tests, then refactor while keeping all tests green
- **Coverage Targets**: 80%+ for business logic with fast feedback loops

### Flexible Size-Based Tracks

| Track | Scope | Required Stages | Example |
|-------|-------|-----------------|---------|
| **Micro** | Bug fix, typo, small refactor | F → G (TDD only) | Fix typo, update config |
| **Small** | Single feature, no contracts | E → F → G → H | Add field to form, UI polish |
| **Medium** | Multi-component, no new services | B → C → D → E → F → G → H → I | New API endpoint |
| **Large** | System change, new contracts/services | Full A → K | New LLM integration, auth system |

### Strategic Review Checkpoints

1. **Planning Complete** (after Stage D): PRD + Discovery + SPECs + ADRs
2. **Design Complete** (after Stage E): FEATURE spec
3. **Tests Complete** (after Stage F): Failing unit tests
4. **Implementation Complete** (after Stage H): Working + refactored code
5. **Release Ready** (after Stage I): OP-NOTE
6. **Deployed** (after Stage K): Post-deployment verification

---

## Quick Start

### 1. Use This Template

```bash
# Clone the repository
git clone https://github.com/hardness1020/VibeFlow.git

# Or use as GitHub template
# Click "Use this template" button on GitHub
```

### 2. Point AI Agent to the Rules

Add to your project context or configuration:

```
Use the workflow rules in /rules/ for all development activities:
- 00-workflow.md: Main workflow governance
- 01-prd.md: Product requirements
- 02-discovery/: Codebase discovery (policy.md + template.md)
- 03-tech_spec.md: Technical specifications
- 04-adr.md: Architecture decision records
- 05-feature.md: Feature planning
- 06-tdd/: Hybrid TDD practices (policy.md + guide.md)
- 07-op_note.md: Operational runbooks
```

### 3. Choose Your Workflow Track

**For a bug fix or small change:**
```
"Fix the login button styling issue following the Micro track (F → G)"
```

**For a new feature:**
```
"Implement user profile editing following the Medium track (B → C → D → E → F → G → H → I)"
```

**For a major system change:**
```
"Add authentication system following the Large track (full A → K pipeline)"
```

---

## The Complete Workflow Pipeline

```
A. Initiate (PRD)
   ↓
B. Codebase Discovery (Spec-Driven Analysis)
   - Phase 0: Spec Discovery (analyze existing specs first)
   - Phase 1: Spec-Code Validation (verify specs match reality)
   - Phase 2: Test Impact Analysis (identify affected tests, coverage gaps)
   - Phase 3: Dependency & Side Effect Mapping (trace impact radius)
   - Phase 4: Reusable Component Discovery (prevent duplication)
   ↓
C. Specify (Tech Specs with Architecture Diagrams)
   ↓
D. Decide (ADRs for Non-Trivial Choices)
   ↓
   [CHECKPOINT #1: Planning Complete]
   ↓
E. Plan (Feature Spec with Acceptance Criteria)
   ↓
   [CHECKPOINT #2: Design Complete]
   ↓
F. Write Unit Tests First (RED Phase: Failing Tests Define Behavior)
   ↓
   [CHECKPOINT #3: Unit Tests Complete]
   ↓
G. Implement to Pass Unit Tests (GREEN Phase: Minimal Code)
   ↓
H. Write Integration Tests & Refactor (REFACTOR Phase: Full Coverage + Clean Code)
   ↓
   [CHECKPOINT #4: Implementation Complete]
   ↓
I. Release Preparation (OP-NOTE: Runbook)
   ↓
   [CHECKPOINT #5: Release Ready]
   ↓
J. Deploy & Verify
   ↓
K. Close Loop (Update Index, Tag Release)
   ↓
   [CHECKPOINT #6: Deployed]
```

---

## Documentation Overview

### `/rules/` - Workflow Rules

| File | Purpose | When to Use |
|------|---------|-------------|
| `00-workflow.md` | Master governance rule | Always - defines the entire pipeline |
| `01-prd.md` | Product requirements template | Stage A - for user-facing changes |
| `02-discovery/` | Codebase discovery (policy + template) | Stage B - for Medium/Large changes |
| `03-tech_spec.md` | Technical specifications | Stage C - for contracts/topology/SLOs |
| `04-adr.md` | Architecture decision records | Stage D - for non-trivial choices |
| `05-feature.md` | Feature planning template | Stage E - for implementation blueprints |
| `06-tdd/` | Hybrid TDD practices (policy + guide) | Stages F/G/H - test-driven implementation |
| `07-op_note.md` | Operational runbooks | Stage I - for deployment/operations |

---

## Real-World Examples

### Example 1: Adding an LLM Feature (Large Track)

**Stage A (PRD)**: Define credibility scoring goals, success metrics (p95 ≤ 400ms, CTR +2pp)

**Stage B (Discovery)**: Comprehensive spec-driven codebase analysis
- Phase 0: Review `spec-llm.md`, `spec-api.md` for existing LLM patterns and contracts
- Phase 1: Validate spec accuracy (discovered 4 undocumented endpoints, spec drift detected)
- Phase 2: Identify 35 affected tests across 4 test files, map coverage gaps in error handling
- Phase 3: Map dependencies (LLM services, circuit breaker, performance tracker, 12 consumers)
- Phase 4: Find reusable `BaseLLMService` pattern, prevent duplicate timeout logic
- Output: `docs/discovery/disco-123.md`

**Stage C (Spec)**: Document new LLM pipeline architecture with diagram, update `spec-llm.md` to v2.0.0

**Stage D (ADR)**: Record decision to use OpenAI vs Anthropic with trade-offs

**Stage E (Feature)**: `ft-123-credibility-score.md` with acceptance criteria, test plan with goldens

**Stage F (Unit Tests)**: Write failing tests for scoring logic with mocked LLM responses

**Stage G (Implement)**: Minimal code to pass unit tests

**Stage H (Integration + Refactor)**: Add real LLM integration tests, refactor for performance

**Stage I (OP-NOTE)**: Document deployment steps, monitoring, rollback procedures

**Stages J-K**: Deploy, verify, update indices, tag release

### Example 2: Quick Bug Fix (Micro Track)

**Stage F**: Write failing test that exposes the bug

**Stage G**: Fix the bug to make the test pass

Done! Commit with test + fix together.

---

## Benefits

### For Individual Developers
- **Clarity**: Always know what to do next and why
- **Confidence**: Comprehensive tests catch regressions
- **Documentation**: Your work is automatically documented
- **Efficiency**: No rework from misaligned requirements

### For Teams
- **Alignment**: Everyone follows the same process
- **Traceability**: Trace features from requirements through deployment
- **Knowledge Sharing**: Docs capture decisions and context
- **Onboarding**: New team members understand the system through living docs

### For AI-Assisted Development
- **Structured Guidance**: AI assistants follow clear, enforced rules
- **Quality Assurance**: Built-in blockers prevent common AI pitfalls
- **Contract Safety**: Versioned specs prevent breaking changes
- **Review Points**: Humans approve at strategic checkpoints
- **Comprehensive Discovery**: AI performs spec-driven codebase analysis before design
- **Reuse Detection**: Prevents duplicate implementations through automated component discovery
- **Test Impact Analysis**: Identifies affected tests and coverage gaps proactively

---

## Why Star This Repository?

If you find VibeFlow useful, please consider starring the repository:

- **Support Development**: Show appreciation for the work and encourage continued improvements
- **Bookmark for Later**: Easy access when you need it
- **Help Others Discover**: More stars = more visibility for others facing similar challenges
- **Join the Community**: Be part of a growing movement toward structured AI-assisted development

**[⭐ Star this repository](https://github.com/hardness1020/VibeFlow)** if you believe in docs-first, TDD-driven development!

---

## Contributing

We welcome contributions! Here's how you can help:

1. **Share Your Experience**: Open issues with workflow improvements based on real usage
2. **Improve Documentation**: Submit PRs for clearer explanations or examples
3. **Add Templates**: Contribute new rule files or documentation templates
4. **Report Issues**: Found a workflow gap? Let us know!

### Contribution Guidelines

- Follow the workflow when contributing (meta, right?)
- Add examples to demonstrate improvements
- Keep rules concise and actionable
- Test your changes

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Inspired by best practices from Stripe, Airbnb, Linear, and other S-tier SaaS products
- Built for use with [Claude Code](https://claude.com/claude-code) by Anthropic
- Community feedback and contributions

---

## Get Started Today

1. **Star this repository** ⭐ to show support and bookmark for later
2. **Clone or fork** the template
3. **Point AI Agent** to the `/rules/` directory
4. **Choose your workflow track** based on change scope
5. **Start building** with confidence

**Questions?** Open an issue or check the [workflow documentation](rules/00-workflow.md).

**Happy coding with VibeFlow!** 🚀
