#!/usr/bin/env bash
# Stop hook: Batch-validate all changed doc files at end of turn.
# Replaces per-edit PostToolUse validation with one consolidated pass.
#
# Scans git status for changed doc files, runs the matching validation
# script for each, and outputs a consolidated report.
#
# Input: JSON on stdin with stop_reason (ignored)
# Output: Plain text feedback (non-blocking)

set -euo pipefail

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$PROJECT_ROOT" ]; then exit 0; fi

SCRIPTS_DIR="$PROJECT_ROOT/.claude/skills/vibeflow-validate/scripts"

# Collect all changed files (modified + staged + untracked)
CHANGED=$(cd "$PROJECT_ROOT" && git status --porcelain 2>/dev/null | awk '{print $NF}')
if [ -z "$CHANGED" ]; then exit 0; fi

REPORT=""
for FILE in $CHANGED; do
  case "$FILE" in
    docs/prds/prd*.md)          SCRIPT="check_planning.py"; DOC_TYPE="PRD" ;;
    docs/discovery/disco-*.md)  SCRIPT="check_planning.py"; DOC_TYPE="Discovery" ;;
    docs/specs/spec-*.md)       SCRIPT="check_planning.py"; DOC_TYPE="Tech Spec" ;;
    docs/adrs/adr-*.md)         SCRIPT="check_planning.py"; DOC_TYPE="ADR" ;;
    docs/features/ft-*.md)      SCRIPT="check_design.py";   DOC_TYPE="Feature Spec" ;;
    docs/op-notes/op-*.md)      SCRIPT="check_release.py";  DOC_TYPE="OP-NOTE" ;;
    *) continue ;;
  esac

  SCRIPT_PATH="$SCRIPTS_DIR/$SCRIPT"
  if [ ! -f "$SCRIPT_PATH" ]; then continue; fi

  RESULT=$(python3 "$SCRIPT_PATH" --json --project-root "$PROJECT_ROOT" 2>/dev/null || echo "")
  if [ -z "$RESULT" ]; then continue; fi

  SUMMARY=$(echo "$RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    issues = len(data.get('issues', []))
    warnings = len(data.get('warnings', []))
    doc_type = '$DOC_TYPE'
    if issues == 0 and warnings == 0:
        print(f'  {doc_type}: PASS')
    elif issues == 0:
        print(f'  {doc_type}: PASS ({warnings} warnings)')
    else:
        print(f'  {doc_type}: {issues} issues, {warnings} warnings')
except:
    pass
" 2>/dev/null || echo "")

  if [ -n "$SUMMARY" ]; then
    REPORT="${REPORT}${SUMMARY}\n"
  fi
done

if [ -n "$REPORT" ]; then
  echo "[VibeFlow] Doc validation:"
  echo -e "$REPORT"
fi

exit 0
