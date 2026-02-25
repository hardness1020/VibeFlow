# Branch Conventions

Every work item is bound to a dedicated git branch:

- **Format:** `feat/<slug>` (e.g., `feat/add-anti-hallucination-guardrails`)
- **Slug:** The work item key from `docs/workflow-state.yaml` (kebab-case from description)
- **Lifecycle:** Register creates branch → all work happens on branch → close/merge to main
- **Enforcement:** Hook blocks edits on `main` and on branches not matching an active work item
