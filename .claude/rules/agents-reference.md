# Agents Reference

Specialized subagents with tool restrictions enforced by PreToolUse hooks:

| Agent | Stages | Tools | Hook | Purpose |
|-------|--------|-------|------|---------|
| `codebase-analyst` | B | Read, Grep, Glob | — | Analyze codebase, map dependencies |
| `spec-drafter` | C-D | Read, Grep, Glob, Write, Edit | `enforce-docs-only.py` | Draft specs and ADRs (docs/ only) |
| `api-researcher` | E | Read, Grep, Glob | — | Analyze existing API patterns |
| `test-writer` | F | Read, Grep, Glob, Write, Edit, Bash | `enforce-test-files-only.py` | Create stubs + failing tests |
| `implementer` | G | Read, Grep, Glob, Write, Edit, Bash | `enforce-no-test-no-doc.py` | Implement to pass tests (source only) |

Agent definitions live in `.claude/agents/`. Enforcement hooks exit 2 to block, exit 0 to allow, and fail open on errors.
