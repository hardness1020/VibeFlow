---
name: vibeflow-release
description: Release preparation for Stages I-L of the VibeFlow docs-first workflow
metadata:
  triggers:
    - prepare release
    - deployment
    - OP-NOTE
    - close loop
    - spec reconciliation
    - Stage I
    - Stage J
    - Stage K
    - Stage L
    - release checklist
---

# VibeFlow Release Skill

## Purpose

Guides release preparation through Stages I-L of the VibeFlow workflow:
- **Stage I**: Spec Reconciliation (sync docs with implementation)
- **Stage J**: OP-NOTE Creation (deployment documentation)
- **Stage K**: Deploy (execute deployment)
- **Stage L**: Close Loop (update indices, retrospective)

## Triggers

Invoke this skill when you hear:
- "prepare release"
- "deployment"
- "OP-NOTE"
- "close loop"
- "spec reconciliation"
- "Stage I/J/K/L"
- "release checklist"

## Workflow

```
Stage I: Spec Reconciliation
    │
    ├── Compare Feature Spec vs actual implementation
    ├── Update SPEC documents with any deviations
    ├── Reconcile ADRs with decisions made
    └── Ensure docs match deployed reality
    │
    ▼
Stage J: OP-NOTE Creation
    │
    ├── Create docs/op-notes/op-<feature>.md
    ├── Document: Preflight, Deploy Steps, Monitoring
    ├── Document: Runbook, Rollback, Post-Deploy Checks
    └── Update op-notes/index.md
    │
    ▼
Stage K: Deploy
    │
    ├── Execute preflight checklist
    ├── Run deployment steps
    ├── Execute post-deploy verification
    └── Monitor for issues
    │
    ▼
Stage L: Close Loop
    │
    ├── Update master indices
    ├── Mark feature complete
    ├── Run retrospective (Large track)
    └── Archive or link documentation
```

## Commands

### Check Release Readiness
```bash
# Validate OP-NOTE completeness
python scripts/validate_opnote.py --json

# Check spec reconciliation status
python scripts/reconcile_specs.py --json
```

### Create OP-NOTE
1. Copy template from `assets/opnote-template.md`
2. Fill in all required sections
3. Run validation: `python scripts/validate_opnote.py`

## Stage Details

### Stage I: Spec Reconciliation

**Purpose**: Ensure documentation matches implementation before release.

**Tasks**:
1. Compare Feature Spec API Design with actual implementation
2. Update any divergent signatures or behaviors
3. Review SPEC documents for accuracy
4. Update ADRs if decisions changed during implementation
5. Document any deviations discovered

**Validation**:
```bash
python scripts/reconcile_specs.py --feature-id <FEATURE-ID>
```

### Stage J: OP-NOTE Creation

**Purpose**: Document everything operators need for deployment.

**Required Sections**:
- Header (file, date, features covered)
- Preflight (prerequisites, migrations, env vars)
- Deploy Steps (ordered commands with verification)
- Monitoring (dashboards, alerts, SLOs)
- Runbook (symptom → diagnose → remediate)
- Rollback (precise steps, data compatibility)
- Post-Deploy Checks (smoke tests, owners)

**Location**: `docs/op-notes/op-<feature-slug>.md`

**Validation**:
```bash
python scripts/validate_opnote.py --path docs/op-notes/op-<feature>.md
```

### Stage K: Deploy

**Purpose**: Execute deployment following OP-NOTE.

**Pre-Deploy Checklist**:
- [ ] OP-NOTE complete and validated
- [ ] All preflight items checked
- [ ] Rollback plan verified
- [ ] On-call notified
- [ ] Monitoring dashboards open

**Post-Deploy Checklist**:
- [ ] Health checks passing
- [ ] Smoke tests executed
- [ ] Error rates nominal
- [ ] Performance within SLOs

### Stage L: Close Loop

**Purpose**: Finalize feature lifecycle.

**Tasks**:
1. Update `docs/features/index.md` - mark feature complete
2. Update `docs/op-notes/index.md` - link OP-NOTE
3. Update `docs/specs/index.md` if new SPECs created
4. Create git tag for release
5. Run retrospective (Large track only)

**Indices to Update**:
- Feature index with completion status
- OP-NOTE index with deployment link
- SPEC index with version updates
- ADR index with new decisions

## Gate Requirements

**Checkpoint #5 (Release Ready)**:
- [ ] OP-NOTE exists with all required sections
- [ ] Spec reconciliation complete
- [ ] Rollback procedure documented
- [ ] Monitoring configured

**Checkpoint #6 (Deployed)**:
- [ ] Deployment successful
- [ ] Post-deploy checks passing
- [ ] Indices updated
- [ ] Git tag created

## Files

```
vibeflow-release/
├── SKILL.md                          # This file
├── scripts/
│   ├── validate_opnote.py           # OP-NOTE validation
│   └── reconcile_specs.py           # Spec reconciliation checker
└── assets/
    └── opnote-template.md           # OP-NOTE template
```

## Integration

This skill integrates with:
- **vibeflow-validate**: Use `/validate checkpoint 5` and `/validate checkpoint 6`
- **vibeflow-tdd-implementation**: Follows after Stage H complete
- **vibeflow-planning**: References SPECs and ADRs created in planning

## Best Practices

1. **Never deploy without OP-NOTE**: Gate production deployments
2. **Keep runbooks actionable**: Symptom → Diagnose → Remediate
3. **Test rollback procedures**: Don't assume they work
4. **Update indices promptly**: Don't let documentation lag
5. **Reconcile specs honestly**: Document what was actually built
