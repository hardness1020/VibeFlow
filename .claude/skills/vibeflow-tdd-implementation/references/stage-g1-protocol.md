# Stage G.1: Design Changes Protocol

How to handle contract changes discovered during implementation.

## When to Trigger G.1

### STOP Immediately For:

| Change Type | Example |
|-------------|---------|
| API signatures | Function params/return type changed |
| Database schema | New table/column exposed to API |
| Event formats | Message structure changed |
| New dependencies | Adding Redis, Kafka, new library |
| SLO changes | Latency target changed |

### Continue Without G.1:

| Change Type | Example |
|-------------|---------|
| Algorithm change | Different sorting approach |
| Error handling | Better error messages (within taxonomy) |
| Private functions | Internal helper renamed |
| Performance opt | Caching (within SLO) |

## The Protocol

```
┌─────────────────────────────────────────────────────────┐
│  1. STOP implementation immediately                      │
│     - Do not write more code                            │
│     - Commit current work as WIP                        │
│     - Document discovered issue                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. UPDATE SPEC first                                    │
│     - Document new contract in affected SPEC            │
│     - Increment SPEC version                            │
│     - Update architecture diagram if topology changed   │
│     - Link to ADR if new dependency/framework           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. CREATE/UPDATE ADR if needed                          │
│     - Non-trivial decisions require ADR                 │
│     - Document why change is necessary                  │
│     - Mark as "Accepted" before proceeding              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. UPDATE Feature Spec                                  │
│     - Update API Design section                         │
│     - Update affected signatures                        │
│     - Document change rationale                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. UPDATE tests (return to Stage F)                     │
│     - Update tests to reflect new contract              │
│     - Tests should be back to RED                       │
│     - Update stub implementations                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. RESUME implementation (Stage G)                      │
│     - Implement to pass updated tests                   │
│     - Follow new contract from updated SPEC             │
│     - Reference SPEC version in code comments           │
└─────────────────────────────────────────────────────────┘
```

## Decision Matrix

| Change Type | Example | STOP? | Update Order |
|-------------|---------|-------|--------------|
| API signature | Function params changed | YES | SPEC → Feature → Tests → Code |
| Database schema | New column exposed to API | YES | SPEC → Migration → Tests → Code |
| Event format | Message structure changed | YES | SPEC → ADR → Tests → Code |
| New dependency | Adding Redis | YES | ADR → SPEC → Tests → Code |
| SLO change | Latency target changed | YES | SPEC → Tests → Code |
| Algorithm change | Different sorting | NO | Continue → Stage I reconciliation |
| Error handling | Better messages | NO | Continue → Stage I reconciliation |
| Private function | Internal renamed | NO | Code only |

## Examples

### Example 1: Function Signature Change

**Discovery:** During implementation, realize a parameter needs different type.

**Original (Feature Spec):**
```python
def verify_bullets(bullets: List[str], sources: List[str]) -> bool:
```

**Needed:**
```python
def verify_bullets(bullets: List[BulletPoint], sources: List[Artifact]) -> VerificationResult:
```

**Actions:**
1. STOP - Don't implement with new signature
2. Update `spec-api.md`:
   - Change return type documentation
   - Increment version (e.g., v2.3.0 → v2.4.0)
3. Update Feature Spec API Design section
4. Update tests to expect new types
5. Update stubs with new signature
6. Resume implementation

### Example 2: New External Dependency

**Discovery:** Need Redis for caching during verification.

**Actions:**
1. STOP - Don't add Redis without ADR
2. Create ADR:
   - Context: Verification latency too high without cache
   - Decision: Add Redis for verification result caching
   - Consequences: +performance, -complexity
3. Update `spec-system.md`:
   - Add Redis to topology diagram
   - Add to component inventory
   - Increment version
4. Update Feature Spec with Redis integration details
5. Resume implementation

### Example 3: Database Schema Change

**Discovery:** Need new column on existing table.

**Actions:**
1. STOP
2. Update `spec-database-schema.md`:
   - Add column to table definition
   - Document migration
   - Increment version
3. Create migration file
4. Update tests for new schema
5. Resume implementation

## Allowed Without G.1

These changes can continue without stopping:

**Internal Algorithm:**
```python
# Original
def _calculate_score(self, items):
    return sum(items) / len(items)

# Changed to (internal optimization)
def _calculate_score(self, items):
    return statistics.mean(items)  # Same contract, different implementation
```

**Private Helper:**
```python
# Original
def _helper_method(self):
    ...

# Renamed (internal only)
def _improved_helper(self):
    ...
```

**Error Messages (within taxonomy):**
```python
# Original
raise ValidationError("Invalid input")

# Improved (same error type)
raise ValidationError("Invalid input: expected list, got string")
```

## Documentation

When triggering G.1, document:

1. **In commit message:**
   ```
   WIP: Pause implementation for contract change

   Discovered need to change return type of verify_bullets().
   Following Stage G.1 protocol.
   ```

2. **In Feature Spec (add note):**
   ```markdown
   ## Design Changes (G.1 Update)

   **Date:** 2025-11-10
   **Reason:** Original return type insufficient
   **Change:** VerificationResult replaces bool return
   **SPEC Updated:** spec-api.md v2.3.0 → v2.4.0
   ```

3. **In ADR (if created):**
   Link from Feature Spec and SPEC.

## Benefits

- Maintains docs-first discipline
- Clear decision trail
- Tests reflect current contract
- No divergence between docs and implementation
