---
name: vibeflow-intake
description: Conversational demand clarification and feasibility research before formal work item registration
metadata:
  triggers:
    - intake
    - new idea
    - I want to build
    - explore feasibility
    - should I build
    - assess feature
    - pre-register
---

# vibeflow-intake

Conversational demand clarification and feasibility research before formal work item registration.

## Purpose

This skill helps users go from a vague idea to a concrete work item registration. It runs **before** `/vibeflow-workitem register` to ensure the right track, scope, and description are chosen.

Works on any branch (including `main`).

## 4-Phase Workflow

### Phase 1: Demand Clarification

Ask the user to clarify the following (skip items they've already provided):

1. **Problem** — What problem are you solving? What's broken or missing?
2. **Users** — Who benefits from this? (end users, developers, ops, etc.)
3. **Done Criteria** — How will you know it's done? What does success look like?
4. **Constraints** — Any technical, time, or compatibility constraints?
5. **Scope Signal** — Is this a bug fix, a single feature, a multi-component change, or a system-level change?

Keep the conversation natural. Ask follow-up questions if answers are vague. One or two rounds is usually enough.

### Phase 2: Feasibility Research

Delegate to the `codebase-analyst` agent for read-only codebase analysis:

- Does existing code support this, or is new infrastructure needed?
- What files/modules would be affected?
- Are there existing patterns to follow?
- What are the risks (high coupling, missing tests, architectural debt)?

**Skip this phase** for obvious Micro/Small items where the scope is clear and the change is localized.

### Phase 3: Synthesis

Produce an **Intake Brief** (displayed in conversation, not persisted to disk):

```
## Intake Brief

**Problem**: [1-2 sentences]
**Users**: [who benefits]
**Feasibility**: [summary from Phase 2, or "Skipped — scope is clear"]
**Complexity**: [Low / Medium / High]
**Recommended Track**: [Micro / Small / Medium / Large]
**Rationale**: [why this track]
**Suggested Description**: "<description for register command>"
**Suggested ID**: <numeric ID>
```

### Phase 4: Handoff

Present the Intake Brief to the user. If they confirm:

```
/vibeflow-workitem register "<description>" <ID> <track>
```

If they want changes, loop back to the relevant phase.

## Guidelines

- **Ephemeral output**: The Intake Brief lives in the conversation only — no files are written.
- **Bias toward smaller tracks**: When in doubt, recommend Small over Medium. Users can always upgrade.
- **Don't over-research**: Phase 2 should take 1-2 minutes, not 10. Quick scan, not deep dive.
- **Natural language**: This is a conversation, not a form. Adapt to the user's communication style.
