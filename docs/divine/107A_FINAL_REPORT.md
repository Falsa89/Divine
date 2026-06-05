# Final Report — MEGA_RELEASE_ACCELERATION_56_v107A

## Verdict

```
MEGA_RELEASE_ACCELERATION_56_BATTLE_LAUNCH_CONTRACT_AND_SERVER_ID_LOADER_ADOPTION_FLAGGED_READY_WITH_CONTRACT_ONLY_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

P0 runtime seam pack completato. Endpoint `POST /api/battle/launch` registrato e verificato con curl (preview echo, coercion attiva). Schema Battle Launch Contract v1 definito formalmente. Helper frontend `buildLaunchContext` introdotto. Loader server_id adoption rimane contract-only (deferito a v107B).

## Commit hash

(local container — public sync pending)

## Suite result

```
Overall: FAIL  (pass=1085, fail=23, miss=0)
REQUIRED FAIL = 0
MISS = 0
OPTIONAL FAIL = 23 (target ≤ 30)
v107A tuples: 11/11 PASS
v106 / v105 / v104 / v103: PASS (nessuna regressione)
v100 MD5 baseline aggiornata (server.py supersede: 3eb3...→5af3...)
```

## Files Created / Modified

### Modified (3)
- `backend/server.py` — registra `v107a_battle_launch_router` (2 righe import + include_router)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — 11 tuple v107A + sentinel
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` — supersede server.py MD5 con historical reference

### Created (10 JSON design)
- `data/design/release_acceleration/v107a_v106_public_sync_snapshot_v1.json`
- `data/design/battle_launch/battle_launch_contract_schema_v1.json`
- `data/design/battle_launch/v107a_battle_launch_endpoint_result_v1.json`
- `data/design/battle_launch/v107a_pre_battle_lobby_contract_result_v1.json`
- `data/design/battle_launch/v107a_combat_contract_consumer_result_v1.json`
- `data/design/battle_launch/v107a_story_autoresolve_deprecation_result_v1.json`
- `data/design/battle_launch/v107a_encounter_source_adapter_contract_v1.json`
- `data/design/battle_launch/v107a_idempotency_reward_progress_guard_v1.json`
- `data/design/server_scope/v107a_backend_loader_server_id_adoption_result_v1.json`
- `data/design/server_scope/v107a_frontend_loader_server_id_propagation_result_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_56_v107a_rollup_marker_v1.json`

### Created (code)
- `backend/routes/v107a_battle_launch.py` (router `/api/battle/launch`)
- `frontend/src/battle_launch/buildLaunchContext.ts` (contract producer helper)

### Created (11 validators)
- `backend/scripts/validate_v107a_*.py` (10 sub) + rollup

## Track summaries

### Track 1 — v106 public sync snapshot
15 artifact v106 verificati presenti localmente. PSP apply non eseguita. db_writes=0. Dry-run estimate=160 profili. Banner SERVER_DATA_ISOLATION_BACKEND_PENDING rimane attivo.

### Track 2 — Battle Launch Contract schema
JSON Schema Draft-07. 10 modes (story…world_boss), 6 enemy_source_types, 4 reward_policy, 4 progress_policy, 2 battle_engine_mode. Validation rules + feature_flag_coercions documentati.

### Track 3 — `/api/battle/launch` endpoint
- ✅ Registrato in `server.py` (router prefix `/api/battle`)
- ✅ Smoke test curl: payload con `reward_policy=live, progress_policy=live, battle_engine_mode=authoritative` viene **correttamente coerced a preview** perché tutti i flag sono OFF
- ✅ `idempotency_key_required_for_live_gated_or_live` enforced
- ✅ `db_writes_performed=0`, `reward_granted=false`, `progress_written=false`, `currency_mutated=false`
- ✅ `server_id` parsed ma usato solo per echo + audit trail

### Track 4 — Pre-Battle Lobby contract producer
Helper `frontend/src/battle_launch/buildLaunchContext.ts` introdotto con `buildLaunchContext`, `validateLaunchContext`, `parseLaunchContextFromParams`. Default values: `reward_policy=preview, progress_policy=preview, battle_engine_mode=preview`. **Lobby tsx NON modificata** (conversione consumer pianificata v107B).

