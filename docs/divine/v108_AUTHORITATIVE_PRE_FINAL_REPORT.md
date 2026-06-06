# v108_AUTHORITATIVE_PRE — Final Report

**Pack:** `MEGA_RELEASE_ACCELERATION_66_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE`
**Sentinel:** `PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE`
**Commit:** `fc2ef8a719835b6f673593c080d29469bf64c346`

---

## 1. Verdict

```
MEGA_RELEASE_ACCELERATION_66_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

- `REQUIRED = 0`, `MISS = 0`, `OPTIONAL = 22 ≤ 30`
- 3-run deterministic (`1181/22/0/0` per ciascuna)
- Runtime invariant v108_POSTQA_A **10/10 PASS** + rollup POSTQA A/A2/B/C/D **PASS**
- POSTQA_D mutation gates **9/9 preserved** (smoke 423 + lock code intact)
- 11/11 sub-validator pack 66 **PASS**

---

## 2. Baseline 3-run (pre-pack 66)

| Run | pass | fail | miss | required_fail |
|-----|------|------|------|---------------|
| 1   | 1170 | 22   | 0    | 0             |
| 2   | 1170 | 22   | 0    | 0             |
| 3   | 1170 | 22   | 0    | 0             |

Output: `data/design/authoritative_pre/v108_authoritative_pre_baseline_multirun_v1.json` + `docs/divine/108_AUTHORITATIVE_PRE_BASELINE_MULTIRUN.md`

---

## 3. Final 3-run (post-pack 66)

| Run | pass | fail | miss | required_fail |
|-----|------|------|------|---------------|
| 1   | 1181 | 22   | 0    | 0             |
| 2   | 1181 | 22   | 0    | 0             |
| 3   | 1181 | 22   | 0    | 0             |

**Delta vs baseline:** `+11 PASS`, `fail invariati a 22`. Zero regressioni.

Output: `data/design/authoritative_pre/v108_authoritative_pre_final_multirun_suite_result_v1.json`

---

## 4. Battle Instance Envelope (Track B)

Schema `battle_instance_envelope_v1` definito in
`data/design/authoritative_pre/v108_authoritative_pre_battle_instance_envelope_schema_v1.json`.

Campi chiave:
- `battle_instance_id`, `server_id`, `account_id`, `mode`, `encounter_id`
- `player_team_id`, `player_team_snapshot`, `enemy_source_type`, `enemy_source_id`, `enemy_team_snapshot`
- `battle_engine_mode` ∈ {`preview`,`authoritative_pre`}
- `authoritative_live = false` (**valore fisso**)
- `reward_policy` ∈ {`none`,`preview`}, `progress_policy` ∈ {`none`,`preview`}
- `idempotency_key` (nullable), `client_trace_id` (nullable)
- `feature_flags_observed` (snapshot honest)
- `safety` (db_writes_allowed=false, reward_live_enabled=false, progress_live_enabled=false, server_filter_applied=false, calls_legacy_mutating_endpoints=false)

Block codes definiti: `BATTLE_INSTANCE_SERVER_REQUIRED`, `BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED`, `BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED`, `BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN`, `BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN`.

---

## 5. Backend preview instance endpoint (Track C)

`POST /api/battle/instance/preview` → router file `backend/routes/v108_authoritative_pre_instance.py`, montato in `server.py`.

Smoke runtime live (eseguito a verifica):

| Input                                                                               | HTTP | Code                                          |
|-------------------------------------------------------------------------------------|------|-----------------------------------------------|
| `mode=story` (server_id mancante)                                                   | 423  | `BATTLE_INSTANCE_SERVER_REQUIRED`             |
| server_id presente, team mancante                                                   | 423  | `BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED`        |
| team = `PLAYER_SAFE_FALLBACK_TEAM`                                                  | 423  | `BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED`        |
| team reale, enemy_source mancante                                                   | 423  | `BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED`       |
| enemy_source_id = `GENERATED_ENEMY_RANDOM` (no qa_flag)                             | 423  | `BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED`       |
| `reward_policy=live`                                                                | 423  | `BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN`       |
| **happy path** (team reale, enemy authored E_001)                                   | 200  | envelope `schema_version=battle_instance_envelope_v1`, `authoritative_live=false` |

Sicurezza statica del router:
- nessun import `db`/`motor`/`AsyncIOMotorClient`
- nessuna chiamata a endpoint legacy mutanti
- `authoritative_live` **forzato a False** in tutti i path (anche se REWARD_LIVE_ENABLED fosse true, l'endpoint rifiuta)

---

## 6. Story / Lobby / Combat chain (Track D — pure audit)

Verificato senza modifiche di codice. La chain era già coerente da v108_pre + v108_POSTQA_A:

1. `story.tsx` → `pre-battle-lobby` (marker `v108_pre`)
2. `pre-battle-lobby.tsx` → `/api/battle/launch` (v107D, gated, default OFF, telemetry) → naviga a `/combat` con `launch_context` (Battle Launch Contract v1) + `battle_launch_id` (v108_POSTQA_A)
3. `combat.tsx` legge `launch_context`, riconosce preview valido → **BLOCCA** `/api/battle/simulate`, `refreshUser`, `grantAffinity` (preview reward lock attivo)

Compatibilità envelope ↔ combat:
- `battle_instance_envelope_v1` condivide i campi chiave con `BattleLaunchContract v1` → consumabile dal combat **senza modifiche**, attraverso il preview reward lock già attivo

Residuo onesto: `combat.tsx` legacy entry (senza `launch_context`) resta legacy mutante — **documentato**, non chiamato nel flusso authoritative-pre.

---

## 7. Real team source (Track E)

JSON: `v108_authoritative_pre_real_team_source_contract_v1.json`

- Source reali: `user_heroes` (account-wide), `team_formation` 6 slot (account-wide)
- `PLAYER_SAFE_FALLBACK_TEAM` client-side: **VIETATO come reale** in authoritative-pre
- Forbidden markers: `PLAYER_SAFE_FALLBACK_TEAM`, `FAKE_TEAM`, `DEFAULT_TEAM`, `DEMO_TEAM`, `STUB_TEAM`
- Block code: `REAL_PLAYER_TEAM_SOURCE_PENDING`
- Server-scoped team: **false** (promosso in v109 + v110 PSP apply)
- Battle instance endpoint rifiuta team fake → **smoke 423 verified**

---

## 8. Enemy source (Track F)

JSON: `v108_authoritative_pre_enemy_source_contract_v1.json`

- Allowed types: `authored`, `player_team`, `bot_team`, `boss`, `training_preset`, `event_preset`
- Player-facing: `authored`, `boss`, `training_preset`, `event_preset`
- QA-only: `player_team`, `bot_team`
- Forbidden markers (no qa_flag): `PLACEHOLDER_ENEMY`, `ALPHA_ENEMY`, `STUB_ENEMY`, `DEMO_ENEMY`, `GENERATED_ENEMY_RANDOM`
- Block code: `AUTHORED_ENCOUNTER_SOURCE_PENDING`
- Random / placeholder / alpha player-facing: **vietati** → smoke 423 con `GENERATED_ENEMY_RANDOM`

---

## 9. Server_id loader adoption (Track G — onesto)

JSON: `v108_authoritative_pre_server_id_loader_adoption_v1.json`

Loader auditati (6+):
| Loader                                | parses_server_id | filter_applied |
|---------------------------------------|------------------|----------------|
| `user_heroes`                         | false            | false          |
| `team_formation`                      | false            | false          |
| `inventory`                           | false            | false          |
| `currencies_wallet`                   | false            | false          |
| `story_progress`                      | false            | false          |
| `battle_launch / battle_instance_preview` | **true**     | false (echo only; missing → 423) |

- `server_filter_applied_anywhere = false` (**dichiarazione onesta**)
- Mancanza `server_id` su `/api/battle/instance/preview` → `BATTLE_INSTANCE_SERVER_REQUIRED`
- PSP apply: **false**, server_isolation_live: **false**, promosso in v109 + v110

---

## 10. Reward / Progress / Idempotency preflight (Track H)

JSON: `v108_authoritative_pre_reward_progress_idempotency_preflight_v1.json`

Feature flag (tutti OFF):
`REWARD_LIVE_ENABLED`, `PROGRESS_LIVE_ENABLED`, `BATTLE_LAUNCH_AUTHORITATIVE_ENABLED`, `SERVER_SCOPED_RUNTIME_ENABLED`, `AUTHORITATIVE_BATTLE_ENGINE_ENABLED`.

Endpoint block:
- `reward_policy=live` → 423 `BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN` ✅ smoke verified
- `progress_policy=live` → 423 `BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN` ✅ (logica simmetrica)

Idempotency:
- non richiesta in authoritative-pre (field nullable)
- documentata come **obbligatoria** quando `REWARD_LIVE_ENABLED` o `PROGRESS_LIVE_ENABLED` diventeranno true

Reward/progress write attempts: **0**. DB writes: **0**.

---

## 11. POSTQA_D gate preservation (Track I)

JSON: `v108_authoritative_pre_postqa_d_gate_preservation_v1.json`

| Endpoint                            | Flag                                                  | Default OFF |
|-------------------------------------|--------------------------------------------------------|-------------|
| `POST /api/hero/gain-exp`           | `DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS`         | ✅          |
| `POST /api/hero/levelup`            | `DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS`         | ✅          |
| `POST /api/fusion/star-up`          | `DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS`                | ✅          |
| `POST /api/soul/forge`              | `DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS`            | ✅          |
| `POST /api/vip/add-spend`           | `DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS`          | ✅          |
| `POST /api/battlepass/buy-premium`  | `DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS`          | ✅          |
| `POST /api/friends/gift/{id}`       | `DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS`           | ✅          |
| `POST /api/gvg/end-war`             | `DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS`             | ✅          |
| `POST /api/equipment/equip`         | `DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS`             | ✅          |

- Lock code preservato: `LEGACY_MUTATION_LOCKED_BY_POSTQA_D`
- Smoke runtime: `POST /api/soul/forge` → HTTP 423 + lock code ✅
- `unlocked_in_this_pack = []`

---

## 12. Runtime invariant preservation (Track J)

10/10 validator `v108_POSTQA_A` referenziati nel runner, 0 cancellati, 0 weakened, 0 silently deleted. Aggiunti 12 nuovi (pack 66). Rollup POSTQA A/A2/B/C/D tutti referenziati.

---

## 13. Safety flags

| Vincolo                                                   | Stato |
|-----------------------------------------------------------|-------|
| NO full authoritative live claim                          | ✅    |
| NO reward live                                            | ✅    |
| NO progress live                                          | ✅    |
| NO DB write for reward/progress/economy                   | ✅    |
| NO PSP apply                                              | ✅    |
| NO legacy cleanup apply                                   | ✅    |
| NO server isolation live claim                            | ✅    |
| NO false server_id filter claim                           | ✅    |
| NO fake team as real                                      | ✅    |
| NO random enemy player-facing                             | ✅    |
| NO placeholder/alpha enemy player-facing unless QA flag   | ✅    |
| NO battle_engine formula rewrite                          | ✅    |
| NO gacha/shop/VIP/BP mutation                             | ✅    |
| NO unlocking POSTQA_D mutation gates                      | ✅    |
| NO deletion/downgrading runtime invariant validators      | ✅    |
| NO fake_PASS                                              | ✅    |
| NO validator weakening                                    | ✅    |
| NO release readiness claim                                | ✅    |

---

## 14. Files modified / created

### Backend
- **NEW** `backend/routes/v108_authoritative_pre_instance.py` (router authoritative-pre)
- `backend/server.py` (+ include_router v108_authoritative_pre_instance)

### Design JSON
- `data/design/authoritative_pre/v108_authoritative_pre_baseline_multirun_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_battle_instance_envelope_schema_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_backend_instance_endpoint_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_story_lobby_combat_chain_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_real_team_source_contract_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_enemy_source_contract_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_server_id_loader_adoption_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_reward_progress_idempotency_preflight_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_postqa_d_gate_preservation_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_runtime_invariant_preservation_v1.json`
- `data/design/authoritative_pre/v108_authoritative_pre_final_multirun_suite_result_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_66_v108_authoritative_pre_rollup_marker_v1.json`
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (version 2 → 3, +1 superseding entry per `backend/server.py`)
- `data/design/release_acceleration/mega_release_acceleration_49_v100_rollup_marker_v1.json` (rigenerato)

### Validator (12)
- `backend/scripts/validate_v108_authoritative_pre_baseline_multirun.py`
- `backend/scripts/validate_v108_authoritative_pre_battle_instance_envelope_schema.py`
- `backend/scripts/validate_v108_authoritative_pre_backend_instance_endpoint.py`
- `backend/scripts/validate_v108_authoritative_pre_story_lobby_combat_chain.py`
- `backend/scripts/validate_v108_authoritative_pre_real_team_source_contract.py`
- `backend/scripts/validate_v108_authoritative_pre_enemy_source_contract.py`
- `backend/scripts/validate_v108_authoritative_pre_server_id_loader_adoption.py`
- `backend/scripts/validate_v108_authoritative_pre_reward_progress_idempotency_preflight.py`
- `backend/scripts/validate_v108_authoritative_pre_postqa_d_gate_preservation.py`
- `backend/scripts/validate_v108_authoritative_pre_runtime_invariant_preservation.py`
- `backend/scripts/validate_v108_authoritative_pre_final_multirun_suite.py`
- `backend/scripts/validate_mega_release_acceleration_66_v108_authoritative_pre_rollup.py`

### Master runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+ 12 tuple dopo POSTQA_D)

### Documenti
- **NEW** `docs/divine/108_AUTHORITATIVE_PRE_BASELINE_MULTIRUN.md`
- **NEW** `docs/divine/v108_AUTHORITATIVE_PRE_FINAL_REPORT.md` (questo file)

---

## 15. git diff --stat (sintesi)

```
backend/routes/v108_authoritative_pre_instance.py    | NEW (+240)
backend/server.py                                    | +8
backend/scripts/validate_v108_authoritative_pre_*.py | NEW x11
backend/scripts/validate_mega_release_acceleration_66_v108_authoritative_pre_rollup.py | NEW (+155)
backend/scripts/run_hero_skill_kit_validator_suite.py| +14
data/design/authoritative_pre/*.json                 | NEW x11
data/design/release_acceleration/.._66_marker.json   | NEW
data/design/closed_alpha/v100_runtime_md5_baseline_v1.json | +5 superseding
data/design/release_acceleration/.._49_marker.json   | regenerated
docs/divine/108_AUTHORITATIVE_PRE_BASELINE_MULTIRUN.md | NEW
docs/divine/v108_AUTHORITATIVE_PRE_FINAL_REPORT.md   | NEW (this file)
```

Totale (commit `fc2ef8a7`): **~28 file changed**, principalmente nuovi artefatti del pack.

---

## 16. Remaining blockers (deferred, documentati)

I 22 optional fail residui sono **ereditati e già documentati** dai pack precedenti (POSTQA_A2 baseline reconciliation, B1 triage, POSTQA_C legacy fail resolution). Nessuna regressione introdotta dal pack 66.

Esempi:
- `PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN` (deferred → v109)
- `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` (deferred → v109)
- `PROJECT-V96-MD5-BASELINE-LOCK` (superseded chain documented)
- `MEGA-RELEASE-ACCELERATION-45-v96-ROLLUP` (related)
- `LIVE-MODES-SLC-NEXT-COMBO-A`, `BENCHMARK-CANONICAL-COMBO-A` (deferred → v109)
- `SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1` (deferred → v110)
- `PROJECT-M-TRACK-B/G`, `PROJECT-V-TRACK-F` (deferred → v108_authoritative full)
- `PROJECT-SP-*-TRACK-*` (deferred → v110 PSP apply)
- `PROJECT-BATCH1-V2-TRACK-F-MENU-HARDENING` (deferred → v109)
- `PROJECT-ALIGN-FIX-TRACK-H`, `PROJECT-SF-MERGE-TRACK-F/H` (deferred → v110)
- `PROJECT-FORGE-CRASH-TRACK-G-HYGIENE`, `PROJECT-INLINE-CONFIRM-TRACK-E` (deferred)
- `PROJECT-BETA-TESTING-TRACK-F-REDIS`, `…-TRACK-G-REPORTING` (deferred → v110)
- `PROJECT-GACHA-RATE-SANITY-FINAL-SIGNOFF` (deferred → v110)

Nessuno richiesto/required. Nessuno è blocker per il prossimo pack autoritative full.

---

## 17. Updated remaining pack list

1. **v108_authoritative (full live)** — attivazione `BATTLE_LAUNCH_AUTHORITATIVE_ENABLED` + `REWARD_LIVE_ENABLED` + `PROGRESS_LIVE_ENABLED`, autoritative battle engine, idempotency key obbligatorio (P1)
2. **v109** — Chat / Guild / Live Events server isolation + promozione server_id loader filter_applied=true (P1)
3. **v110** — Legacy data cleanup apply + economy migration + PSP apply (P2)
4. Eventuale **v108_authoritative_QA_C** — riduzione optional ≤ 15 prima del go-live (opzionale)

---

## 18. Time estimate impact

- Pack 66 chiuso in 1 sessione (12 track + endpoint backend + audit chain + 12 validator + rollup + final report)
- Tempo stimato per `v108_authoritative (full live)`: **invariato** — l'envelope schema, le block code, il preflight contract e il gate preservation sono ora **governati da validator**, riducendo il rischio di regressione

---

## 19. Verdetto finale

```
MEGA_RELEASE_ACCELERATION_66_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

- `required=0`, `miss=0`, `optional=22 ≤ 30`, deterministic 3/3
- runtime invariant 10/10 PASS, POSTQA_D gates 9/9 preserved
- 0 DB write, 0 reward grant, 0 progress write, 0 economy/inventory/currency mutation
- 0 fake_PASS, 0 validator weakening, 0 silent deletion
- 0 authoritative live claim, 0 reward live activation, 0 progress live activation
- **Release readiness NON dichiarata.**
- Public sync attesa (pending) sul container locale.
