# VibeFlow — AI-Assisted Docs-First Development Workflow

## Project Identity

VibeFlow is a workflow template that enforces docs-first, TDD-driven development for AI-assisted software engineering. It uses Claude Code skills and hooks to ensure documentation stays current and tests drive implementation.

## Core Principle: Docs-First Mandate

**All documentation MUST exist and be validated BEFORE any code is written.** Stages A-E produce documents; Stages F-H implement code that must match those documents.

## Enforcement Rules

These rules are **deterministic** — enforced by hooks and skills:

1. **Branch binding (UserPromptSubmit hook):** All prompts blocked unless current branch is `feat/<slug>` for an active work item. Manage-work commands are exempted so users can register new work items from main.
2. **Checkpoint gates (two layers):**
   - **UserPromptSubmit hook:** `checkpoint-gate.py` blocks prompts containing "advance"/"close" if checkpoint not passed (deterministic safety net)
   - **Manage-work skill:** `advance` and `close` commands validate checkpoints before updating the manifest (skill-instructed, redundant backup)
3. **Exception:** Prompts are always allowed when no manifest exists (initial project setup) or when no active work items are present
4. **All hooks are read-only** — no hook mutates any file. All manifest updates happen in skills.

## Reference

Workflow stages, tracks, branch conventions, file naming, skills, and agents are documented in `.claude/rules/`. See `README.md` for the full pipeline diagram and contributor details.
