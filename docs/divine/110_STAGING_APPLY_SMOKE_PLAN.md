# v110 APPLY PREFLIGHT — Staging Apply Smoke Plan

**Pack**: `MEGA_RELEASE_ACCELERATION_71_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED`
**Track**: F
**Public sync tag**: `PUBLIC_SYNC_TAG_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED`

## Ambiente

- environment: **staging** (production_db_forbidden_in_smoke=true)
- sample size: 5 users / 25 user_heroes / 5 team / 5 equipment / 5 story_progress

## 15 step previsti

1. mongodump backup staging
2. apply --dry-run
3. apply --plan-only
4. apply --limit 5
5. verify psp_count = limit
6. verify no duplicate psp
7. verify premium balance unchanged
8. verify hard balance unchanged
9. verify soft balance aggregated per user unchanged
10. verify team size unchanged (=6)
11. apply seconda volta idempotente --limit 5
12. verify psp_count invariato (idempotenza)
13. validate v109/v110 runtime invariants
14. rollback --dry-run
15. validate rollback ripristina firma pre-apply

## Risultati attesi

- psp_inserts_first_run: 5
- psp_inserts_second_run_with_same_limit: 0 (idempotente)
- db_writes_in_dry_run / plan_only: 0
- premium_balance_diff / hard_balance_diff: 0
- team_size_diff: 0
- runtime_invariants_pass: true

## Abort conditions

any_premium_balance_mismatch, any_hard_balance_mismatch, any_team_size_drift, any_duplicate_psp, any_legacy_delete, runtime_invariant_failure.

## Stato in questo pack

- smoke_executed_in_this_pack: **false**
- db_writes_in_this_pack: **0**
- production_db_smoke: **false**

Riferimento: `data/design/v110_psp_apply_preflight/v110_staging_apply_smoke_plan_v1.json`.
