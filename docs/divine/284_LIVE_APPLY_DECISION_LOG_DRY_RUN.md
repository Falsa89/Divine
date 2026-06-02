# 284 — LIVE_APPLY_DECISION_LOG_DRY_RUN (v48 Track C)

## Sintesi
Schema design-only per il futuro registro decisionale di live apply. **Nessuna**
decisione persistita oggi; ogni futura decisione live richiede approvazione
manuale utente.

## Stato
- `schema_only=true`, `actual_decisions_persisted=false`
- `future_live_decision_requires_manual_user_approval=true`
- `canary_allowed=false`, `live_allowed=false`, `db_writes=0`

## Schema entry richiesto
- required_fields: operation_family, timestamp_preview, decision, approver, rationale, evidence_refs, rollback_plan_ref
- decision_enum: no_go_signoff_pending / no_go_blockers_open / go_canary_rehearsal_only_dry_run / go_canary_live_BLOCKED_REQUIRES_MANUAL_USER_APPROVAL / go_live_BLOCKED_REQUIRES_MANUAL_USER_APPROVAL
- approver_enum: system_dry_run / owner_pending / qa_pending / game_director_pending
- evidence_refs_must_include: validator_pass_list, md5_invariants_proof, default_503_proof, db_writes_zero_proof, alert_dispatched_false_proof, persisted_false_proof

## Entries (8/8)
Ogni famiglia: `current_decision=no_go_signoff_pending`, `approver=system_dry_run`, `requires_manual_user_approval=true`.
