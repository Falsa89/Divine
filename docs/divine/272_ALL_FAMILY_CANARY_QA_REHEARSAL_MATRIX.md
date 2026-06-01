# 272 — ALL_FAMILY_CANARY_QA_REHEARSAL_MATRIX (v45 Track C)

## Sintesi
Matrice design-only per la rehearsal QA canary di TUTTE le 8 operation families.
Nessun runtime, nessun live flip, nessun reward grant, nessuna mutazione.
`signoff_state=pending`, `canary_enabled=false`, `canary_percentage=0`,
`live_enabled=false`, `live_flip_allowed=false`, `db_writes=0`.

## Famiglie coperte (8/8)
1. gem_socket_commit
2. material_raid_claim
3. gear_forge_fusion_commit
4. rune_scroll_talisman_commit
5. artifact_upgrade_commit
6. divine_weapon_upgrade_commit
7. battle_pass_reward_claim
8. mail_reward_claim

## Per ogni famiglia
- `kill_switch_test_plan` (trigger + expected response + verification)
- `rollback_template_execution_steps` (5 step)
- `rehearsal_scenarios` (9 scenari: happy path, duplicate same hash, duplicate diff hash, missing idempotency key, expected version mismatch, unauthorized user, feature flag disabled, simulated rollback trigger, observability alert trigger dry-run)
- `pass_fail_criteria` (db_writes=0, live_enforcement=false, reward_grant=false, mutation=false, preview_request_must_not_be_blocked=true)

## Vincoli speciali
- `battle_pass_reward_claim`: `no_bp_delta_runtime=true`
- `mail_reward_claim`: `no_mail_state_mutation=true`, `no_mail_delete_mutation=true`, `no_mail_read_mutation=true`
