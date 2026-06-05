# Final Report — MEGA_RELEASE_ACCELERATION_55_v106

## Verdict

```
MEGA_RELEASE_ACCELERATION_55_SERVER_SCOPED_DB_SCHEMA_AND_PLAYER_SERVER_PROFILES_GATED_MIGRATION_PREP_DRY_RUN_READY_APPLY_GATED_NOT_EXECUTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Pack di fondazione P0 completato in default mode. **0 DB writes**, **0 mutazioni runtime**. Schema `player_server_profiles` definito, scripts backup/dry-run/apply/rollback gated creati, dry-run eseguito con successo (160 account inspecionati).

## Commit hash

(local container — public sync pending)

## Suite result

```
Overall: FAIL  (pass=1074, fail=23, miss=0)
REQUIRED FAIL = 0
MISS = 0
OPTIONAL FAIL = 23 (target ≤ 30)
v106 tuples: 11/11 PASS
v105 / v104 / v103: PASS (nessuna regressione)
```

## Files created / modified

### Modified (1)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (11 tuple v106 + sentinel `PUBLIC_SYNC_TAG_v106_MEGA_RELEASE_ACCELERATION_55_SERVER_SCOPED_DB_SCHEMA_AND_PLAYER_SERVER_PROFILES_GATED_MIGRATION_PREP`)

### Created (10 JSON design)
- `data/design/server_scope/v106_existing_data_model_audit_v1.json`
- `data/design/server_scope/player_server_profiles_schema_v1.json`
- `data/design/server_scope/v106_account_global_vs_server_scoped_matrix_v1.json`
- `data/design/server_scope/v106_backup_manifest_v1.json`
- `data/design/server_scope/v106_dry_run_player_server_profiles_result_v1.json`
- `data/design/server_scope/v106_apply_result_v1.json`
- `data/design/server_scope/v106_rollback_plan_v1.json`
- `data/design/server_scope/v106_server_scoped_read_contract_v1.json`
- `data/design/server_scope/v106_bot_server_actor_migration_policy_v1.json`
- `data/design/server_scope/v106_staging_apply_readiness_gate_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_55_v106_rollup_marker_v1.json`

### Created (4 scripts)
- `backend/scripts/backup_v106_player_server_profiles_pre_migration.py`
- `backend/scripts/dry_run_v106_player_server_profiles_migration.py`
- `backend/scripts/apply_v106_player_server_profiles_migration.py`
- `backend/scripts/rollback_v106_player_server_profiles_migration.py`

### Created (11 validators)
- `backend/scripts/validate_v106_*.py` (10 sub) + `validate_mega_release_acceleration_55_v106_rollup.py`

### Created (7 docs)
- `docs/divine/106_EXISTING_DATA_MODEL_AUDIT.md`
- `docs/divine/106_PLAYER_SERVER_PROFILES_SCHEMA.md`
- `docs/divine/106_ACCOUNT_GLOBAL_VS_SERVER_SCOPED_MATRIX.md`
- `docs/divine/106_DRY_RUN_PLAYER_SERVER_PROFILES_MIGRATION.md`
- `docs/divine/106_ROLLBACK_PLAYER_SERVER_PROFILES.md`
- `docs/divine/106_SERVER_SCOPED_READ_CONTRACT.md`
- `docs/divine/106_STAGING_APPLY_READINESS_GATE.md`
- `docs/divine/106_FINAL_REPORT.md`

## Existing data model audit summary

17 collection. 8 → PSP. 3 account-global. 5 mixed/split. 1 chat separate. 3 critical risk (arena_mmr, guild, chat). 6 high risk.

## player_server_profiles schema summary

- Collection: `player_server_profiles`
- PK composta unica: `(account_id, server_id)`
- profile_id: `<account_id>:<server_id>`
- 5 indici (1 unique compound, 4 secondari)
- Forbidden fields: `password_hash`, `oauth_access_token`, `oauth_refresh_token`, `provider_client_secret`, `raw_iap_receipt_token`, `raw_payment_method`
- Starter safety: no premium currency, no random heroes, no legacy heroes, no reward grant

## Account-global vs server-scoped matrix

10 account-global · 14 server-scoped · 8 mixed (con recommended esplicito per ognuno).

## Backup manifest

**Status**: `BACKUP_NOT_EXECUTED_DRY_RUN_DEFAULT`. Manifest template documentato (backup_id, generated_at_utc, files con SHA256, masked secrets). 17 collection pianificate. Format: jsonl.gz per collection. Masking rules: password_hash, oauth tokens, provider secrets, iap receipts.

## Dry-run migration result

- **DB inspected**: YES (`divine_waifus`)
- **DB writes**: 0
- **Estimated profiles**: **160** (accounts → server_id=`s1`)
- **default_server_id**: `s1`
- Migration plan summary: users restano global, soft currencies in psp, hard currencies global, chat collection separata.

## Apply status

**`APPLY_SKIPPED_GATED`** (default). Script ha rifiutato l'esecuzione perché nessuno dei 4 flag richiesti era set. 0 db writes, 0 collections created, 0 indexes, 0 profiles backfilled, 0 original collections deleted. premium_currency_granted=false, reward_granted=false, legacy_cleanup_applied=false.

## Rollback status

**`ROLLBACK_NOT_EXECUTED_PLAN_DOCUMENTED`**. Script ha rifiutato senza i 2 flag rollback. 2 strategie documentate (reverse_via_backup_restore preferita + soft_disable_psp_only fallback).

## Read contract summary

11 endpoint contract_only per v107/v108/v109. Validation rules definite. Fallback when flag disabled mantiene banner `SERVER_DATA_ISOLATION_BACKEND_PENDING`.

## Bot/server actor migration policy

- 5 archetipi approvati (`f2p_base`, `f2p_active`, `advanced_pull_bot`, `spender_like_controlled`, `whale_like_limited`).
- Invariants: start_level=1, credible_progression, roster_min_size=3, event_access parità player.
- Forbidden: empty roster, legacy hero in bot, premium grant, random hero assignment, day-1 lv100, top ranking seed.

## Staging apply readiness gate

**`NOT_PASSED_APPLY_GATED_NOT_EXECUTED`**. 12 criteria · dry_run_pass=✅ · rollback_script_present=✅ · user_explicit_approval=❌ (mancante per design v106 default). 7 abort conditions + monitoring plan + post-apply smoke plan documentati.

## Safety flags

```
production_db_writes                   = false  ✅
destructive_migration                  = false  ✅
original_user_data_deleted             = false  ✅
legacy_cleanup_applied                 = false  ✅
reward_grant                           = false  ✅
premium_currency_grant                 = false  ✅
gacha_shop_vip_bp_mutation             = false  ✅
battle_engine_runtime_changes          = false  ✅
combat_tsx_changes                     = false  ✅
new_player_facing_feature              = false  ✅
fake_PASS                              = false  ✅
validator_weakening                    = false  ✅
hiding_optional_fails                  = false  ✅ (23 OPTIONAL FAIL espliciti)
claiming_backend_isolation_live        = false  ✅ (apply non eseguito)
commercial_release_claim               = false  ✅
```

## Remaining blockers

1. **Apply staging non eseguito** — richiede 4 env flag espliciti + backup eseguito (per design v106 default).
2. **Loader backend non leggono ancora `server_id`** — implementazione adoption è lavoro di **v107**.
3. **Chat surface non scopata** — lavoro **v109**.
4. **Currency split soft/hard** — decisione esplicita finalizzata in roadmap; implementazione **v107**.
5. **battle_pass / gacha_history / shop_purchases** — design decision recommended, da finalizzare prima di v110.

## Next recommended pack

**v107 — Battle Launch Contract Unification + Backend Loader Server-ID Adoption**

Motivazione: con lo schema definito e la migration pronta in dry-run, v107 può introdurre:
- adoption del query param `server_id` su 6 endpoint chiave (`/api/user/heroes`, `/api/team/get-formation`, `/api/inventory`, `/api/currencies`, `/api/story/progress`, `/api/server-profiles/current`) con feature flag `server_scoped_runtime_enabled` (default false);
- schema `launch_context` v1 enforced in `combat.tsx`;
- `pre-battle-lobby` produce payload conforme;
- `/api/battle/launch` authoritative + idempotente.

Entrambe le tracce sono complementari: backend adoption sblocca isolation reale appena lo staging apply sarà autorizzato; battle launch contract sblocca la conversione runtime di story/tower/arena (v108).
