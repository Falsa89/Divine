# v106 — Staging Apply Readiness Gate

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_staging_apply_readiness_gate_v1.json`

## Gate Status

**`NOT_PASSED_APPLY_GATED_NOT_EXECUTED`** (default Emergent run).

## Criteri (12)

| Criterion | Required | Current |
|---|---|---|
| backup_present | ✅ | ❌ (verrà creato pre-apply) |
| backup_manifest_sha256_verified | ✅ | ❌ |
| dry_run_pass | ✅ | ✅ (160 profili) |
| collection_counts_documented | ✅ | ✅ |
| index_plan_reviewed | ✅ | ✅ (5 indici) |
| rollback_script_present | ✅ | ✅ |
| db_target_staging_only | ✅ | n/a (no apply) |
| no_production_env_targeted | ✅ | ✅ |
| user_explicit_approval | ✅ | ❌ (flag mancante) |
| monitoring_plan | ✅ | ✅ |
| post_apply_smoke_plan | ✅ | ✅ |
| abort_conditions_documented | ✅ | ✅ |

## Abort conditions

- target db == production
- backup manifest SHA256 mismatch
- dry-run profile_count_estimate diverge >5% da pre-flight
- any flag missing
- premium currency grant detected
- legacy cleanup apply detected
- reward grant detected

## Monitoring plan

- Profili creati / per server / per archetype.
- Error rate post-apply loaders.
- Chat duplication test S1 vs S2.
- Arena leaderboard scoping smoke.

## Post-apply smoke plan

1. `GET /api/server-profiles/current` (gated).
2. `GET /api/user/heroes?server_id=s1` returns scoped roster.
3. Banner `SERVER_DATA_ISOLATION_BACKEND_PENDING` removed quando flag enabled.
