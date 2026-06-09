# Pack 92 — MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP — Final Report

> **Lingua**: italiano (per direttiva utente).
> **Pacchetto**: `MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP`
> **Sentinella**: `PUBLIC_SYNC_TAG_v110_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP`
> **Track**: M (core server-scope megapack)
> **Generato**: 2026-06-09 (UTC)

---

## 1. Verdict

```
verdict = MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
verdict_class = READY
required_fails = 0
miss = 0
optional_fails = 29   # invariato vs baseline pre-Pack-92
deterministic = true  # 3 esecuzioni consecutive identiche (1507/29/0/0)
frontend_user_heroes_server_id_sweep = COMPLETED
real_runtime_guard_smoke_executed = true (read-only, no broad DB writes)
```

---

## 2. Commit hash & Git diff --stat

> Il commit verrà eseguito al termine di questo report; il `commit_hash`
> sarà inserito come post-script (§24) dopo `git commit`.

### Sintesi diff (file rilevanti)

```
backend/routes/soul_forge.py                                                       |   90 +/-  (wallet split server_id)
backend/routes/combat.py                                                           |   80 +/-  (story chapters server_id guard)
backend/routes/equipment.py                                                        |   45 +/-  (equipment honest deferred blocker)
backend/scripts/run_hero_skill_kit_validator_suite.py                              |   20 +++
backend/scripts/smoke_v110_pack_92_runtime_guard_e2e.py                            |  220 +++  (new)
backend/scripts/cleanup_v110_pack_92_test_artifacts.py                             |   75 +++  (new)
backend/scripts/validate_v110_pack_92_*.py                                          | ~250 +++  (16 new validators)
backend/scripts/validate_mega_release_acceleration_92_*.py                          |   60 +++  (1 new rollup)
data/design/v110_pack_92_core_server_scope/*.json                                  | ~600 +++  (16 new design JSONs + summary)
docs/divine/115_CANON_CORE_SERVER_SCOPE_SPLIT.md                                   |   38 +++  (new SOT doc)
docs/divine/110_PACK_92_BASELINE_MULTIRUN.md                                       |    9 +++  (new)
docs/divine/110_PACK_92_FINAL_MULTIRUN_SUITE.md                                    |   11 +++  (new)
docs/divine/110_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP_FINAL_REPORT.md | (new)
frontend/app/(tabs)/heroes.tsx                                                     |   12 +/-
frontend/app/(tabs)/battle.tsx                                                     |    8 +/-
frontend/app/hero-collection.tsx                                                   |    5 +/-
frontend/app/select-home-hero.tsx                                                  |   12 +/-
frontend/app/equipment.tsx                                                         |   55 +/-  (server scope + deferred blocker UI)
frontend/app/soul-forge.tsx                                                        |   16 +/-
frontend/app/story.tsx                                                             |   16 +/-
frontend/app/inventory.tsx                                                         |    1 +/-  (Pack 91 caveat resolved)
data/design/.../*.json (MD5 rebases secondari)                                     |   ~30 +/- (12 baseline aggiornate)
```

Il rimanente diff (~160 file `*_result.json` + `*.pyc`) è puramente
derivato dall'esecuzione dei validator deterministici.

---

## 3. Baseline & Final suite — multirun

### Pre-Pack-92 baseline (3 run)

| Run | pass | fail | miss | deterministic |
|-----|------|------|------|---------------|
| 1   | 1490 | 29   | 0    | true          |
| 2   | 1490 | 29   | 0    | true          |
| 3   | 1490 | 29   | 0    | true          |

### Post-Pack-92 final (3 run)

| Run | pass | fail | miss | deterministic |
|-----|------|------|------|---------------|
| 1   | 1507 | 29   | 0    | true          |
| 2   | 1507 | 29   | 0    | true          |
| 3   | 1507 | 29   | 0    | true          |

Δ pass = +17 (16 nuove track Pack 92 + 1 rollup). Δ fail = 0.
`REQUIRED_FAIL = 0`, `MISS = 0`. Baseline 29 OPTIONAL preservata.

