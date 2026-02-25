---
paths:
  - "docs/**"
---

# Document Standards

When creating or editing documents in `docs/`, follow these format requirements by document type.

## PRD (`docs/prds/prd.md`)

- Must include measurable success metrics
- Must define user stories or job-to-be-done
- Must specify scope boundaries (what's in/out)

## Discovery (`docs/discovery/disco-*.md`)

- Must map existing code structure and dependencies
- Must identify integration points and constraints
- Must flag risks or unknowns for later ADRs

## Tech Specs (`docs/specs/spec-*.md`)

- Must include architecture diagrams or descriptions
- Must specify interfaces and data flow
- Must reference relevant ADRs for design choices

## ADRs (`docs/adrs/adr-*-*.md`)

- Must follow Status / Context / Decision / Consequences structure
- Must list alternatives considered with trade-offs
- Must link to the tech spec or feature spec that motivated the decision

## Feature Specs (`docs/features/ft-*-*.md`)

- Must include acceptance criteria (testable conditions)
- Must define API contracts if applicable
- Must specify error handling and edge cases

## OP-NOTEs (`docs/op-notes/op-*.md`)

- Must include step-by-step deployment runbook
- Must define rollback procedures
- Must list monitoring and alerting checks