### Track 5 — Combat renderer contract consumer
Adapter contract documentato. **`combat.tsx` behavior NON riscritto** (guardrail v107A). Fallback when missing: continue rendering existing preview path; no throw; no mutation.

### Track 6 — Backend loader server_id adoption
**CONTRACT_ONLY_LOADER_CHANGE_DEFERRED_TO_v107B**. 9 endpoint targetati con target_behavior_when_flag_on documentato per ognuno. **0 loader endpoint modificati in v107A**. `backend_isolation_live=false`, `backend_claims_isolation_live=false`. Banner obligation token mantenuto.

### Track 7 — Frontend loader server_id propagation
Helper disponibile + hook `useServerScope` (v104) attivo. 16 loader player-facing identificati come target propagation in v107B. **Adoption stato: HELPER_AVAILABLE_LOADERS_NOT_YET_PROPAGATING**.

### Track 8 — Story auto-resolve deprecation
Plan a 4 fasi (v107A→v107B→v108→v108_post). Target replacement: POST `/api/battle/launch` con mode=story. **v107A action: plan documented, NO code change to `story.tsx` or `/story/battle` endpoint**.

### Track 9 — Encounter source adapter contract
6 adapter definiti (authored, player_team, bot_team, boss, training_preset, event_preset) con `id_format`, `source`, `legacy_hero_id_risk`. Protocol: side_effects=`none`. Runtime implementation: v108.

### Track 10 — Idempotency / reward / progress guard
8 guard rules. Coercion automatica delle policy live → preview quando flag corrispondenti OFF. HTTP 400 quando idempotency_key mancante con live policy coerced.

## Safety flags

```
db_apply                          = false  ✅
psp_migration_apply               = false  ✅
production_db_writes              = false  ✅
reward_grant                      = false  ✅
progress_live_write               = false  ✅
currency_inventory_mutation       = false  ✅
gacha_shop_vip_bp_mutation        = false  ✅
battle_engine_formula_rewrite     = false  ✅
combat_tsx_behavior_rewrite       = false  ✅
destructive_migration             = false  ✅
claim_backend_isolation_live      = false  ✅
claim_authoritative_battle_live   = false  ✅ (sempre coerced a preview)
fake_different_server_data        = false  ✅
hiding_preview_state              = false  ✅ (PREVIEW_ECHO_NON_AUTHORITATIVE esplicito)
fake_PASS                         = false  ✅
validator_weakening               = false  ✅
commercial_release_claim          = false  ✅
```

## Remaining blockers

1. **Loader endpoint backend NON ancora accettano `server_id`** (deferito a v107B).
2. **`pre-battle-lobby.tsx` NON ancora consumer del contract helper** (deferito a v107B).
3. **`combat.tsx` NON ancora parser del launch_context** (deferito a v107B).
4. **`/story/battle` auto-resolve ancora attivo** (deprecation plan documentato, esecuzione v107B→v108).
5. **PSP apply non eseguita** → ogni flag isolamento server resta cosmetico.
6. **`/api/battle/launch` non authoritative** (per design v107A: solo preview echo).

## Next recommended pack

**v107B — Battle Launch Contract Adoption (Frontend Consumers + Backend Loader Server-ID Acceptance)**

- Modifica `pre-battle-lobby.tsx` per produrre payload conforme al contract.
- Adapter parser in `combat.tsx` (lettura non distruttiva del launch_context).
- Backend loader (`/api/user/heroes`, `/api/team/get-formation`, `/api/inventory`, `/api/currencies`, `/api/story/progress`) accettano query param `server_id` opzionale (ignorato quando `SERVER_SCOPED_RUNTIME_ENABLED=false`).
- Smoke test integration: `/api/battle/launch` chiamato realmente da story screen in preview mode.
- Nessuna PSP apply, nessun reward grant, nessun progress write.
