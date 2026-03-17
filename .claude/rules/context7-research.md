---
paths:
  - "docs/**"
---

# Context7 Library Research Workflow

When a document references external libraries, frameworks, or APIs, use Context7 MCP tools to fetch current documentation instead of relying on training data.

## Tools

| Tool | Purpose |
|------|---------|
| `mcp__plugin_context7_context7__resolve-library-id` | Resolve a library name to its Context7 library ID |
| `mcp__plugin_context7_context7__query-docs` | Fetch documentation for a resolved library ID |

## Workflow

1. **Identify** — List all external libraries, frameworks, and APIs referenced in the document
2. **Resolve** — Call `mcp__plugin_context7_context7__resolve-library-id` with `libraryName` for each library (max 3 calls)
3. **Fetch** — Call `mcp__plugin_context7_context7__query-docs` with the resolved `libraryId` and a focused `topic` string (max 3 calls)
4. **Incorporate** — Weave findings into the relevant document sections (see skill-specific guidance)

## Constraints

- Maximum 3 calls per tool per skill invocation
- Always pass a `topic` parameter to `query-docs` to get focused results
- If Context7 does not have the library, fall back to `/find-docs`

## Fallback

Use `/find-docs` when Context7 cannot resolve a library or when broader technical documentation is needed.