---

## 4. Core route & schema audit (Track B)

| Endpoint                       | File                        | Schema status                                                    | Pack 92 azione                                                                  |
|--------------------------------|-----------------------------|------------------------------------------------------------------|---------------------------------------------------------------------------------|
| `GET /api/wallet`              | `routes/soul_forge.py`      | `users`(global) + `wallets`(legacy) + `psp.soft_currencies`(canonical) | **REAL SPLIT**: `currencies_global`/`currencies_server_scoped` + PSP check     |
| `GET /api/story/chapters`      | `routes/combat.py`          | `db.story_progress`(legacy) + `psp.story_progress`(canonical)    | **REAL FILTER**: PSP.story_progress lookup, no DB write strict path             |
| `GET /api/user/equipment`      | `routes/equipment.py`       | `user_equipment`: server_id presente solo ~10% (3/31 docs)       | **HONEST DEFERRED BLOCKER**: `EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED`|
| `GET /api/inventory`           | `routes/items.py`           | strict server-scoped da Pack 89                                  | **UNCHANGED** (Pack 89 baseline preservato)                                     |
| `GET /api/user/heroes`         | `server.py`                 | strict server-scoped da Pack 81                                  | **UNCHANGED** (Pack 81 baseline preservato)                                     |
| `GET /api/team/get-formation`  | `routes/v96_team_formation` | strict server-scoped da Pack 88                                  | **UNCHANGED** (Pack 88 baseline preservato)                                     |

Frontend player-facing audit: 9 caller individuati in `/app/frontend/app/*`
(esclusi preview/dev). Tutti migrati al sweep §8.

---

## 5. Core server-scope SOT (Track C)

Documento canonico creato: `docs/divine/115_CANON_CORE_SERVER_SCOPE_SPLIT.md`.

**Account-wide (resta globale):**
- account identity / email / username / auth tokens
- global entitlements / purchase entitlements
- `gems` (hard/premium IAP-coupled)
- `gold` (legacy account-wide; promotion server-scoped DEFERITA)

**Server-scoped (PSP):**
- `user_heroes` (Pack 81), `team_formation` (Pack 88), `inventory` (Pack 89/90/91)
- soft currencies (`honor`, `guild_points`, `prana`, `soul_seals`, `mission_coins`, `dimension_frags`, `star_dust`) → `psp.soft_currencies`
- `story_progress` → `psp.story_progress`
- `user_equipment` (migration richiesta prima della promozione strict)
- `player_level`/`player_exp`/progressione operativa → PSP

**Vincoli**: nuovi server partono freschi, nessun S1→S2 copy, reward/progress live OFF.

---

## 6. Currency/Wallet loader split (Track D)

```python
# soul_forge.py — GET /api/wallet?server_id=<sid>
# server_id presente + PSP esiste:
return {
  "server_id": sid,
  "filter_applied": True,
  "wallet_source": "psp_server_scoped_split",
  "currencies_global":      {"gold": {...}, "gems": {...}},        # users (account-wide per SOT)
  "currencies_server_scoped":{"honor":..., "guild_points":..., ...}, # psp.soft_currencies REAL
  "_slc_pack_92_wallet_split": True,
}
# server_id presente + PSP assente -> blocker PLAYER_SERVER_PROFILE_REQUIRED, filter_applied=true
# server_id assente -> legacy_account_wide_deprecated, filter_applied=false
```

- **NO false `filter_applied=true`**: quando `filter_applied=true` lo split o
  il blocker sono **reali** (verificato via runtime smoke).
- **NO balance mutation**: nessuna scrittura su `users.gold/gems` né su
  `psp.soft_currencies`. Spend/write strict scope → pack futuro.

---

## 7. Story progress loader (Track E)

```python
# combat.py — GET /api/story/chapters?server_id=<sid>
# server_id presente + PSP:
sp = psp.get("story_progress") or {}
# REAL read di completed/current_chapter/current_stage da PSP, no DB write
return {server_id, filter_applied: True, progress_source: "psp_server_scoped", chapters, progress}
```

