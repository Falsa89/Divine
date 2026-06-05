# Final Report — MEGA_RELEASE_ACCELERATION_57_v107B

## Verdict

```
MEGA_RELEASE_ACCELERATION_57_BATTLE_LAUNCH_CONTRACT_ADOPTION_FRONTEND_CONSUMERS_AND_LOADER_SERVER_ID_ACCEPTANCE_READY_WITH_PARTIAL_ADOPTION_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

Adoption pack P0 completato in modalità onesta: 2 consumer helper (`preBattleLobbyAdapter`, `combatLaunchParser`) introdotti come pure helpers non-distruttivi. Smoke integration **3/3 PASS** sul vero endpoint `POST /api/battle/launch`. tsx consumer binding deferito a **v107C** per rispetto guardrail "no broad combat.tsx rewrite".

## Commit hash

(local container — public sync pending)

## Suite

| Metrica | v107A | **v107B** | Target |
|---|---|---|---|
| PASS | 1085 | **1095** (+10) | — |
| REQUIRED FAIL | 0 | **0** | = 0 ✅ |
| OPTIONAL FAIL | 23 | **23** | ≤ 30 ✅ |
| MISS | 0 | **0** | = 0 ✅ |
| v107B tuples | n/a | **10/10 PASS** | — ✅ |

## Files Created / Modified

**Modified (1)**: `backend/scripts/run_hero_skill_kit_validator_suite.py` (+10 tuple + sentinel v107B)

**Created (code, 3)**:
- `frontend/src/battle_launch/consumers/preBattleLobbyAdapter.ts` — `launchFromLobby()` chiama POST `/api/battle/launch` con `buildLaunchContext`, ritorna preview echo + errors.
- `frontend/src/battle_launch/consumers/combatLaunchParser.ts` — pure helper `readLaunchContextFromRouterParams`/`FromPostResponse`. Nessun side effect.
- `backend/scripts/smoke_v107b_battle_launch_integration.py` — real HTTP smoke test (3 case).

**Created (8 JSON design + 1 rollup marker + 10 validators)**

## Track Summaries

### 1. v107A baseline snapshot
**11 artifact v107A** verificati presenti. `server.py` MD5 confermato `5af33f8e58fe9aad7ae552c603e43192`. `/api/battle/launch` endpoint status: `PREVIEW_ECHO_NON_AUTHORITATIVE`. db_writes_performed=0.

### 2. Pre-Battle Lobby adoption
**`ADAPTER_HELPER_INTRODUCED_TSX_INTEGRATION_DEFERRED`** · `launchFromLobby()` produce contract v1, chiama `/api/battle/launch`, ritorna `LobbyLaunchResult{contract, preview_echo, errors}`. Default `reward_policy=preview`, `progress_policy=preview`, `battle_engine_mode=preview`. **`pre-battle-lobby.tsx` NON modificato** (consumer binding v107C).

### 3. Combat consumer adoption
**`PARSER_HELPER_INTRODUCED_COMBAT_TSX_UNCHANGED`** · 2 funzioni pure (`readLaunchContextFromRouterParams`, `readLaunchContextFromPostResponse`) ritornano `CombatLaunchEnvelope{contract, is_valid, errors, source, is_preview}`. **`combat.tsx` NON modificato**.

### 4. Story → Lobby/Launch routing
**`ROUTING_PLAN_DOCUMENTED_NO_CODE_CHANGE_v107B`** · Flow target a 7 step documentato. `story.tsx` NON modificato in v107B. Esecuzione v107C.

### 5. Backend loader server_id acceptance
**`REAL_ACCEPTANCE_ON_BATTLE_LAUNCH_ENDPOINT_OTHERS_CONTRACT_ONLY`** · `POST /api/battle/launch` accetta `server_id` (verified via smoke). 9 altri endpoint documentati come target v107C/v108/v109. **0 loader endpoint modificati**. `backend_isolation_live=false`, banner SERVER_DATA_ISOLATION_BACKEND_PENDING attivo.

### 6. Frontend loader server_id propagation
**`ADAPTERS_AVAILABLE_TSX_LOADERS_NOT_YET_PROPAGATING`** · hook `useServerScope` + helper `buildLaunchContext` + 2 adapter consumer pronti. 16 loader player-facing target v107C.

### 7. Battle Launch smoke integration ✅
**3/3 case PASS** via `urllib` reale contro `http://localhost:8001/api/battle/launch`:
- `story_preview_default` → 200 PREVIEW_ECHO, 0 coercioni
- `live_attempt_with_idempotency_coerced_to_preview` → 200 PREVIEW_ECHO, **3 coercioni applicate** (reward, progress, engine_mode)
- `tower_preview` → 200 PREVIEW_ECHO

