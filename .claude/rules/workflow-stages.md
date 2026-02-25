# Workflow Stages & Tracks

## Stage Summary

See `README.md` for the full pipeline diagram.

- **Stages A-D** (Planning): PRD, Discovery, Tech Specs, ADRs
- **Stage E** (Design): Feature Spec with API Design
- **Stages F-H** (Implementation): TDD cycle — RED, GREEN, REFACTOR
- **Stages I-L** (Release): Reconcile, OP-NOTE, Deploy, Close — **optional**
- **DONE**: Terminal state after Checkpoint #4 (can close without release)

Six checkpoints gate progression between phases.

## Tracks

| Track | Start | End | Planning | Release |
|-------|-------|-----|----------|---------|
| Micro | F | G → DONE | None | No |
| Small | E | H → DONE or I-L | Feature spec | Optional |
| Medium | B | H → DONE or I-L | Full planning | Optional |
| Large | A | H → DONE or I-L | Full + PRD | Optional |