- **NO DB write strict path**: il path server-scoped non fa `insert_one`
  né `upsert` sulla collection `story_progress` legacy.
- **NO story progress write promotion**: il path POST `/api/story/battle`
  (write esistente che muta `db.story_progress` + `users.gold/gems`) NON
  è promosso in Pack 92. Documentato in Track J come future write pack.

---

## 8. Equipment loader (Track F)

```python
# equipment.py — GET /api/user/equipment?server_id=<sid>
# server_id presente:
return {
  "blocker": "EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED",
  "server_id": sid, "psp_exists": bool(psp),
  "filter_applied": True,                  # filtro REALE applicato, ma onestamente negato
  "equipment_source": "none",
  "items": [],
  "migration_required": True,
  "migration_required_reason": "user_equipment collection schema mixed (server_id presente solo ~10% dei docs in baseline). Promozione a strict filter senza backfill produrrebbe risultati falsi/vuoti per la maggior parte dei player.",
}
# server_id assente -> legacy account-wide list (non-player-facing)
```

- **Honest deferred blocker** ≠ false readiness: il filter è reale,
  il blocker è dichiarato apertamente, migration documentata.
- Nessuna equip/unequip/forge write promotion (POSTQA_D lock preserved).

---

## 9. Frontend server_id sweep (Track G)

8 file player-facing migrati:

| File                                  | Endpoint(s) migrati                              | useServerScope | server_id query |
|---------------------------------------|--------------------------------------------------|----------------|------------------|
| `frontend/app/(tabs)/heroes.tsx`      | `/api/user/heroes`                               | ✅             | ✅               |
| `frontend/app/(tabs)/battle.tsx`      | `/api/user/heroes`                               | ✅             | ✅               |
| `frontend/app/hero-collection.tsx`    | `/api/user/heroes`                               | ✅             | ✅               |
| `frontend/app/select-home-hero.tsx`   | `/api/user/heroes`                               | ✅             | ✅               |
| `frontend/app/equipment.tsx`          | `/api/user/equipment` + `/api/user/heroes` + UI deferred-blocker banner | ✅ | ✅      |
| `frontend/app/soul-forge.tsx`         | `/api/user/heroes` + `/api/wallet`               | ✅             | ✅               |
| `frontend/app/story.tsx`              | `/api/story/chapters`                            | ✅             | ✅               |
| `frontend/app/inventory.tsx`          | `/api/user/heroes` (Pack 91 **caveat resolved**) | ✅             | ✅               |

`pre-battle-lobby.tsx` già passava `server_id` (Pack 80/81/88), preservato.

---

## 10. Frontend static regression guard (Track H)

Validator `validate_v110_pack_92_frontend_static_regression_guard.py`:
- Esegue grep dinamico su `/app/frontend/app/` (esclusi preview/dev/sandbox/node_modules).
- Per ogni endpoint guardato (`/api/user/heroes`, `/api/inventory`, `/api/item-shop/buy`, `/api/inventory/use-exp`, `/api/wallet`, `/api/story/chapters`, `/api/user/equipment`):
  - Se presente nel file, almeno una occorrenza deve essere seguita da `?` con `server_id=` (esplicito o via `${qs}` con definizione `qs` contenente `server_id=`); occorrenze "bare" sono accettate solo se il file adotta il hook (sono fallback no-server-selected).
- Vieta literal `server_id=s1` ovunque nel frontend (`server_id=s1` → 0 occorrenze).

Risultato corrente: **OK**, `player_facing_files_adopt_server_id_query_or_hook_fallback zero_silent_s1_literal`.

---

## 11. Runtime guard smoke (Track I) — **EXECUTED, READ-ONLY**

Script: `backend/scripts/smoke_v110_pack_92_runtime_guard_e2e.py`  
Result: `data/design/v110_pack_92_core_server_scope/v110_pack_92_runtime_guard_smoke_result_v1.json`

