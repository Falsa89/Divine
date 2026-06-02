# 280 — ROLLBACK_RUNBOOK_REHEARSAL_MATRIX (v47 Track C)

## Sintesi
Matrice design-only del rollback runbook rehearsal per le 8 operation families.

## Scenari per famiglia (8 step ordinati)
1. `kill_switch_toggle_rehearsal` (flag OFF dry-run)
2. `verify_default_503` (HTTP 503 atteso)
3. `verify_db_writes_zero`
4. `capture_aggregation_snapshot` (v45)
5. `capture_alert_evaluation` (v46)
6. `capture_go_no_go_snapshot` (v46)
7. `owner_notification_dry_run` (NOT sent)
8. `rollback_blocked_if_live_ledger_absent`

## Stato per famiglia
- `rollback_rehearsal_state=pending`
- `live_rollback_enabled=false`
- `actual_rollback_performed=false`
- `reward_reversal_enabled=false`
- `mutation_reversal_enabled=false`
- `db_writes=0` per ogni step

## Famiglie speciali
- `battle_pass_reward_claim`: `no_bp_delta_runtime=true`
- `mail_reward_claim`: `no_mail_state_mutation=true`
