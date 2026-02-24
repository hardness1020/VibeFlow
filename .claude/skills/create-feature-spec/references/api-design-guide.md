# API Design Guide

How to write the API Design section of a Feature Spec.

## Why API Design Matters

The API Design section is **the contract** between:
- **Stage E (Design)** → Defines what will be built
- **Stage F (RED)** → Creates stubs and tests from these signatures
- **Stage G (GREEN)** → Implements to match these signatures

If signatures change during implementation, you must follow Stage G.1 protocol:
1. STOP implementation
2. Update SPEC
3. Update Feature Spec API Design
4. Update tests
5. Resume implementation

## Function/Method Signatures

### Format

```markdown
### ServiceName.method_name()

- **Signature:** `method_name(param1: Type, param2: Type = default) -> ReturnType`
- **Purpose:** [One sentence describing what it does]
- **Parameters:**
  - `param1`: [Type] - [Description, constraints]
  - `param2`: [Type, optional, default=X] - [Description]
- **Returns:** `ReturnType` - [Description of structure]
- **Raises:** (if applicable)
  - `ErrorType`: [When/why raised]
```

### Example (Python)

```markdown
### BulletVerificationService.verify_bullet_set()

- **Signature:** `verify_bullet_set(bullets: List[BulletPoint], sources: List[Artifact], confidence_threshold: float = 0.8) -> VerificationResult`
- **Purpose:** Verify generated bullets against source artifacts for factual accuracy
- **Parameters:**
  - `bullets`: List[BulletPoint] - Bullets to verify
  - `sources`: List[Artifact] - Source artifacts for verification
  - `confidence_threshold`: float, default=0.8 - Minimum confidence for passing
- **Returns:** `VerificationResult` with:
  - `passed`: bool - Overall verification status
  - `bullet_results`: List[BulletVerification] - Per-bullet results
  - `overall_confidence`: float - Average confidence (0.0-1.0)
- **Raises:**
  - `InsufficientSourcesError`: When sources list is empty
  - `VerificationTimeoutError`: When LLM call exceeds timeout
```

### Example (TypeScript)

```markdown
### useCredibilityScore()

- **Signature:** `useCredibilityScore(artifactId: string, options?: ScoreOptions) => UseCredibilityScoreResult`
- **Purpose:** React hook for fetching and caching credibility scores
- **Parameters:**
  - `artifactId`: string - ID of artifact to score
  - `options`: ScoreOptions (optional)
    - `refetchInterval`: number - Auto-refetch interval in ms
    - `enabled`: boolean - Whether to fetch (default: true)
- **Returns:** `UseCredibilityScoreResult`
  - `data`: CredibilityScore | undefined
  - `isLoading`: boolean
  - `error`: Error | null
  - `refetch`: () => Promise<void>
```

## API Endpoint Signatures

### Format

```markdown
### API Endpoint: [METHOD] /api/v1/[path]

- **Method:** POST | GET | PUT | DELETE | PATCH
- **Path:** `/api/v1/[resource]/[subpath]`
- **Authentication:** Required | Optional | None
- **Rate Limit:** [X] requests per [period] (if applicable)
- **Request Body:** (for POST/PUT/PATCH)
  ```json
  {
    "field1": "type (required)",
    "field2": "type (optional, default: X)"
  }
  ```
- **Query Parameters:** (for GET)
  - `param1`: [type] - [Description] (required/optional)
- **Response Body:**
  ```json
  {
    "field1": "type",
    "field2": "type"
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: [Condition]
  - `401 Unauthorized`: [Condition]
  - `404 Not Found`: [Condition]
  - `429 Too Many Requests`: [Condition]
  - `500 Internal Server Error`: [Condition]
```

### Example

```markdown
### API Endpoint: POST /api/v1/bullets/{bullet_id}/verify

- **Method:** POST
- **Path:** `/api/v1/bullets/{bullet_id}/verify`
- **Authentication:** Required (JWT)
- **Path Parameters:**
  - `bullet_id`: int - ID of bullet to verify
- **Request Body:**
  ```json
  {
    "artifact_ids": [1, 2, 3],
    "confidence_threshold": 0.8
  }
  ```
- **Response Body:**
  ```json
  {
    "verified": true,
    "confidence": 0.92,
    "sources": [
      {
        "artifact_id": 1,
        "match_type": "exact",
        "excerpt": "..."
      }
    ]
  }
  ```
- **Error Responses:**
  - `400`: Invalid bullet_id or empty artifact_ids
  - `404`: Bullet not found
  - `422`: Confidence threshold out of range (0-1)
```

## Data Type Definitions

When return types or parameters are complex, define them:

```markdown
### Data Types

**VerificationResult:**
```python
@dataclass
class VerificationResult:
    passed: bool                          # Overall pass/fail
    bullet_results: List[BulletVerification]  # Per-bullet results
    overall_confidence: float              # Average confidence 0.0-1.0
    verification_time_ms: int              # Processing time
```

**BulletVerification:**
```python
@dataclass
class BulletVerification:
    bullet_id: int
    verified: bool
    confidence: float
    source_matches: List[SourceMatch]
    issues: List[str]  # Empty if verified
```
```

## Best Practices

### DO

✅ Use exact names that will appear in code
✅ Specify all parameter types
✅ Document optional parameters with defaults
✅ Describe return type structure
✅ List all error conditions
✅ Use language-appropriate type annotations

### DON'T

❌ Use placeholder names like `doSomething()`
❌ Leave out parameter types
❌ Omit return type structure
❌ Forget error cases
❌ Include implementation logic

## Converting API Design to Stubs (Stage F)

The API Design section directly becomes implementation stubs:

**From API Design:**
```markdown
### BulletVerificationService.verify_bullet_set()
- **Signature:** `verify_bullet_set(bullets: List[BulletPoint], sources: List[Artifact]) -> VerificationResult`
```

**To Stub (Stage F):**
```python
class BulletVerificationService:
    """Verify generated bullets against source artifacts."""

    def verify_bullet_set(
        self,
        bullets: List[BulletPoint],
        sources: List[Artifact]
    ) -> VerificationResult:
        """
        Verify bullet set against sources.

        Implementation for ft-030: Anti-hallucination verification.
        """
        raise NotImplementedError(
            "BulletVerificationService.verify_bullet_set not implemented. "
            "See docs/features/ft-030-anti-hallucination.md for requirements."
        )
```

## Checklist

Before completing API Design section:

- [ ] All public methods/functions documented
- [ ] All API endpoints documented
- [ ] Parameter types specified
- [ ] Return types specified with structure
- [ ] Error conditions documented
- [ ] Complex types defined
- [ ] Names match intended implementation