**Marker test (no production writes):**
- email: `pack92_test_user_<ts>@test.com`
- PSP/user marker: `pack_92_test_artifact=true`
- server A: `s_pack92_a_<ts>` (PSP creato)
- server UNKNOWN: `s_pack92_unknown_<ts>` (PSP NON creato → blocker)

**Prove (15/15 PASS):**

| #  | Step                                                                  | Esito |
|----|-----------------------------------------------------------------------|-------|
| 1  | register test user                                                    | ✅ PASS |
| 2  | ensure PSP A                                                           | ✅ PASS |
| 3  | mark Pack 92 artifacts (DB write SOLO su test artifacts)              | ✅ PASS |
| 4  | `GET /api/wallet?server_id=A` → split REALE                           | ✅ PASS (filter_applied=true, wallet_source=psp_server_scoped_split) |
| 5  | `GET /api/wallet?server_id=UNKNOWN` → blocker onesto                  | ✅ PASS (blocker=PLAYER_SERVER_PROFILE_REQUIRED, filter_applied=true, wallet_source=none) |
| 6  | `GET /api/wallet` (no server_id) → legacy flagged                     | ✅ PASS (filter_applied=false, wallet_source=legacy_account_wide_deprecated) |
| 7  | `GET /api/story/chapters?server_id=A` → real PSP read                 | ✅ PASS (filter_applied=true, progress_source=psp_server_scoped) |
| 8  | `GET /api/story/chapters?server_id=UNKNOWN` → blocker onesto          | ✅ PASS (blocker=PLAYER_SERVER_PROFILE_REQUIRED, progress_source=none) |
| 9  | `GET /api/story/chapters` (no server_id) → legacy flagged             | ✅ PASS (filter_applied=false, progress_source=legacy_account_wide_deprecated) |
| 10 | `GET /api/user/equipment?server_id=A` → honest deferred blocker       | ✅ PASS (blocker=EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED, migration_required=true) |
| 11 | `GET /api/user/equipment` (no server_id) → legacy flagged             | ✅ PASS (filter_applied=false) |
| 12 | `GET /api/inventory?server_id=A` (Pack 89 strict preservato)          | ✅ PASS (inventory_source=player_server_scoped, items=[]) |
| 13 | `POST /api/item-shop/buy` senza server_id (Pack 90 strict preservato) | ✅ PASS (400/422 SERVER_ID_REQUIRED) |
| 14 | `GET /api/user/heroes?server_id=A` (Pack 81 strict preservato)        | ✅ PASS (list empty, no leak) |
| 15 | Cleanup test artifacts                                                 | ✅ PASS (users=1, inv=0, psp=1, uh=0, story=1, eq=0 eliminati) |

`real_smoke_executed=true`, `read_only=true`, `no_db_writes_other_than_test_setup=true`.

---

## 12. Future migration/write-path plan (Track J)

| Nome                              | Endpoints                                       | Approval string proposta                                          | Eseguito in Pack 92 |
|-----------------------------------|-------------------------------------------------|-------------------------------------------------------------------|---------------------|
| `currency_spend_write`            | `POST /api/wallet/spend` (NEW) + buy decrement  | `AUTORIZZO_V110_CURRENCY_SPEND_WRITE_STRICT_SCOPE_PACK_NN`        | ❌ NO               |
| `story_progress_write`            | `POST /api/story/battle`                        | `AUTORIZZO_V110_STORY_PROGRESS_WRITE_STRICT_SCOPE_PACK_NN`        | ❌ NO               |
| `equipment_write` (3 step)         | backfill server_id → loader strict → write strict | `AUTORIZZO_V110_EQUIPMENT_WRITE_STRICT_SCOPE_PACK_NN`              | ❌ NO               |
| `reward_claim_ledger`             | reward live                                     | `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_PACK_NN`                 | ❌ NO               |

Ogni futuro pack include: backup snapshot, idempotency token, audit ledger, rollback plan.