Tutti i 3 response confermano `safety.db_writes_performed=0`, `reward_granted=false`, `progress_written=false`.

### 8. Story auto-resolve guard
- v107A_contract_only: **DONE**
- v107B_adapter_helpers: **DONE**
- v107C_frontend_consumer_binding: PENDING
- v108_authoritative_engine: PENDING
- v108_post_endpoint_410_or_redirect: PENDING

`story_tsx_modified_v107b=false`, `story_battle_endpoint_modified_v107b=false`, `reward_granted=false`, `progress_written=false`.

### 9. Route exposure safety
**0 nuove route player-facing**. `alpha-menu-preview` unchanged. QA routes non promosse. `/api/battle/launch` classificato runtime_infra, non player-facing. Deep-link a combat con launch_context **NON introdotto** in v107B.

## Safety Flags

```
psp_apply                         = false  ✅
db_migration                      = false  ✅
production_db_writes              = false  ✅
reward_grant                      = false  ✅
progress_live_write               = false  ✅
currency_inventory_mutation       = false  ✅
gacha_shop_vip_bp_mutation        = false  ✅
battle_engine_formula_rewrite     = false  ✅
broad_combat_tsx_rewrite          = false  ✅ (combat.tsx untouched)
destructive_migration             = false  ✅
claim_backend_isolation_live      = false  ✅
claim_authoritative_battle_live   = false  ✅ (smoke prova coercion live→preview)
fake_different_server_data        = false  ✅
hiding_preview_state              = false  ✅ (status PREVIEW_ECHO esplicito)
fake_PASS                         = false  ✅
validator_weakening               = false  ✅
commercial_release_claim          = false  ✅
```

## Remaining Blockers

1. **tsx consumer integration deferita** — `pre-battle-lobby.tsx`, `combat.tsx`, `story.tsx` non ancora consumer (v107C).
2. **5+ backend loader (heroes/team/inventory/currencies/story_progress) non accettano `server_id`** — v107C.
3. **`/story/battle` auto-resolve ancora attivo** — deprecation v108.
4. **PSP apply non eseguita** — server isolamento cosmetico.
5. **`/api/battle/launch` non authoritative** — by design, runtime authoritative v108.

## Next Recommended Pack

**v107C — TSX Consumer Binding (non-destructive) + Backend Loader server_id Acceptance**

- `pre-battle-lobby.tsx`: import + invoca `launchFromLobby()` quando entra in modalità preview esplicita (gated da feature flag).
- `combat.tsx`: import + invoca `readLaunchContextFromRouterParams()` per popolare un ref non-bloccante (no behavioral change).
- `story.tsx`: aggiungi pulsante secondario "Avvia in preview lobby" (gated, default hidden).
- Backend loader (`/api/user/heroes`, `/api/team/get-formation`, `/api/inventory`, `/api/currencies`, `/api/story/progress`): accettano query param `server_id` opzionale (parsed, audited, ignorato quando `SERVER_SCOPED_RUNTIME_ENABLED=false`).
- Smoke integration estesa: chiamata reale da story screen al lobby adapter.
- Tutti i flag restano OFF default. NO reward grant. NO progress write.
