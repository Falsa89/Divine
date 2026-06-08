# 110 — Lobby Team Fetch + Core Loader Promotion — Final Report

**Pack:** `MEGA_RELEASE_ACCELERATION_80_LOBBY_TEAM_FETCH_AND_CORE_LOADER_PROMOTION`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_LOBBY_TEAM_FETCH_AND_CORE_LOADER_PROMOTION`
**Data esecuzione (UTC):** 2026-06-07T23:30Z
**Lingua:** Italiano

---

## 1. Verdict

```
MEGA_RELEASE_ACCELERATION_80_LOBBY_TEAM_FETCH_AND_CORE_LOADER_PROMOTION_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

NON viene rivendicata la `release readiness`.

---

## 2. Commit Hash (HEAD prima del commit Pack 80)

```
08a859ac68c3ae39c5101d6af9518faed369387f
```

Il commit Pack 80 sara' firmato con messaggio in italiano:
`feat(pack-80): lobby fetch reale /api/team/get-formation + promozione team_formation loader + MD5 rebase`.

---

## 3. Git Diff Stat (solo file Pack 80)

```
 backend/routes/v96_team_formation.py                                          |   7 +
 backend/scripts/run_hero_skill_kit_validator_suite.py                         |  15 ++
 backend/scripts/validate_mega_release_acceleration_80_lobby_team_fetch_rollup.py |  37 ++++
 backend/scripts/validate_v110_core_loader_promotion_batch.py                  |  20 +++
 backend/scripts/validate_v110_lobby_team_fetch_baseline_multirun.py           |  11 ++
 backend/scripts/validate_v110_lobby_team_fetch_final_multirun_suite.py        |  14 ++
 backend/scripts/validate_v110_lobby_team_fetch_gate_invariant_preservation.py |  16 ++
 backend/scripts/validate_v110_lobby_team_fetch_live_readiness_update.py       |  10 ++
 backend/scripts/validate_v110_lobby_team_fetch_md5_rebase.py                  |  31 ++++
 backend/scripts/validate_v110_lobby_team_fetch_route_usage_map.py             |  16 ++
 backend/scripts/validate_v110_lobby_team_fetch_zero_mutation_preservation.py  |  11 ++
 backend/scripts/validate_v110_pack_79_runtime_real.py                         |   3 +-
 backend/scripts/validate_v110_pre_battle_lobby_team_fetch_implementation.py   |  30 ++++
 backend/scripts/validate_v110_real_team_source_runtime_smoke.py               |  34 ++++
 backend/scripts/validate_v110_story_lobby_combat_payload_update.py            |  17 ++
 backend/scripts/validate_v110_team_formation_route_hardening.py               |  22 +++
 data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json    |  10 +-
 data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json  |  15 +-
 data/design/closed_alpha/v100_runtime_md5_baseline_v1.json                    |   7 +-
 data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json | 174 +++++++++
 frontend/app/pre-battle-lobby.tsx                                             | 187 +++++++++-
 21 files changed, 677 insertions(+), 10 deletions(-)
```

---

## 4. Exact Files Modified

### Runtime (codice eseguito in produzione)

- `frontend/app/pre-battle-lobby.tsx`
- `backend/routes/v96_team_formation.py`

### Validators + suite (orchestrazione)

- `backend/scripts/run_hero_skill_kit_validator_suite.py` (registrazione 13 nuovi validator)
- `backend/scripts/validate_v110_pack_79_runtime_real.py` (rebase MD5 baseline assert)
- 13 nuovi validator Pack 80 (vedi sezione 3).

### Tracking baseline / MD5

- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json`
- `data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json` (nuovo)

---

## 5. Runtime Files Modified

| File | MD5 prima | MD5 dopo | Modifica |
|---|---|---|---|
| `frontend/app/pre-battle-lobby.tsx` | `5ab539bd6a2fdb617a09edfc95f3d06a` | `f8b770a118548602a7f680f59b6c409c` | Fetch reale `/api/team/get-formation?server_id=...`, render 6 slot, empty slot onesti, auth Bearer da SecureStore |
| `backend/routes/v96_team_formation.py` | `cb92524dfe530f38113713ff3167a800` | `347a625d864702e8cda98c170ba62fd6` | Emette `profile_id` (dal PSP) e `blocker` esplicito nel payload, sempre presenti |

---

## 6. Baseline 3-Run Suite (pre-Pack 80)

```
pass=1330  fail=29  miss=0  required_fail=0
```

I 29 fail sono OPTIONAL e pre-esistenti (Redis HA, MD5 lock storici su `battle_engine.py`/`server.py`, audit minori). Nessuno e' causato da modifiche Pack 80.

## 7. Final 3-Run Suite (post-Pack 80)

```
pass=1343  fail=29  miss=0  required_fail=0
delta_pass=+13  delta_fail=0  delta_miss=0  delta_required_fail=0
```

Tre run deterministici hanno tutti riprodotto `pass=1343, fail=29, miss=0`.

---

## 8. Route Usage Map

| Sorgente | Route reale chiamata | Filtro server_id | Auth |
|---|---|---|---|
| `frontend/app/pre-battle-lobby.tsx` | `/api/team/get-formation` | SI (query param `server_id`) | Bearer da `SecureStore:v96_auth_token` |
| `frontend/app/pre-battle-lobby.tsx` | `/api/user/heroes` (enrichment) | NO (account-wide; promotion DEFERRED) | Bearer |
| `frontend/app/pre-battle-lobby.tsx` | `/api/encounter-source/get` (v95 read-only) | NO | read-only |

`selected_server_id` viene letto da `AsyncStorage` (chiave `selected_server_id`), **NESSUN** hardcoded `s1` come fallback player-facing silenzioso. Nessuna chiamata a `/api/battle/simulate`. Nessuna probe-only confusa come loader di produzione.

---

## 9. Lobby Team Fetch Implementation

`pre-battle-lobby.tsx`:

- Nuovo state `playerFormation: PlayerFormationState` con campi `team`, `source`, `fallback_used`, `filter_applied`, `profile_id`, `blocker`, `fetch_status`, `raw_slot_count`.
- `useEffect` dipendente da `selectedServerLoaded`, `selectedServerId`, `backendUrl`:
  - Se `selectedServerId` mancante -> stato `skipped_no_server` + blocker `SELECTED_SERVER_REQUIRED`.
  - Altrimenti recupera Bearer da `SecureStore.getItemAsync('v96_auth_token')` e chiama `${EXPO_BACKEND_URL}/api/team/get-formation?server_id=<id>`.
  - Parsea `filter_applied`, `source`, `profile_id`, `team_formation`, `blocker`.
  - Esegue enrichment best-effort da `/api/user/heroes` per popolare `role`, `level`, `stars`, `power`.
  - Calcola `slots = team_formation.slice(0, PLAYER_SLOT_COUNT).map(...)`.
  - `fallback_used=true` se blocker o slot vuoti.
- Render: `Array.from({ length: PLAYER_SLOT_COUNT }, ...)` su 6 slot. Se lo slot esiste -> `<UnitCard>`. Altrimenti -> `<EmptySlotCard index=i>` (placeholder onesto, NON fake hero).
- Stato visibile: `fetch_status`, `server_id`, `profile_id`, `raw_slots`, `rendered_slots`, `blocker`.
- Pulsante "Avvia Battaglia" rimane disabilitato finche' uno qualunque tra `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER`, `AUTHORED_ENCOUNTER_SOURCE_PENDING`, `SELECTED_SERVER_REQUIRED` e' attivo.

---

## 10. Team Formation Route Hardening

`backend/routes/v96_team_formation.py`:

- Accetta `server_id: Optional[str] = None`.
- `filter_applied=true` SOLO quando `server_id` e' presente nel branch corretto.
- PSP-aware: se `server_id` presente, fetcha `player_server_profiles` e calcola `profile_id`.
- Schema costante (chiavi `server_id`, `filter_applied`, `source`, `profile_id`, `team_formation`, `blocker`, `psp_present_for_server`, `fallback_used`).
- Blocker `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` quando server_id richiesto ma team account-wide vuoto.
- Compat back: senza `server_id` torna `saved_formation` o `safe_fallback_formation`.
- `db_writes=0` (verificato staticamente: nessuna `update_*`/`insert_*`/`delete_*` nel modulo).

---

## 11. Real Team Source Runtime Smoke

Probe HTTP localhost su `http://127.0.0.1:8001`:

