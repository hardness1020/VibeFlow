---
name: vibeflow-feature-spec
description: Create Feature Specs for Stage E of the VibeFlow docs-first workflow
metadata:
  triggers:
    - create feature spec
    - write feature
    - design feature
    - acceptance criteria
    - API design
    - Stage E
    - feature planning
---

# vibeflow-feature-spec

Create Feature Specs for Stage E of the VibeFlow docs-first workflow.

## Purpose

This skill creates Feature Spec documents that:
- Define the API design contract (exact function/class signatures)
- Specify testable acceptance criteria
- Document design changes (UI/API/schema)
- Include test and evaluation plan
- Reference discovery findings and specs

## Workflow

```
Stage E: Feature Spec
    │
    ├── Define API Design (exact signatures)
    ├── Write testable acceptance criteria
    ├── Document design changes (UI/API/schema)
    ├── Create test and evaluation plan
    ├── Map telemetry and metrics
    └── Reference discovery findings and specs
```

## Usage

### Create Feature Spec

```
/vibeflow-feature-spec <ID> <slug>
```

Creates `docs/features/ft-<ID>-<slug>.md` with required sections.

Example:
```
/vibeflow-feature-spec 030 anti-hallucination
```

### Validate Feature Spec

```
/vibeflow-feature-spec validate <ID>
```

Validates that the feature spec has all required sections.

### Update Schedule

```
/vibeflow-feature-spec schedule
```

Updates `docs/features/schedule.md` with feature status.

## Document Requirements

### Required Sections

**For All Features:**
- Header (ID, File, Owner, TECH-SPECs with versions)
- Architecture Conformance
- API Design (exact signatures)
- Acceptance Criteria
- Design Changes
- Test & Eval Plan
- Telemetry & Metrics
- Edge Cases & Risks

**For Medium/Large Features (Additional):**
- Stage B Discovery Findings
  - Test Impact Analysis
  - Existing Implementation Analysis
  - Dependency & Side Effect Mapping

### API Design Section (Critical)

The API Design section defines the contract for Stage F (test writing):

```markdown
## API Design

### ServiceName.method_name()
- **Signature:** `method_name(param: Type, param2: Type = default) -> ReturnType`
- **Purpose:** [Brief description]
- **Parameters:**
  - `param`: [Description]
  - `param2`: [Description, default value]
- **Returns:** [Description of return type and structure]

### API Endpoint: POST /api/v1/endpoint
- **Method:** POST
- **Path:** `/api/v1/endpoint`
- **Request Body:**
  ```json
  {
    "field": "type"
  }
  ```
- **Response Body:**
  ```json
  {
    "result": "type"
  }
  ```


**Why This Matters:**
- Stage F creates implementation stubs from these signatures
- Tests are written using these exact function names
- Any changes require updating specs first (Stage G.1)

### Acceptance Criteria

Format as testable checklist or Gherkin:

```markdown
## Acceptance Criteria

- [ ] User can [action] with [condition] resulting in [outcome]
- [ ] System returns [response] when [condition]
- [ ] Error [X] is shown when [condition]

Or Gherkin:

Given [context]
When [action]
Then [expected outcome]
```

## Validation

- `scripts/validate_feature.py` — Validate feature spec structure and API Design

## References

See `assets/`:
- `feature-template.md` — Complete feature spec template

See `references/`:
- `api-design-guide.md` — API Design section guidance

## Checkpoints

**Checkpoint #2 (Design Complete):**
```
/vibeflow-validate checkpoint 2
```
Validates:
- Feature spec exists with all sections
- API Design has exact signatures
- Acceptance criteria are testable
- Links to TECH-SPECs with versions