---

## 13. Data invariants (Track K)

```json
{
  "broad_db_writes": false,
  "currency_write_promotion": false,
  "story_progress_write_promotion": false,
  "equipment_write_promotion": false,
  "reward_live": false, "progress_live": false,
  "premium_grant": false, "s1_to_s2_copy": false,
  "legacy_cleanup_executed": false,
  "destructive_migration": false,
  "production_user_db_writes": false,
  "schema_migration_executed": false, "backfill_executed": false,
  "account_wide_fallback_for_server_bound_data": false,
  "silent_s1_fallback": false, "copy_s1_to_s2_inventory": false,
  "false_filter_applied_true": false,
  "pack_88_team_strict_preserved": true,
  "pack_89_inventory_get_strict_preserved": true,
  "pack_90_inventory_write_paths_strict_preserved": true,
  "pack_91_inventory_frontend_consumer_migration_preserved": true,
  "player_level_mutation": false, "user_heroes_cross_server_mutation": false,
  "team_route_regression": false, "postqa_d_gates_unlocked": false,
  "battle_engine_formula_rewrite": false,
  "battle_simulate_called_from_staging_or_live": false,
  "release_readiness_claimed": false,
  "fake_PASS": false, "validator_weakening": false
}
```

I soli DB writes eseguiti in Pack 92 sono test artifacts marcati
`pack_92_test_artifact=true` nello smoke E2E, cancellati nel finally.

---

## 14. Cleanup / rollback (Track L)

Script: `backend/scripts/cleanup_v110_pack_92_test_artifacts.py`
- **Refuse-by-default**, `--apply` richiesto.
- Filtra `pack_92_test_artifact=true` OR email `^pack92_test_user_\d+@test\.com$`.
- Production users protetti.
- Post-smoke dry-run: `candidate test users: 0`.

**Rollback runtime**: revert dei 3 file backend + 8 file frontend al
commit pre-Pack-92 + revert dei 13 MD5 rebase JSON. Nessuna migration
DB / nessun backfill da invertire.

---

## 15. Live readiness update (Track M)

```
inventory_read_write_frontend_ready      = true
frontend_server_id_sweep_ready           = true
currency_loader_ready                    = true   # split real
story_loader_ready                       = true   # PSP read real
equipment_loader_ready                   = false  # migration required first
equipment_loader_preflight_ready         = true   # honest deferred blocker active

currency_spend_write_ready               = false
story_progress_write_ready               = false
equipment_write_ready                    = false
reward_claim_ledger_live                 = false
reward_live                              = false
progress_live                            = false
release_readiness_claimed                = false
```

---

## 16. MD5 rebase (Track N)

### Backend runtime modificati in Pack 92

| File                              | MD5 post-Pack-92                       | Reason                                                                                     |
|-----------------------------------|----------------------------------------|--------------------------------------------------------------------------------------------|
| `backend/routes/soul_forge.py`    | `0bf5e5b493c1503819d2d9e3831cc058`     | Wallet split server-scope (real split + PSP check + legacy flagged)                        |
| `backend/routes/combat.py`        | `d0b16edd17ba8a8cd50960caacfd12fa`     | Story chapters loader server-scope guard (PSP real read + no DB write strict)              |
| `backend/routes/equipment.py`     | `54867dda3ea4ac58da4fad0ab402123b`     | Equipment loader honest deferred blocker (no strict promotion, migration required)         |

### Backend invariati
| File                              | MD5                                    | Note                                                            |
|-----------------------------------|----------------------------------------|-----------------------------------------------------------------|
| `backend/routes/items.py`         | `f887c3ce5eea0a847a1d9a05ae9e2aa5`     | Pack 90 baseline preserved (unchanged in Pack 92)               |

### Rebase secondari (autorizzati da Track N)

Pack 92 ha modificato 3 file frontend già tracciati in baseline MD5 di
pack precedenti. Rebase applicato in 13 JSON di design, con storico
preservato (`from_historical` salvato):

