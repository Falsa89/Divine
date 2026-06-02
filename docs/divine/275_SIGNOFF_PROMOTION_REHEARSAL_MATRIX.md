# 275 — SIGNOFF_PROMOTION_REHEARSAL_MATRIX (v46 Track B)

## Sintesi
Matrice design-only per la rehearsal di **promotion del signoff** sulle 8 famiglie.
Nessuna promotion live viene eseguita: `actual_promotion_performed=false`.

## States definiti
`pending` → `dry_run_ready` → `qa_ready` → `canary_rehearsal_ready` → `live_ready_blocked`

## Stato per ogni famiglia (v46)
- `current_state=pending`
- `target_state_after_rehearsal=dry_run_ready`
- `actual_promotion_performed=false`
- `canary_enabled=false`, `live_enabled=false`, `live_flip_allowed=false`, `db_writes=0`
- `owner_signoff=pending`, `qa_signoff=pending`, `game_director_signoff=pending`

## Evidence checklist obbligatoria per ogni famiglia
- `validators_passing`, `suite_zero_required_fail`, `md5_invariants_intact`,
  `default_503_with_flag_off`, `dry_run_smoke_passed`,
  `replay_conflict_detection_dry_run`, `alert_thresholds_dry_run`,
  `rollback_runbook_present`

## Famiglie speciali
- `battle_pass_reward_claim`: `no_bp_delta_runtime=true`
- `mail_reward_claim`: `no_mail_state/delete/read_mutation=true`
