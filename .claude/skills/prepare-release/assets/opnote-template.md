# OP-NOTE Template

## Overview

OP-NOTEs (Operator Notes) document everything needed to deploy and operate a feature or release. They serve as runbooks for deployment and incident response.

## Naming Convention

Choose one naming pattern:
- **Per feature**: `op-<FEATURE-ID>-<slug>.md` (e.g., `op-ft-001-hover-badge.md`)
- **Per release**: `op-release-<semver>.md` (e.g., `op-release-1.3.0.md`)

## Location

All OP-NOTEs go in: `docs/op-notes/`

Maintain an index at: `docs/op-notes/index.md`

---

## Template

```markdown
# OP-NOTE — [Feature Name / Release Version]

**File:** docs/op-notes/op-[id]-[slug].md
**Date:** YYYY-MM-DD
**Author:** [Name]
**Features:** [List of feature spec files covered]

## Summary

[1-2 sentences describing what this deployment changes]

---

## Preflight

### Prerequisites
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

### Approvals Required
- [ ] [Approval type] from [Role/Person]

### Migrations
| Migration | Status | Notes |
|-----------|--------|-------|
| `YYYYMMDD_migration_name.sql` | Pending | [Description] |

### Feature Flags
| Flag | Initial Value | Final Value | Notes |
|------|---------------|-------------|-------|
| `feature.name` | `false` | `true` | Enable after verification |

### Environment Variables
| Variable | Value | Environment | Notes |
|----------|-------|-------------|-------|
| `VAR_NAME` | `value` | Production | [Purpose] |

> **Note:** Never include secrets in OP-NOTEs. Reference secret management system.

---

## Deploy Steps

### Pre-Deployment
1. [ ] Verify all preflight items complete
2. [ ] Notify on-call: [channel/person]
3. [ ] Open monitoring dashboards

### Deployment
1. [ ] [Step 1 with exact command]
   ```bash
   # Example: Build and push
   docker build -t app:version .
   docker push registry/app:version
   ```
   **Verify:** [How to verify this step succeeded]

2. [ ] [Step 2 with exact command]
   ```bash
   # Example: Deploy
   kubectl set image deployment/app container=app:version
   ```
   **Verify:** [How to verify this step succeeded]

3. [ ] [Step 3...]

### Post-Deployment Verification
1. [ ] Health check: `curl https://app/healthz` returns 200
2. [ ] [Additional verification steps]

---

## Monitoring

### Dashboards
| Dashboard | URL | What to Watch |
|-----------|-----|---------------|
| [Name] | [URL] | [Key metrics] |

### Alerts
| Alert | Threshold | Response |
|-------|-----------|----------|
| [Alert name] | [Condition] | [Action to take] |

### SLOs/SLIs
| Metric | Target | Current |
|--------|--------|---------|
| Availability | 99.9% | [Current] |
| Latency p95 | <400ms | [Current] |
| Error Rate | <0.1% | [Current] |

---

## Runbook

### Symptom: [Problem description]

**Diagnose:**
1. Check [what to check]
2. Look for [indicators]
3. Verify [conditions]

**Remediate:**
1. If [condition A]: [Action A]
2. If [condition B]: [Action B]
3. If unclear: Escalate to [team/person]

### Symptom: [Another problem]

**Diagnose:**
[Steps...]

**Remediate:**
[Steps...]

---

## Rollback

### When to Rollback
- [ ] Error rate exceeds [threshold]
- [ ] Latency exceeds [threshold]
- [ ] [Critical functionality] fails
- [ ] [Other conditions]

### Rollback Steps
1. [ ] [Step 1 - exact command]
   ```bash
   # Example: Rollback deployment
   kubectl rollout undo deployment/app
   ```

2. [ ] [Step 2...]

3. [ ] Verify rollback successful:
   - [ ] [Verification 1]
   - [ ] [Verification 2]

### Data Compatibility Notes
- [Note about data migrations and rollback compatibility]
- [Any data that cannot be rolled back]

### Post-Rollback Actions
1. [ ] Notify stakeholders
2. [ ] Create incident report
3. [ ] Schedule post-mortem

---

## Post-Deploy Checks

### Smoke Tests
| Test | Command/Steps | Expected Result |
|------|---------------|-----------------|
| [Test 1] | [How to run] | [Expected output] |
| [Test 2] | [How to run] | [Expected output] |

### Canary/Gradual Rollout
| Phase | Traffic % | Duration | Success Criteria |
|-------|-----------|----------|------------------|
| 1 | 10% | 30 min | Error rate <0.1% |
| 2 | 50% | 1 hour | Error rate <0.1% |
| 3 | 100% | - | Error rate <0.1% |

### Sign-off
- [ ] Smoke tests passing
- [ ] Metrics within SLO
- [ ] No unexpected errors in logs
- [ ] Feature functioning as expected

**Deployed By:** [Name]
**Deployed At:** [Timestamp]
**On-Call:** [Name/Team]

---

## Related Documents

- Feature Spec: [Link to feature spec]
- ADR: [Link to relevant ADRs]
- SPEC: [Link to relevant SPECs]
- Previous OP-NOTE: [Link if applicable]
```

---

## Required Sections Checklist

Every OP-NOTE must include:

- [ ] **Header**: File path, date, author, features covered
- [ ] **Preflight**: Prerequisites, approvals, migrations, flags, env vars
- [ ] **Deploy Steps**: Ordered commands with verification for each
- [ ] **Monitoring**: Dashboards, alerts, SLOs/SLIs
- [ ] **Runbook**: At least one symptom → diagnose → remediate
- [ ] **Rollback**: When to rollback, exact steps, data notes
- [ ] **Post-Deploy Checks**: Smoke tests, sign-off

## Best Practices

1. **Be specific**: Include exact commands, not "deploy the app"
2. **Include verification**: Every step should have a way to verify success
3. **No secrets**: Reference secret management, never inline credentials
4. **Test rollback**: Actually verify rollback works before deployment
5. **Keep updated**: Update OP-NOTE if deployment process changes
6. **Link related docs**: Connect to feature specs, ADRs, SPECs

## Gate

**No production deployment is allowed without a validated OP-NOTE covering the change.**