| Caso | URL | Risultato atteso | Risultato reale |
|---|---|---|---|
| No auth + server_id | `/api/team/get-formation?server_id=s1` | 401 (gating onesto) | 401 OK |
| No auth + no server_id | `/api/team/get-formation` | 401 | 401 OK |
| Bearer invalido + server_id | `/api/team/get-formation?server_id=s1` | 401 (no bypass) | 401 OK |

NESSUN DB write eseguito durante lo smoke (verifica statica: nessuna `update_one`/`insert_one`/`delete_one` nel modulo route). NESSUN bypass auth silenzioso.

---

## 12. Core Loader Promotion Batch

| Loader | filter_applied | Stato | Motivazione onesta |
|---|---|---|---|
| `/api/team/get-formation` | **true** | **PROMOTED_REAL_FILTER_APPLIED** | Pack 79 + Pack 80: query param `server_id`, PSP-aware, blocker esplicito, profile_id emesso. |
| `/api/user/heroes` | false | DEFERRED_NO_REAL_SERVER_FILTER_YET | Loader account-wide. Non c'e' filtro per server. Non si puo' onestamente dichiarare `filter_applied=true`. |
| `/api/inventory` | false | DEFERRED_NO_REAL_SERVER_FILTER_YET | Inventory non e' ancora PSP-scoped. Promotion deferred. |
| `/api/currencies` | false | DEFERRED_NO_REAL_SERVER_FILTER_YET | Currency ancora account-wide. PSP `soft_currencies` richiede pack separato. |
| `/api/story/progress` | false | DEFERRED_NO_REAL_SERVER_FILTER_YET | Story progress non ancora PSP-scoped. Promotion deferred. |

Nessun `filter_applied=true` falso emesso da nessuna parte (`false_filter_applied_true_emitted_anywhere=false`).

---

## 13. Story / Lobby / Combat Payload Update

