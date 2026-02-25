---
paths:
  - ".claude/skills/**"
---

# Skill Development Conventions

When creating or modifying skills in `.claude/skills/`, follow these conventions.

## Directory Structure

Each skill lives in its own directory under `.claude/skills/`:

```
.claude/skills/<skill-name>/
  SKILL.md        # Skill definition (required)
  scripts/        # Helper scripts called by the skill
  references/     # Reference docs the skill reads for context
  assets/         # Templates, schemas, or other static files
```

## SKILL.md Format

```markdown
---
name: <verb-noun>
description: <one-line purpose>
metadata:
  triggers:
    - <natural language trigger phrase>
    - <another trigger phrase>
---

# <skill-name>

<Purpose paragraph>

## Instructions

<Step-by-step instructions for Claude to follow>
```

## Naming

- Skill directory names use `verb-noun` format (e.g., `manage-work`, `define-prd`, `run-tdd`)
- Names should be kebab-case, concise, and action-oriented

## Key Conventions

- Skills are the **only** place that mutates `docs/workflow-state.yaml` — hooks are read-only
- Skills should reference `docs/workflow-state.yaml` as the single source of truth
- Skills that spawn subagents should specify the agent by name from `.claude/agents/`
- Scripts in `scripts/` should use Python with only standard library dependencies