| File                                | Da (historical)                         | A (post-Pack-92)                       | JSON aggiornate (count) |
|-------------------------------------|------------------------------------------|----------------------------------------|--------------------------|
| `frontend/app/soul-forge.tsx`       | `fe4efcdeb60c69e8827f914cf0ac8e4c`       | `58f24f4aac0664460f03ee566d1942c0`     | 8                        |
| `frontend/app/story.tsx`            | `6ce181dd4db0eac129e3d4cf0e2154a8`       | `77144cd718cd2c6cd222637be3ff7f2d`     | 3                        |
| `frontend/app/equipment.tsx`        | `2a77383ab2b0ca6b8de442e857c5c1aa`       | `f04050a49204c890a2d352c43681e27c`     | 1                        |

Tutti i rebase con `replacement_invariant_functional=true`,
`validator_weakening=false`, `fake_PASS=false`, `historical_references_preserved=true`.

**Invarianti preservate dai file frontend rebase-ati:**
- `soul-forge.tsx`: EMERGENCY_RESTORE Track B/H semantics preservate; lock UI invariata; nessuna nuova mutation surface.
- `story.tsx`: v108 PRE_COMBAT_STORY MD5 sentinel preservata semanticamente (story first-node runtime preview screen invariata).
- `equipment.tsx`: POSTQA_D lock preserved; nessun cambio equip/unequip/forge UI logic.

---

## 17. Gate invariant preservation (Track O)

| Gate                                              | Stato       |
|---------------------------------------------------|-------------|
| `POSTQA_D_*` unlock                               | **CHIUSO**  |
| `battle_engine_formula_rewrite`                   | **OFF**     |
| `battle_simulate_called_from_staging_or_live`     | **OFF**     |
| Pack 84 PSP normalization                          | ✅ preserved |
| Pack 85 PSP ensure                                 | ✅ preserved |
| Pack 86 register guard                             | ✅ preserved |
| Pack 87 starter claim                              | ✅ preserved |
| Pack 88 team formation strict                      | ✅ preserved |
| Pack 89 GET inventory strict                       | ✅ preserved |
| Pack 90 inventory write paths strict               | ✅ preserved |
| Pack 91 inventory frontend consumer migration      | ✅ preserved |
| `release_readiness_claimed`                       | **OFF**     |
| `fake_PASS` / `validator_weakening`               | **OFF**     |

---

## 18. Safety flags (snapshot)

```json
{
  "fake_PASS": false, "validator_weakening": false, "release_readiness_claimed": false,
  "schema_migration_executed": false, "backfill_executed": false,
  "production_user_db_writes": false, "unmarked_test_writes": false,
  "broad_db_writes": false, "currency_write_promotion": false,
  "story_progress_write_promotion": false, "equipment_write_promotion": false,
  "reward_live": false, "progress_live": false,
  "premium_grant": false, "currency_grant": false,
  "s1_to_s2_copy": false, "copy_s1_to_s2_inventory": false,
  "account_wide_fallback_for_server_bound_data": false, "silent_s1_fallback": false,
  "hardcoded_s1_in_writes": false, "false_filter_applied_true": false,
  "legacy_cleanup_executed": false, "destructive_migration": false, "delete_of_real_data": false,
  "player_level_mutation": false, "user_heroes_cross_server_mutation": false,
  "team_route_regression": false, "postqa_d_gates_unlocked": false,
  "battle_engine_formula_rewrite": false, "battle_simulate_called_from_staging_or_live": false
}
```

---

## 19. Dichiarazioni esplicite (non-negoziabili)

- **Inventory Pack 91 preserved** — Pack 91 caveat su `inventory.tsx` (chiamata
  a `/api/user/heroes` senza `server_id`) **risolto** in Pack 92 sweep.
  Verifica: smoke E2E step 12 (`inventory_source=player_server_scoped`).
- **Frontend `/api/user/heroes` server_id sweep COMPLETED** — 8 file
  player-facing migrati; pre-battle-lobby già correct pre-Pack-92.
  Static guard validator PASS.