- `selected_server_id` propagato dentro `launchContext` (gia' presente da Pack 79, preservato).
- `player_team_snapshot_source = real_fetch_team_formation_route_with_psp_aware_lookup`.
- `slot_count = 6` (era 3-slot placeholder pre-Pack 79).
- `enemy_source = authored_catalog_inline_mirror_with_v95_endpoint_readonly` (NESSUN fake enemy).
- `no_fake_launch_when_blocker_active = true`: il pulsante "Avvia Battaglia" e' disabilitato e mostra blocker chain visibili.

---

## 14. Zero Mutation / Economy Preservation

```
db_writes: 0
reward_grant: false
progress_advance: false
ledger_writes: false
premium_currency_grant: false
gacha_mutation: false
shop_mutation: false
vip_mutation: false
battle_pass_mutation: false
```

Nessuna mutazione DB. Nessuna economia toccata. Nessun grant. Nessun gacha. Nessun BP/VIP/Shop.

---

## 15. Live Readiness Update

```
reward_live: false
progress_live: false
ledger_live: false
battle_engine_authoritative_live: false
release_readiness_claimed: false
```

Reward live e Progress live restano **OFF**. Nessuna release readiness claim.

---

## 16. MD5 Rebase Summary

Catena di rebase autorizzata (mantenendo riferimenti storici):

```
frontend/app/pre-battle-lobby.tsx:
  pre-Pack 79   a495baf478924c52eaac9dd22c4032e7
  Pack 79  ->   5ab539bd6a2fdb617a09edfc95f3d06a   (PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER blocker + fallback vuoto)
  Pack 80  ->   f8b770a118548602a7f680f59b6c409c   (real fetch + 6 slot + auth bearer)
```

Tracking files aggiornati con il nuovo MD5 e preservazione dello storico:
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json`
- `backend/scripts/validate_v110_pack_79_runtime_real.py` (assert lobby MD5 aggiornato)

`backend/routes/v96_team_formation.py` non ha MD5 lock validator e quindi non richiede rebase tracking, ma e' documentato nel summary (`cb92524d... -> 347a625d...`).

---

## 17. Gate / Runtime Invariant Preservation

- POSTQA_D gates: **non modificati**.
- `battle_engine.py`: **non riscritto** (MD5 invariato `1ac058bc...`).
- `/api/battle/simulate`: **non chiamato** da staging/live.
- v107D binding: `launchFromLobby`, `EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED` -> preservati.
- v108_POSTQA_A blocker chain: `REAL_PLAYER_TEAM_SOURCE_PENDING`, `AUTHORED_ENCOUNTER_SOURCE_PENDING`, `SELECTED_SERVER_REQUIRED`, `launchAllowedNormal`, `blockerReasons`, `EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH`, `realPlayerTeamAvailable`, `authoredEncounterAvailable`, `selectedServerAvailable` -> preservati.
- v93 `resolvePlayerFormation` token -> preservato (rimane funzione, ora usata come initial state).
- v91 token (`SourceBadge`, `Modifica Team`, `Avvia Battaglia`, `random_opponents_allowed=false`, `is_random: false`, `runtime_generated: false`, `fallback_random_allowed: false`, `router.push('/(tabs)/battle'`, `/combat?mode=...`) -> tutti preservati.

Validator legacy correlati eseguiti dopo le modifiche e tutti **PASS**: `validate_v91_pre_battle_lobby_flow`, `validate_v93_real_formation_source`, `validate_v93_team_editor_wiring`, `validate_v95_real_formation_runtime_fetch`, `validate_v108_postqa_invariant_lobby_no_fake_team_launch`, `validate_v108_pre_combat_story_md5_forensic_audit`, `validate_v108_pre_combat_story_md5_supersede_review`, `validate_v108_authoritative_runtime_story_lobby_combat_chain`, `validate_v108_pre_pre_battle_lobby_compatibility`, `validate_v108_postqa_invariant_lobby_launch_context_to_combat`, `validate_v108_authoritative_pre_story_lobby_combat_chain`, `validate_pre_battle_lobby_ui_fix`, `validate_v96_auth_endpoints`, `validate_v110_pack_79_runtime_real` (post rebase).

---

## 18. Safety Flags

```
fake_PASS:                                false
validator_weakening:                      false
release_readiness_claimed:                false
production_apply_executed:                false
production_db_writes:                     false
destructive_migration:                    false
delete:                                   false
premium_grant:                            false
reward_live:                              false
progress_live:                            false
legacy_cleanup_executed:                  false
false_filter_applied_true:                false
fake_team_as_real:                        false
fake_enemy_as_authored:                   false
3_slot_placeholder_player_facing:         false
hardcoded_s1_silent_player_facing_fallback: false
battle_engine_formula_rewrite:            false
battle_simulate_called_from_staging_or_live: false
approval_flags_changed_to_yes_for_pack_80: false
postqa_d_gates_unlocked:                  false
```

---

## 19. REWARD / PROGRESS LIVE OFF

**Dichiarazione esplicita:** Reward live e Progress live restano **OFF**. Nessun ledger write live. Nessun grant. Nessun premium currency grant. Nessuna progressione live abilitata in questo pack.

---

## 20. LEGACY CLEANUP NOT EXECUTED

**Dichiarazione esplicita:** NESSUN legacy cleanup eseguito. NESSUNA migrazione distruttiva. NESSUN delete. NESSUN PSP production apply (gia' eseguito in Pack 77, NON ripetuto).

---

## 21. No Fake Team As Real

**Dichiarazione esplicita:** NESSUN fake team spacciato per reale. Quando il fetch a `/api/team/get-formation?server_id=...` torna `blocker=PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` o team vuoto, la lobby:
- NON renderizza fake heroes,
- mostra empty slot card placeholder (`<EmptySlotCard>`) per i 6 slot,
- mantiene `fallback_used=true` e source label `blocked_no_team_for_server`,
- disabilita "Avvia Battaglia" mostrando il blocker chain.

Nessun 3-slot placeholder player-facing. Nessun hardcoded `s1` silent fallback. Nessun `filter_applied=true` falso.

---

## 22. Remaining Blockers (Deferred, Documented)

- `/api/user/heroes` core loader **NOT promoted** (no real per-server filter yet) — DEFERRED honestly.
- `/api/inventory` core loader **NOT promoted** (no PSP scoping yet) — DEFERRED honestly.
- `/api/currencies` core loader **NOT promoted** (PSP soft_currencies path requires separate pack) — DEFERRED honestly.
- `/api/story/progress` core loader **NOT promoted** (not PSP-scoped yet) — DEFERRED honestly.
- Reward/progress live **OFF** (intenzionale).
- Legacy cleanup **NOT executed** (intenzionale).
- PSP production apply **NOT re-executed** (gia' fatto in Pack 77, non ripetuto).

---

## 23. Next Step Recommendation

Suggerimenti per il prossimo pack (richiede ZIP esplicito da utente):

1. **Inventory loader PSP-scoped**: introdurre `server_id` su `/api/inventory` e promuoverlo a `filter_applied=true` solo se le query MongoDB filtrano davvero per `user_id + server_id`.
2. **Currencies PSP-scoped**: spostare `soft_currencies` su `player_server_profiles.soft_currencies` con read path PSP-aware su `/api/currencies?server_id=...`.
3. **Story progress PSP-scoped**: aggiungere `server_id` su `/api/story/progress` e leggere da PSP.
4. **User heroes**: definire se gli eroi siano account-wide o PSP-scoped; se PSP-scoped, aggiungere `server_id` su `/api/user/heroes`.
5. **Lobby E2E test reale**: aggiungere uno smoke E2E autenticato (con account `divine_waifus_staging_clone`) che apre la lobby, verifica il fetch e l'emissione 6 slot.

NESSUN suggerimento abilita reward live o progress live: continueranno a richiedere pack dedicati con autorizzazione esplicita.

---

## 24. Appendice — Validator Pack 80

```
PROJECT-V110-LOBBY-TEAM-FETCH-BASELINE-MULTIRUN              PASS
PROJECT-V110-LOBBY-TEAM-FETCH-ROUTE-USAGE-MAP                PASS
PROJECT-V110-PRE-BATTLE-LOBBY-TEAM-FETCH-IMPLEMENTATION      PASS
PROJECT-V110-TEAM-FORMATION-ROUTE-HARDENING                  PASS
PROJECT-V110-REAL-TEAM-SOURCE-RUNTIME-SMOKE                  PASS
PROJECT-V110-CORE-LOADER-PROMOTION-BATCH                     PASS
PROJECT-V110-STORY-LOBBY-COMBAT-PAYLOAD-UPDATE               PASS
PROJECT-V110-LOBBY-TEAM-FETCH-ZERO-MUTATION-PRESERVATION     PASS
PROJECT-V110-LOBBY-TEAM-FETCH-LIVE-READINESS-UPDATE          PASS
PROJECT-V110-LOBBY-TEAM-FETCH-MD5-REBASE                     PASS
PROJECT-V110-LOBBY-TEAM-FETCH-GATE-INVARIANT-PRESERVATION    PASS
PROJECT-V110-LOBBY-TEAM-FETCH-FINAL-MULTIRUN-SUITE           PASS
MEGA-RELEASE-ACCELERATION-80-LOBBY-TEAM-FETCH-ROLLUP         PASS
```

13/13 validator PASS. Suite finale: `pass=1343, fail=29, miss=0, required_fail=0`.

---

**Fine report Pack 80.**
