# 434 — Alpha Internal QA Bug Backlog + Triage

**Pack:** `MEGA_RELEASE_ACCELERATION_21_v72`

## File
- `data/design/qa/alpha_internal_qa_bug_backlog_v1.json`
- `data/design/qa/alpha_internal_qa_bug_triage_matrix_v1.json`
- `data/design/qa/alpha_internal_qa_no_fix_or_fix_decision_log_v1.json`

## Findings
- BUG-V72-001 (P3, alpha-preview-hub): copy polish 'DEEPLINK-ONLY (disabled)' → deferred.
- BUG-V72-002 (P3, first-session-onboarding-preview): state machine label line-height su 360px → deferred.
- BUG-V72-003 (P3, alpha-preview-hub): ordinamento entries per QA priority → deferred.

## Triage
- P0 open: 0
- P1 open: 0
- P2 open: 0
- P3 open: 3 (tutti deferred a batch polish dedicato)

## Decision log
- `applied_fixes_count=0`, `deferred_fixes_count=3`, `no_fix_needed=false`, `all_fixes_preview_only=true`.
- Default no fix v72: nessun fix codice applicato.
