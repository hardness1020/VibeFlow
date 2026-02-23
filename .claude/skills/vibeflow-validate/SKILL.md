---
name: vibeflow-validate
description: Checkpoint validation and guardrail enforcement for the VibeFlow docs-first development workflow
metadata:
  triggers:
    - validate checkpoint
    - check gate
    - am I ready
    - can I proceed
    - can I start implementing
    - can I deploy
---

# vibeflow-validate

Checkpoint validation and guardrail enforcement for the VibeFlow docs-first development workflow.

## Purpose

This skill validates checkpoint completion before stage progression:
- Checks that required artifacts exist with all sections
- Enforces the docs-first mandate
- Runs validation scripts and reports pass/fail/warn status
- Returns structured JSON reports with blocking issues

## Workflow

```
Validate Request
    │
    ├── Determine checkpoint or document type
    ├── Locate required artifacts
    └── Select validation script
    │
    ▼
Run Validation
    │
    ├── Execute validation checks
    ├── Collect errors and warnings
    └── Generate JSON report
    │
    ▼
Report Results
    │
    ├── Output pass/fail summary
    ├── List blocking issues
    └── Return exit code (0=pass, 1=fail, 2=warn)
```

## Usage

### Validate a Specific Checkpoint

```
/vibeflow-validate checkpoint <number>
```

Example:
```
/vibeflow-validate checkpoint 1
```

### Validate Current State

```
/vibeflow-validate
```

This auto-detects the current stage and validates the appropriate checkpoint.

### Validate Specific Document

```
/vibeflow-validate prd
/vibeflow-validate discovery <ID>
/vibeflow-validate spec <spec-name>
/vibeflow-validate feature <ID>
/vibeflow-validate opnote <ID>
```

## Checkpoints

| # | Checkpoint | After Stage | Validates |
|---|------------|-------------|-----------|
| 1 | Planning Complete | D | PRD, Discovery, SPECs, ADRs |
| 2 | Design Complete | E | FEATURE spec with API Design |
| 3 | Tests Complete | F | Failing unit tests with stubs |
| 4 | Implementation Complete | H | Passing tests, quality validation |
| 5 | Release Ready | J | OP-NOTE with all sections |
| 6 | Deployed | L | Deployment verified, indices updated |

## Scripts

The following scripts are available in `scripts/`:

- `validate_checkpoint.py` - Master validator, orchestrates all checks
- `check_planning.py` - Checkpoint #1: Planning phase validation
- `check_design.py` - Checkpoint #2: Design phase validation
- `check_tests.py` - Checkpoint #3: Test phase validation
- `check_implementation.py` - Checkpoint #4: Implementation validation
- `check_release.py` - Checkpoint #5: Release readiness validation
- `check_deployed.py` - Checkpoint #6: Deployment verification

## Output Format

All validation scripts output JSON with this structure:

```json
{
  "checkpoint": 1,
  "name": "Planning Complete",
  "valid": false,
  "issues": [
    {
      "severity": "error",
      "file": "docs/prds/prd.md",
      "message": "Missing required section: Success Metrics"
    }
  ],
  "warnings": [
    {
      "file": "docs/specs/spec-api.md",
      "message": "Spec version not incremented despite contract changes"
    }
  ],
  "passed": 5,
  "failed": 2,
  "summary": "Checkpoint #1 NOT PASSED: 2 errors, 1 warning"
}
```

## Exit Codes

- `0` - All validations passed
- `1` - Validation failed (blocking issues found)
- `2` - Warnings only (can proceed with caution)

## Manifest Update

After a checkpoint passes, update the work item's entry in `docs/workflow-state.yaml`:
- Set `checkpoint` to the checkpoint number that passed (1-6)

## References

See `references/checkpoint-criteria.md` for detailed validation criteria for each checkpoint.
