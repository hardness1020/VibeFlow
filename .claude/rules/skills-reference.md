# Skills Reference

## Workflow Management

| Skill | Purpose |
|-------|---------|
| `/manage-work` | Register, track, advance, close work items |
| `/clarify-demand` | Pre-register demand clarification |
| `/validate-checkpoint` | Checkpoint validation and enforcement |

## Stage Skills

| Skill | Stage | Purpose |
|-------|-------|---------|
| `/define-prd` | A | PRDs with success metrics |
| `/analyze-codebase` | B | Codebase discovery and analysis |
| `/define-tech-spec` | C | Tech specs with architecture |
| `/record-decision` | D | ADRs for non-trivial choices |
| `/create-feature-spec` | E | Feature specs with acceptance criteria |
| `/run-tdd` | F-H | TDD cycle: RED → GREEN → REFACTOR |
| `/prepare-release` | I-L | Reconcile, OP-NOTE, deploy, close |

## Quick Reference

```
/manage-work register "<desc>" <ID> <track>   # Create work item + branch
/manage-work status [<ID>]                     # Dashboard or detail view
/manage-work advance <ID>                      # Move to next stage
/manage-work close <ID>                        # Mark DONE after CP#4
/manage-work next <ID>                         # Show next action
/validate-checkpoint <N>                       # Validate checkpoint
/clarify-demand                                # Clarify idea → register
```
