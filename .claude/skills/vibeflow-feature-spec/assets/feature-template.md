# Feature — <ID> <slug>

**File:** docs/features/ft-<ID>-<slug>.md
**Owner:** [Name]
**TECH-SPECs:** `spec-[name].md` (vX.Y), `spec-[name].md` (vX.Y)

---

## Stage B Discovery Findings

> Required for Medium/Large features. Reference: `docs/discovery/disco-<ID>.md`

### Test Impact Analysis

**Tests to Update:**
- `[path/to/test_file.py]` - [Reason for update]

**Tests to Remove:**
- None | `[path/to/test_file.py]` - [Reason]

**Coverage Gaps:**
- [Component/path] (coverage: X%) - [Why gap matters]

**Test Update Checklist:**
- [ ] Update `test_[name].py` for [change]
- [ ] Add [test type] tests for [component] (Stage F)
- [ ] Add integration tests for [component] (Stage H)

### Existing Implementation Analysis

**Similar Features:**
- `[path/to/file.py]` - [Pattern/similarity]

**Reusable Components:**
- `[path/to/component.py]` - [What to reuse]

**Patterns to Follow:**
- [Pattern name] from [location] - [How to apply]

**Code to Refactor:** None | [Description]

### Dependency & Side Effect Mapping

**Dependencies:**
- `[Component/Service]` - [How used]

**Side Effects:**
- Database: [Operations]
- Cache: [Operations]
- External API: [Calls]

**Impact Radius:**
- [Layer]: [Components affected]

**Risk Areas:**
- [Component] - [Risk level] - [Reason]

---

## Architecture Conformance

**Layer Assignment:**
- New code in `[path/to/directory/]` ([layer name])

**Pattern Compliance:**
- Follows [pattern name] ✓
- Uses [service/component] ✓

**Dependencies:**
- `[module.ClassName]` (inheritance/composition)

---

## API Design

> This section defines the contract for Stage F. Exact names, parameters, and return types become implementation stubs.

### [ServiceName].[method_name]()

- **Signature:** `method_name(param1: Type, param2: Type = default) -> ReturnType`
- **Purpose:** [What this method does]
- **Parameters:**
  - `param1`: [Type] - [Description]
  - `param2`: [Type, optional, default=X] - [Description]
- **Returns:** `ReturnType` with:
  - `field1` ([type]): [Description]
  - `field2` ([type]): [Description]
- **Raises:**
  - `ErrorType`: [When raised]

### [ServiceName].[another_method]()

- **Signature:** `another_method(param: Type) -> ReturnType`
- **Purpose:** [Description]
- **Parameters:**
  - `param`: [Description]
- **Returns:** [Description]

### API Endpoint: [METHOD] /api/v1/[path]

- **Method:** POST | GET | PUT | DELETE
- **Path:** `/api/v1/[resource]/`
- **Authentication:** Required | Optional
- **Request Body:**
  ```json
  {
    "field1": "type",
    "field2": "type (optional)"
  }
  ```
- **Response Body:**
  ```json
  {
    "field1": "type",
    "field2": "type"
  }
  ```
- **Error Responses:**
  - `400`: Invalid input - [When]
  - `404`: Not found - [When]
  - `500`: Server error - [When]

---

## Acceptance Criteria

> Must be testable. Each criterion becomes one or more tests.

- [ ] [User/System] can [action] with [condition] resulting in [outcome]
- [ ] [Component] returns [result] when [condition]
- [ ] [Component] handles [error case] gracefully with [behavior]
- [ ] [Performance]: [Operation] completes within [time] for [load]
- [ ] [Security]: [Requirement]

### Gherkin Format (Alternative)

```gherkin
Feature: [Feature name]

Scenario: [Happy path]
  Given [context]
  When [action]
  Then [expected outcome]

Scenario: [Error case]
  Given [context]
  When [invalid action]
  Then [error handling]
```

---

## Design Changes

### API Changes

- `POST /api/v1/[endpoint]` - [New/Modified] - [Description]
- Response adds `[field]` ([type]): [Description]

### Schema Changes

- `[Model].[field]` - [New/Modified] - [Type, constraints]
- Migration: `YYYYMMDD_[description].sql`

### UI Changes

- [Component] - [Description of change]
- [New component] - [Purpose]

---

## Test & Eval Plan

### Unit Tests (Stage F)

- Test [component/function] with [conditions]
- Test [error handling] for [cases]
- Mock: [external dependencies]

### Integration Tests (Stage H)

- Test [endpoint] end-to-end
- Test [database operations]
- Test [external service integration]

### AI/LLM Evaluation (if applicable)

- Goldens: [Version/location]
- Threshold: [Metric] ≥ [value]
- Eval harness: [Location/command]

---

## Telemetry & Metrics

**Events to Track:**
- `[event_name]`: [When fired, what data]

**Dashboards:**
- [Dashboard name]: [Metrics to display]

**Alerts:**
- [Condition] > [threshold]: [Action]

---

## Edge Cases & Risks

**Edge Cases:**
- [Case 1]: [Handling]
- [Case 2]: [Handling]

**Risks:**
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [Impact] | [Mitigation] |

**Fallback Behavior:**
- If [failure condition]: [Graceful degradation]

---

## References

- Discovery: `docs/discovery/disco-<ID>.md`
- Tech Specs: [Links with versions]
- ADRs: [Relevant ADRs]
