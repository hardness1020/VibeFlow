---
name: prepare-release
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

# prepare-release

Release preparation for Stages I-L of the VibeFlow docs-first workflow.

## Purpose

This skill guides release preparation through Stages I-L:
- **Stage I**: Spec Reconciliation (sync docs with implementation)
- **Stage J**: OP-NOTE Creation (deployment documentation)
- **Stage K**: Deploy (execute deployment)
- **Stage L**: Close Loop (update indices, retrospective)

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

## Usage

### Check Release Readiness

```
/prepare-release check
```

Validates OP-NOTE completeness and spec reconciliation status.

### Create OP-NOTE

```
/prepare-release opnote <feature-slug>
```

Creates `docs/op-notes/op-<feature-slug>.md` from template with all required sections.

### Reconcile Specs

```
/prepare-release reconcile <feature-id>
```

Compares Feature Spec vs actual implementation and updates divergent docs.

## Stage Details

### Stage I: Spec Reconciliation

**Purpose**: Ensure documentation matches implementation before release.

**Tasks**:
1. Compare Feature Spec API Design with actual implementation
2. Update any divergent signatures or behaviors
3. Review SPEC documents for accuracy
4. Update ADRs if decisions changed during implementation
5. Document any deviations discovered

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

## Best Practices

1. **Never deploy without OP-NOTE**: Gate production deployments
2. **Keep runbooks actionable**: Symptom → Diagnose → Remediate
3. **Test rollback procedures**: Don't assume they work
4. **Update indices promptly**: Don't let documentation lag
5. **Reconcile specs honestly**: Document what was actually built

## Validation

- `scripts/validate_opnote.py` — Validate OP-NOTE completeness
- `scripts/reconcile_specs.py` — Check spec reconciliation status

## References

See `assets/`:
- `opnote-template.md` — OP-NOTE template

## Manifest Update

After completing each stage, update `docs/workflow-state.yaml`:

**Stage I (Reconcile):**
- Set `stage: I`

**Stage J (OP-NOTE):**
- Set `stage: J`
- Set `docs.opnote: docs/op-notes/op-<slug>.md`

**Checkpoint #5 (after Stage J):**
- Set `checkpoint: 5` after passing validation
- Criteria: OP-NOTE exists with all required sections, spec reconciliation complete

**Stage K (Deploy):**
- Set `stage: K`

**Stage L (Close):**
- Set `stage: L`

**Checkpoint #6 (after Stage L):**
- Set `checkpoint: 6` after passing validation
- Criteria: Deployment verified, indices updated, git tag created

To advance to the next stage: `/manage-work advance <ID>`
To check readiness: `/validate-checkpoint 5` (after OP-NOTE) or `/validate-checkpoint 6` (after deploy)