- **NO broad DB writes** — solo test artifacts marcati `pack_92_test_artifact=true`;
  smoke cleanup automatico nel finally; post-smoke `candidate test users: 0`.
- **NO reward/progress live** — invariato dal Pack 91 (`reward_live=false`,
  `progress_live=false`).
- **NO release readiness claim** — Pack 92 è hardenizzazione loader/sweep,
  non promozione live.
- **NO false `filter_applied=true`** — quando `filter_applied=true` lo
  split (wallet), il filtro (story PSP), o il blocker (equipment deferred)
  sono REALI. Verificato via runtime smoke.
- **NO account-wide fallback per dati server-bound** — frontend con
  `useServerScope` mostra blocker UI se server non selezionato; backend
  legacy path flagged `legacy_account_wide_deprecated`.
- **NO S1→S2 copy** — nessuna copia inventory/story/equipment/currencies
  tra server.
- **NO currency/story/equipment write promotion** — deferiti, piano
  futuro documentato Track J.
- **NO premium grant / NO currency grant**.
- **NO destructive migration / NO schema migration / NO backfill**.
- **NO legacy cleanup execution**.
- **NO POSTQA_D unlock / NO battle_engine rewrite / NO
  `/api/battle/simulate` da staging/live**.
- **NO `fake_PASS` / NO validator weakening** — 1507/29/0/0
  deterministico su 3 run, baseline 29 OPTIONAL preservata, +17 nuove
  Pack 92 tracks tutte PASS.

---

## 20. Deferred blockers & Next step

### Deferred blockers (documentati, NON eseguiti)

1. **Equipment loader strict promotion** — schema migration (backfill
   `server_id` su `user_equipment` docs) richiesta prima della promotion.
2. **Currency spend/write strict scope** — `POST /api/wallet/spend` (NEW)
   + decrement strict path su `/api/item-shop/buy`.
3. **Story progress write strict scope** — `POST /api/story/battle` deve
   essere promosso a strict server-scope.
4. **Equipment equip/unequip/forge write strict scope** — dopo equipment
   loader promotion.
5. **Reward claim ledger live** — non in Pack 92.
6. **Legacy cleanup pre-Pack-86** `user_heroes` account-wide — deferito.

### Next step

- Attendere verifica utente del Pack 92.
- Successivo upload del **Pack 93** (probabile: equipment backfill+loader
  strict, oppure currency spend write strict scope, oppure story
  progress write strict scope).
- Nel frattempo: nessuna esecuzione di legacy cleanup, nessuna promozione
  live di reward/progress, nessuna mutazione di currency/story/equipment
  in scrittura, nessuna release readiness claim.

---

## 21. Sync status

```
local_commit_only            = true
public_push_managed_externally = true
no_remote_available          = true
```

---

## 22. Comando di verifica (riproducibilità)

```bash
# 1) Runtime guard smoke (read-only, cleanup auto)
python3 /app/backend/scripts/smoke_v110_pack_92_runtime_guard_e2e.py
# Atteso: real_smoke_executed=true, required_missing=[]

# 2) Cleanup dry-run (refuse-by-default)
python3 /app/backend/scripts/cleanup_v110_pack_92_test_artifacts.py
# Atteso: candidate test users: 0

# 3) Rollup Pack 92 (16 tracks + summary)
python3 /app/backend/scripts/validate_mega_release_acceleration_92_core_server_scope_megapack_rollup.py
# Atteso: tracks=16/16 verdict=…READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED…

# 4) Master suite 3-run deterministico
for i in 1 2 3; do
  python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | tail -1
done
# Atteso ogni run: Overall: FAIL  (pass=1507, fail=29, miss=0)
```

---

## 23. Post-script — commit hash

```
commit_hash = <da inserire dopo `git commit`>
local_commit_only = true
public_push_managed_externally = true
no_remote_available = true
```

---

*Fine report Pack 92.*
