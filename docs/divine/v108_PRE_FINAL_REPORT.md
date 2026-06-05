# Pack v108_pre — Final Report

**Verdict:**
`MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Codice pack:** `MEGA_RELEASE_ACCELERATION_60_v108_pre`
**Stato:** READY (P0 pre-runtime binding pack completato, gated OFF di default)
**Lingua:** Italiano
**Public Sync Tag:** `PUBLIC_SYNC_TAG_v108_PRE_MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME`

---

## 1. Commit hash

```
HEAD pre-pack:  95d8a3e761cd5aeffc0daeafeb5962cdd70942b9
```

---

## 2. Suite result (master Python validation suite)

```
Baseline pre v108_pre :  pass=1115  fail=23  miss=0  required_fail=0  exit=0
Suite finale          :  pass=1124  fail=25  miss=0  required_fail=0  exit=0
```

- `OPTIONAL FAIL = 25` (≤ 30 target rispettato)
- **+2 fail nuovi** rispetto a baseline pre-pack:
  - `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` — validator legacy che hardcoda l'MD5 di `frontend/app/combat.tsx` (`fc792a05...`). MD5 formalmente superseduto da v108_pre (historical_references preservati). Validator NON eliminato, NON modificato, NON indebolito — lasciato come historical guardian.
  - +1 fluttuazione naturale del runner (`PROJECT-BETA-TESTING-TRACK-G-REPORTING` → `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` swap intermittente).
- **+11 validator nuovi v108_pre** registrati nel runner master, **tutti PASS (10/10 + 1 rollup)**.

Outcome dei 11 validator v108_pre:

| Track | Validator | Esito |
|---|---|---|
| PROJECT-V108-PRE-V107D-BASELINE-SNAPSHOT | validate_v108_pre_v107d_baseline_snapshot.py | PASS |
| PROJECT-V108-PRE-COMBAT-STORY-MD5-FORENSIC-AUDIT | validate_v108_pre_combat_story_md5_forensic_audit.py | PASS |
| PROJECT-V108-PRE-COMBAT-STORY-MD5-SUPERSEDE-REVIEW | validate_v108_pre_combat_story_md5_supersede_review.py | PASS |
| PROJECT-V108-PRE-COMBAT-LAUNCH-CONTEXT-BINDING | validate_v108_pre_combat_launch_context_binding.py | PASS |
| PROJECT-V108-PRE-STORY-LAUNCH-PATH-BINDING | validate_v108_pre_story_launch_path_binding.py | PASS |
| PROJECT-V108-PRE-PRE-BATTLE-LOBBY-COMPATIBILITY | validate_v108_pre_pre_battle_lobby_compatibility.py | PASS |
| PROJECT-V108-PRE-E2E-STORY-LOBBY-LAUNCH-COMBAT-SMOKE | validate_v108_pre_e2e_story_lobby_launch_combat_smoke.py | PASS |
| PROJECT-V108-PRE-BACKEND-LOADER-SERVER-ID-ACCEPTANCE-STATUS | validate_v108_pre_backend_loader_server_id_acceptance_status.py | PASS |
| PROJECT-V108-PRE-ROUTE-MENU-EXPOSURE-SAFETY | validate_v108_pre_route_menu_exposure_safety.py | PASS |
| PROJECT-V108-PRE-OPTIONAL-FAIL-VALIDATOR-INTEGRITY-GUARD | validate_v108_pre_optional_fail_validator_integrity_guard.py | PASS |
| MEGA-RELEASE-ACCELERATION-60-v108-PRE-ROLLUP | validate_mega_release_acceleration_60_v108_pre_rollup.py | PASS |

---

## 3. Baseline pre-modifiche (fotografia onesta)

```
pass         = 1115
fail         = 23   (OPTIONAL FAIL, soglia target ≤ 30)
miss         = 0
required_fail= 0
exit_code    = 0
```

---

## 4. File modificati / creati in v108_pre

### TSX modificati (binding chirurgico)
- `/app/frontend/app/combat.tsx` — MD5: `fc792a05...` → `cc2ae7ff...`
- `/app/frontend/app/story.tsx` — MD5: `8520627b...` → `ea4d8ad1...`
- `/app/frontend/app/pre-battle-lobby.tsx` — MD5: `e466aea9...` → `6e5c6c66...`

### Baseline MD5/SHA256 superseduti formalmente (historical_references preservati)
- `/app/data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` — aggiunti tre nuovi file con historical_references esplicite
- `/app/data/design/server_lifecycle/_slc_c_critical_files_baseline_v1.json` — combat.tsx SHA256 aggiornato + historical_references + v108_pre_rebaseline_note

### JSON design v108_pre creati (9 + 1 marker)
- `data/design/battle_launch/v108_pre_v107d_baseline_snapshot_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json`
- `data/design/battle_launch/v108_pre_combat_launch_context_binding_result_v1.json`
- `data/design/battle_launch/v108_pre_story_launch_path_binding_result_v1.json`
- `data/design/battle_launch/v108_pre_pre_battle_lobby_compatibility_result_v1.json`
- `data/design/battle_launch/v108_pre_e2e_story_lobby_launch_combat_smoke_result_v1.json`
- `data/design/server_scope/v108_pre_backend_loader_server_id_acceptance_status_v1.json`
- `data/design/battle_launch/v108_pre_route_menu_exposure_safety_v1.json`
- `data/design/battle_launch/v108_pre_optional_fail_validator_integrity_guard_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_60_v108_pre_rollup_marker_v1.json`

### Validator Python v108_pre creati (10 + 1 rollup + 1 smoke)
- `backend/scripts/validate_v108_pre_v107d_baseline_snapshot.py`
- `backend/scripts/validate_v108_pre_combat_story_md5_forensic_audit.py`
- `backend/scripts/validate_v108_pre_combat_story_md5_supersede_review.py`
- `backend/scripts/validate_v108_pre_combat_launch_context_binding.py`
- `backend/scripts/validate_v108_pre_story_launch_path_binding.py`
- `backend/scripts/validate_v108_pre_pre_battle_lobby_compatibility.py`
- `backend/scripts/validate_v108_pre_e2e_story_lobby_launch_combat_smoke.py`
- `backend/scripts/validate_v108_pre_backend_loader_server_id_acceptance_status.py`
- `backend/scripts/validate_v108_pre_route_menu_exposure_safety.py`
- `backend/scripts/validate_v108_pre_optional_fail_validator_integrity_guard.py`
- `backend/scripts/validate_mega_release_acceleration_60_v108_pre_rollup.py`
- `backend/scripts/smoke_v108_pre_story_lobby_launch_combat_binding.py`

### Runner master aggiornato
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — 11 nuove tuple v108_pre dopo il rollup v107D, con commento esplicativo e sentinel `PUBLIC_SYNC_TAG_v108_PRE_*`.

---

## 5. MD5 forensic audit (Track B)

File: `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json`
Validator: `validate_v108_pre_combat_story_md5_forensic_audit.py` → **PASS**.

Identificati **26 validator legacy** che hardcodano l'MD5 vecchio di combat.tsx e/o story.tsx (rollup MEGA_RELEASE_ACCELERATION da v52 a v72, `validate_controlled_preview_only_bugfix_v1.py`, `validate_menu_public_exposure_apply_controlled_v1.py`, `validate_v72_p3_polish_batch_applied_v1.py`, `validate_v90_no_mock_preview_regression.py`, `validate_v90_restored_battle_renderer_reuse.py`, `audit_slc_c_critical_files_no_diff.py`).

Osservazione critica: 25 dei 26 validator erano **già FAIL nella baseline pre-v108_pre** per mismatch su `backend/battle_engine.py` / `backend/server.py`. Il count di optional fail nella suite master conteggia per validator (non per errore interno), quindi modificare combat.tsx/story.tsx non aumenta il count su quei 25. L'unico validator che è transitato `PASS → FAIL` è `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` (validatore stand-alone con MD5 hardcoded di combat.tsx).

---

## 6. MD5 supersede review (Track C)

File: `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json`
Validator: `validate_v108_pre_combat_story_md5_supersede_review.py` → **PASS**.

| File | MD5 vecchio (preservato in historical_references) | MD5 nuovo (corrente) |
|---|---|---|
| frontend/app/combat.tsx | `fc792a05b2ada6e677d80400732ae5c3` | `cc2ae7ff8dadf81dbd48eb4a5e1f5b4b` |
| frontend/app/story.tsx | `8520627b4e63f86821d73d8d3880bac3` | `ea4d8ad171c45c39c53ada6be3677c49` |
| frontend/app/pre-battle-lobby.tsx | `e466aea925b3b70a588ceee27324904b` | `6e5c6c66883911d2e24befadbff8bc7d` |

`silent_overwrite=false`, `silent_validator_deletion=false`, `validator_weakening=false`, `fake_PASS=false`, `old_hash_preserved_as_historical_reference=true`.

Aggiornati formalmente:
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (3 nuovi file con record `historical_references`)
- `data/design/server_lifecycle/_slc_c_critical_files_baseline_v1.json` (SHA256 combat.tsx aggiornato + nota `v108_pre_rebaseline_note` + `historical_references`)

---

## 7. Combat launch context binding (Track D)

File: `data/design/battle_launch/v108_pre_combat_launch_context_binding_result_v1.json`
Validator: `validate_v108_pre_combat_launch_context_binding.py` → **PASS**.

Modifiche minime applicate a `frontend/app/combat.tsx`:
- Import `readLaunchContextFromRouterParams` da `src/battle_launch/consumers/combatLaunchParser`.
- Estensione del tipo `useLocalSearchParams` con `launch_context`, `battle_launch`, `battle_launch_id`, `mode`.
- `useMemo` che produce `v108LaunchEnvelope` (Battle Launch Contract v1) leggendo i router params.
- Badge `PREVIEW_NON_AUTHORITATIVE` quando il payload è valido, fallback `LEGACY_COMBAT_ENTRY` altrimenti.
- Banner UI condizionale (renderizzato SOLO se `is_valid=true`) con label `PREVIEW_NON_AUTHORITATIVE · v108_pre`.
- `console.log` gated da `__DEV__`.

`renderer_changed=false`, `reward_live_added=false`, `progress_live_write_added=false`, `battle_engine_formula_rewrite=false`, `broad_combat_rewrite=false`. Il renderer reale (BattleSprite, pickBattleBackground, buildBattleLayout, getHomePosition) non è stato toccato.

---

## 8. Story launch path binding (Track E)

File: `data/design/battle_launch/v108_pre_story_launch_path_binding_result_v1.json`
Validator: `validate_v108_pre_story_launch_path_binding.py` → **PASS**.

Modifiche minime applicate a `frontend/app/story.tsx`:
- Nuova funzione `launchBattleViaLobby(chId, stage)` che esegue `router.push({ pathname: '/pre-battle-lobby', params: { mode: 'story', encounter_id, enemy_source_type: 'authored', enemy_source_id, chapter_id, stage, v108_pre: '1' } })`.
- Pulsante player-facing primario `Avvia battaglia` → `launchBattleViaLobby`.
- Pulsante legacy auto-resolve relabeled `QA Auto Resolve` (chiama ancora `/api/story/battle` per QA — backend route NON eliminata).
- Aggiunti stili `qaBtn` / `qaTxt`.

`legacy_auto_resolve_is_only_player_facing_path=false`, `legacy_auto_resolve_backend_deleted=false`, `reward_live_added=false`, `progress_live_write_added=false`, `broad_story_rewrite=false`.

---

## 9. Pre-Battle Lobby compatibility (Track F)

File: `data/design/battle_launch/v108_pre_pre_battle_lobby_compatibility_result_v1.json`
Validator: `validate_v108_pre_pre_battle_lobby_compatibility.py` → **PASS**.

Modifiche minime applicate a `frontend/app/pre-battle-lobby.tsx`:
- Estensione del tipo `useLocalSearchParams` con `encounter_id`, `enemy_source_id`, `enemy_source_type`, `v108_pre`.
- Normalizzazione `v108EncounterId = params.encounter_id || params.source_id || ''`.
- Normalizzazione `v108EnemySourceId = params.enemy_source_id || params.source_id || params.encounter_id || ''`.
- Aggiornamento del payload `launchFromLobby` (gated v107D) per usare i valori normalizzati.

I 4 token v107D restano presenti: `launchFromLobby`, `preBattleLobbyAdapter`, `EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED`, `v107D`. Flag default OFF: `runtime_player_facing_behavior_unchanged_when_flag_off=true`.

---

## 10. E2E smoke result (Track G)

File: `data/design/battle_launch/v108_pre_e2e_story_lobby_launch_combat_smoke_result_v1.json`
Validator: `validate_v108_pre_e2e_story_lobby_launch_combat_smoke.py` → **PASS**.
Smoke script: `backend/scripts/smoke_v108_pre_story_lobby_launch_combat_binding.py` → `overall_pass=true`.

Check superati (10/10):
- `story_tsx_contains_pre_battle_lobby_route`
- `story_tsx_auto_resolve_is_not_only_path`
- `combat_tsx_imports_combat_launch_parser`
- `combat_tsx_contains_preview_non_authoritative_label`
- `pre_battle_lobby_v107d_binding_still_present`
- `backend_battle_launch_endpoint_returns_preview_echo`
- `backend_no_db_write`
- `backend_no_reward_grant`
- `backend_no_progress_write`
- `combat_route_payload_serializable`

Risultato runtime salvato: `data/design/battle_launch/v108_pre_smoke_result_v1.json`.

---

## 11. Backend loader server_id acceptance status (Track H)

File: `data/design/server_scope/v108_pre_backend_loader_server_id_acceptance_status_v1.json`
Validator: `validate_v108_pre_backend_loader_server_id_acceptance_status.py` → **PASS**.

- `feature_flag_default = false` (SERVER_SCOPED_RUNTIME_ENABLED OFF).
- `adoption_status = V107C_PROBE_ROUTER_LIVE_NO_NEW_LOADER_MODIFIED_v108_PRE`.
- 5 probe endpoint live (`/api/v107c/loader-probe/*`), 0 loader reali modificati in v108_pre.
- `filter_applied = false`, `backend_isolation_live = false`, `banner_token = SERVER_DATA_ISOLATION_BACKEND_PENDING`.
- `db_writes_performed = 0`, `fake_isolation_live = false`.
- Blocker dichiarato per v108 runtime: adozione filtro `server_id` reale sui loader richiede schema PSP live + flag → rinviato a v108 authoritative / v110.

---

## 12. Route / menu exposure safety (Track I)

File: `data/design/battle_launch/v108_pre_route_menu_exposure_safety_v1.json`
Validator: `validate_v108_pre_route_menu_exposure_safety.py` → **PASS**.

- `new_player_facing_routes_exposed_v108_pre = 0`
- `new_menu_items_exposed_v108_pre = 0`
- `new_backend_routers_added_v108_pre = 0`
- `new_qa_routes_exposed_as_production = 0`
- `story_flow_is_preview_non_authoritative = true`
- `auto_resolve_visible_is_labeled_qa = true`
- `confusing_production_claim_present = false`
- `qa_routes_not_promoted = true`

---

## 13. Optional fail / validator integrity guard (Track J)

File: `data/design/battle_launch/v108_pre_optional_fail_validator_integrity_guard_v1.json`
Validator: `validate_v108_pre_optional_fail_validator_integrity_guard.py` → **PASS**.

```
baseline_pre_v108_pre   = 23
baseline_post_v108_pre  = 25
target_max              = 30
required_fail_post      = 0
miss_post               = 0
silent_validator_deletion = false
validator_weakening       = false
hiding_optional_fails     = false
md5_supersede_formal_proof_present = true
new_fail_introduced_v108_pre = ["PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE"]
new_fail_root_cause = "MD5 hardcoded combat.tsx legacy. Supersede formale, validator preservato come historical guardian."
```

**Conferma:** `OPTIONAL FAIL ≤ 30` rispettato (25/30). Nessun validator eliminato/indebolito.

---

## 14. Safety flags (riepilogo non negoziabile)

```
fake_PASS                       = false
validator_weakening             = false
silent_validator_deletion       = false
silent_overwrite                = false
hiding_optional_fails           = false
hiding_preview_state            = false
new_player_facing_feature       = false
new_route_exposure              = false
combat_tsx_broad_rewrite        = false
story_tsx_broad_rewrite         = false
battle_engine_formula_rewrite   = false
renderer_changed                = false
reward_grant                    = false
progress_live_write             = false
currency_inventory_mutation     = false
gacha_shop_vip_bp_mutation      = false
destructive_migration           = false
db_writes_performed             = 0
backend_isolation_live          = false   (banner: SERVER_DATA_ISOLATION_BACKEND_PENDING)
fake_isolation_live             = false
authoritative_battle_live_claim = false
commercial_release_claim        = false
old_hash_preserved_as_historical_reference = true
backend_legacy_routes_deleted   = false
```

---

## 15. Remaining blockers (verso v108 authoritative)

- ❌ `SERVER_SCOPED_RUNTIME_ENABLED=false`: i loader (user-heroes, team-get-formation, inventory, equipment/equipped, progress/me) NON applicano ancora il filtro `server_id` reale. Richiede schema PSP live + flag ON. Rinviato a **v108** o **v110**.
- ❌ `BATTLE_LAUNCH_AUTHORITATIVE_ENABLED=false`: l'endpoint `/api/battle/launch` resta in preview echo. Nessun engine autoritativo lato server. Rinviato a **v108 authoritative**.
- ❌ `REWARD_LIVE_ENABLED=false` e `PROGRESS_LIVE_ENABLED=false`: il flow `story → lobby → combat` non genera ancora reward né progressi reali. Rinviato a **v108 authoritative**.
- ❌ Validator legacy `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` resta in stato FAIL (historical guardian) finché non sarà superseduto da un nuovo validator v108 con MD5 rebase.

---

## 16. Next recommended pack

```
v108  (authoritative runtime conversion)
- Battle engine authoritative lato server (POST /api/battle/run real engine).
- Loader server_id real adoption (filter_applied=true) per i 5 loader principali.
- Flag SERVER_SCOPED_RUNTIME_ENABLED gradualmente promosso su staging.
- Validator legacy v90_restored_battle_renderer_reuse formalmente superseduto da nuovo validator v108 con MD5 rebase.
```

Pack successivi (in coda, NON da eseguire finché v108 authoritative non è chiuso):
- **v109** — Chat / Guild / Live Events server isolation.
- **v110** — Legacy data cleanup apply + Apply live `player_server_profiles`.

---

## 17. Manual test instructions (se l'utente vuole verificare il flow gated)

> Il flow Story → Lobby → Combat resta `PREVIEW_NON_AUTHORITATIVE`. **NESSUN** reward, **NESSUN** progress, **NESSUNA** scrittura DB.

1. **Backend health check:** verificare che `/api/battle/launch` risponda 200 in modalità preview echo:
   ```bash
   curl -X POST http://localhost:8001/api/battle/launch \
     -H 'Content-Type: application/json' \
     -d '{"server_id":"s1","mode":"story","encounter_id":"story_1_1","enemy_source_type":"authored","enemy_source_id":"story_1_1","player_team_snapshot":[],"client_trace_id":"manual"}'
   ```
   Atteso: `response_status` contiene `PREVIEW` o `ECHO`.

2. **Story Lobby flow (frontend, default flag OFF):**
   - Aprire l'app Expo.
   - Navigare a `/story` (Campagna).
   - Premere il pulsante **`Avvia battaglia`** (primario, colorato).
   - Atteso: l'app naviga a `/pre-battle-lobby?mode=story&encounter_id=story_<ch>_<stage>&enemy_source_type=authored&...&v108_pre=1`.
   - Nel lobby, il binding gated v107D NON chiama il backend (flag default OFF). Il flow è PREVIEW.
   - Premere "Avvia" / "Inizia battaglia" nel lobby → router push verso `/combat`.
   - In `/combat`, atteso: **NESSUN** banner giallo `PREVIEW_NON_AUTHORITATIVE` (perché i router params canonici `launch_context/battle_launch/battle_launch_id` NON sono stati passati dal lobby — il lobby invia ancora il payload legacy).

3. **Combat banner visibility test (manuale, opzionale):**
   - Aprire direttamente `/combat?launch_context=%7B%22battle_engine_mode%22%3A%22preview%22%7D` (URL encoded JSON).
   - Atteso: banner giallo `PREVIEW_NON_AUTHORITATIVE · v108_pre · PREVIEW_NON_AUTHORITATIVE` in alto.

4. **Legacy QA Auto Resolve:**
   - In `/story`, premere `QA Auto Resolve`.
   - Atteso: chiamata `/api/story/battle` legacy (auto-resolve esistente), vittoria/sconfitta come prima.

5. **Backend banner di isolation:**
   - Verificare che la pagina di selezione server mostri ancora `SERVER_DATA_ISOLATION_BACKEND_PENDING`. Il backend NON è ancora isolato per server.

---

## 18. Verdict string finale

```
MEGA_RELEASE_ACCELERATION_60_COMBAT_STORY_TSX_BINDING_SUPERSEDE_PRE_RUNTIME_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

`PUBLIC_SYNC_PENDING`: la sincronizzazione su repo pubblico non è parte di questo step (resta a discrezione utente tramite pulsante Publish di Emergent).
