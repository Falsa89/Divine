# 124_PRE_QA_STABILIZATION_115G_SKILL_ARTIFACT_SEMANTIC_CLEANUP_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_115G_SKILL_ARTIFACT_SEMANTIC_CLEANUP_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-115G): `3804a3e46626d23b24366947d52a6a5595e62120`
- Pack 115G commit:    `ce767d2c2d18d217f7c6ce61173e842aa8c9cf7e`
- Report/self-ref:     `02bf607525c20f87b8ccd4bdd3c16af18cf41c5d`

> **Commit policy**: il commit del Pack 115G segue il vincolo esplicito utente: **MAI `git add -A` / `git add .`**. Tutti i file sono stati aggiunti con `git add -- <path>` esplicito file-by-file.

## Scope / files changed
File modificati:
- `frontend/app/hero-skill-kits-catalog.tsx`  *(UI semantic truth)*
- `backend/scripts/validate_hero_skill_kit_catalog_foundation.py`  *(foundation_draft policy)*
- `backend/routes/artifacts.py`  *(legacy GET neutralization + lock envelope constants)*
- `backend/scripts/run_pre_qa_safety_validator_suite.py`  *(registrazione validator 115G)*

File creati:
- `backend/scripts/validate_pre_qa_stabilization_115g_skill_artifact_semantic_cleanup.py`  *(10 check statici)*
- `docs/divine/124_PRE_QA_STABILIZATION_115G_SKILL_ARTIFACT_SEMANTIC_CLEANUP_FINAL_REPORT.md`  *(questo file)*

**Nessuna modifica sotto `data/design/**`** (verificato via `git status` post-edit: 0 path `data/design/` toccato).

## Decisione `final_numbers` semantics (skill kit)
- **Preservato**: i valori `final_numbers` con `status="foundation_draft"` e `runtime_ready=false` gia' presenti nei cataloghi 5★/6★ (20 + 13 entries).
- **NON revertiti** a `final_numbers=null`.
- **NON riscritti**: il pack non altera i valori numerici di `data/design/hero_skill_kits/*.json`.
- **Trattamento**: dati di **fondazione / balance-preview**, esplicitamente NON final, NON runtime-attached, NON battle-runtime, NON live kit.

### UI semantic truth (Stato bilanciamento card, `hero-skill-kits-catalog.tsx`)
**Before:**
```
• final_numbers: null su tutte le skill
• balance_values_finalized: false
• runtime_attached: false
• do_not_treat_as_live_kit: true
```
**After:**
```
• final_numbers: foundation_draft preview-only
• runtime_ready: false
• balance_values_finalized: false
• runtime_attached: false
• battle_runtime_attached: false
• do_not_treat_as_live_kit: true
⚠️  Solo design/catalogo: NON final balance, NON collegato al battle runtime,
   NON aggancia HP bar / VFX / combat. Trattare come anteprima di
   fondazione, non come kit live.
```

### Foundation validator policy (`validate_hero_skill_kit_catalog_foundation.py`)
**Before:** policy null-only — fail se `final_numbers is not None`.

**After (Pack 115G):**
- `final_numbers=null` consentito (compatibilita' retroattiva con 5★ launch_base).
- `final_numbers` come dict consentito **solo se**:
  - `status == "foundation_draft"`;
  - `runtime_ready is False` (esplicito);
  - nessun flag `runtime/runtime_attached/battle_runtime_attached/live/is_live/final/is_final/finalized/balance_finalized/balance_values_finalized = True`;
  - `status` mai uguale a `runtime/live/final/finalized/ready`.

Esecuzione live: **PASS** sul catalogo corrente (20 entries 5★ + 12 launch_base 6★ + 1 launch_extra_premium 6★ Borea).

## Artifact legacy GET behavior — before/after

### `GET /api/artifacts`
**Before:**
- Dipende da `get_current_user` → DB auth read.
- Legge `db.user_artifacts.find({"user_id": uid})` → ownership read.
- Calcola `effective_buff` per ogni artefatto posseduto (`level_mult`).
- Calcola `total_buffs` aggregati.
- Calcola `set_bonuses` con threshold/buff lookup.
- Restituisce shape `{artifacts: [...], total_buffs, set_bonuses, sets, owned_count, total_count}` — active-looking.

**After (Pack 115G):**
- Handler **senza** dipendenza `get_current_user` (zero DB auth call).
- **Zero** lettura `db.user_artifacts`/`db.user_constellations`/`db.teams`.
- **Zero** calcolo `effective_buff`/`total_buffs`/`equipped_buff`/`equipped_skill`/`set_bonuses`/`level_mult`.
- Restituisce **HTTP 423** + envelope esplicito:
  ```json
  {
    "success": false,
    "locked": true,
    "system": "artifacts",
    "code": "ARTIFACT_LEGACY_GET_NEUTRALIZED_PRE_QA",
    "message": "Endpoint legacy in lock pre-QA. Nessuna lettura DB ownership, nessun calcolo buff. Usare i canonical catalog read-only.",
    "no_db_ownership_read": true,
    "no_effective_buff_calculation": true,
    "no_equipped_buff_calculation": true,
    "no_equipped_skill_calculation": true,
    "no_total_buffs_calculation": true,
    "allowed_now": [
      "GET /api/artifacts/catalog",
      "GET /api/artifacts/catalog/preview"
    ]
  }
  ```

### `GET /api/constellations`
**Before:**
- Dipende da `get_current_user` → DB auth read.
- Legge `db.user_constellations.find({"user_id": uid})` → ownership.
- Legge `db.teams.find_one(...)` → equipped team read.
- Calcola `effective_buff`, `skill_mult`, `equipped_buff`, `equipped_skill`.
- Restituisce shape `{constellations, equipped_id, equipped_buff, equipped_skill}` — active-looking.

**After (Pack 115G):**
- Handler **senza** dipendenza `get_current_user`.
- **Zero** lettura DB ownership/team.
- **Zero** calcolo `effective_buff`/`equipped_buff`/`equipped_skill`/`skill_mult`.
- Restituisce **HTTP 423** + envelope esplicito (`CONSTELLATION_LEGACY_GET_NEUTRALIZED_PRE_QA`), con allowed_now puntato ai canonical artifact catalog read-only.

### Endpoint preservati invariati
- `GET /api/artifacts/catalog` — **HTTP 200**, 19.369 byte response, read-only.
- `GET /api/artifacts/catalog/preview` — **HTTP 200**, 3.423 byte response, read-only.

### POST mutation locks preservati invariati
- `ARTIFACT_MUTATION_LOCK_ENVELOPE` + `ARTIFACT_MUTATION_LOCK_STATUS = 423`
- `CONSTELLATION_MUTATION_LOCK_ENVELOPE`
- 7 route POST locked: `POST /api/artifacts/fuse`, `POST /api/artifacts/pull`, `POST /api/artifacts/pull10`, `POST /api/constellations/equip`, `POST /api/constellations/fuse`, `POST /api/constellations/pull`, `POST /api/constellations/pull10`.

### Curl evidence (esecuzione locale post-restart backend)
```
GET /api/artifacts                  → HTTP 423 (envelope ARTIFACT_LEGACY_GET_NEUTRALIZED_PRE_QA)
GET /api/constellations             → HTTP 423 (envelope CONSTELLATION_LEGACY_GET_NEUTRALIZED_PRE_QA)
GET /api/artifacts/catalog          → HTTP 200 (19.369 bytes, read-only)
GET /api/artifacts/catalog/preview  → HTTP 200 (3.423 bytes, read-only)
```

## Validator results

### `python3 backend/scripts/validate_hero_skill_kit_catalog_foundation.py`
**PASS**:
```
PASS: RM1.26-A hero skill kit catalog foundation validated
- 5★ launch_base entries: 20
- 6★ launch_base entries: 12
- 6★ extra premium entries: 1
- total 6★ catalog entries: 13
- skill slot progression: ok
- runtime_attached: false
- balance_values_finalized: false
```

### `python3 backend/scripts/validate_pre_qa_stabilization_115g_skill_artifact_semantic_cleanup.py`
**PASS** (10/10 check):
1. `[1] UI no stale "final_numbers: null" copy OK`
2. `[2] UI foundation_draft / preview-only / runtime_ready=false semantic OK`
3. `[3] Foundation validator semantic (foundation_draft + runtime_ready false) OK`
4. `[4] foundation validator exec PASS (live) OK`
5. `[5] 5★/6★ catalogs no runtime-ready / no live status OK`
6. `[6] /artifacts and /constellations legacy GET neutralized OK`
7. `[7] canonical /artifacts/catalog and /artifacts/catalog/preview preserved OK`
8. `[8] POST mutation locks preserved (constants + 7 routes) OK`
9. `[9] pack 115G no out-of-scope runtime imports OK`
10. `[10] no data/design write in pack-115G scripts OK`

### `python3 backend/scripts/run_pre_qa_safety_validator_suite.py`
**PASS — 15/15** (verdict: `PRE_QA_SAFETY_SUITE_PASS`):

| # | Entry | Stato |
|---|---|---|
| 1  | Validator 113 HomeOverflow | PASS |
| 2  | Smoke 113 HomeOverflow | PASS |
| 3  | Validator 114 Home Routes | PASS |
| 4  | Smoke 114 Home Routes | PASS |
| 5  | Rollup 114 Home Routes | PASS |
| 6  | Validator 114B Gacha/Combat/Lobby Guard | PASS |
| 7  | Validator 115A P0 Hard Gates | PASS |
| 8  | Smoke 115A P0 Hard Gates (runtime) | PASS *(backend up)* |
| 9  | Validator 115B Progression/Forge/Items | PASS |
| 10 | Smoke 115B Progression/Forge/Items (runtime) | PASS *(backend up)* |
| 11 | Validator 115C Auth/Server Scope | PASS |
| 12 | Validator 115D Screen-Entry/Deeplink Guard | PASS |
| 13 | Validator 115E Combat/Tower Legacy Hardening | PASS |
| 14 | Validator 115F Repo Hygiene & Validator Truth | PASS |
| 15 | **Validator 115G Skill/Artifact Semantic Cleanup** | **PASS** |

Totali: 15 · PASS: 15 · FAIL: 0 · SKIPPED: 0 · backend_up: true · `SKIPPED_BACKEND_DOWN` non applicato.

JSON path: `backend/reports/pre_qa_safety_validator_suite_latest.json`.

## Safety invariants
- DB writes: **0** (validator/smoke statici; le handler legacy GET non leggono piu' alcun DB).
- `data/design/**`: **untouched** (verifica statica + `git status` post-edit).
- `battle_engine.py`: **untouched**.
- `combat.tsx` / Tower runtime: **untouched**.
- Character Bible: **untouched**.
- skill catalog data files (`hero_skill_kits/*.json`): **untouched** (read-only).
- gacha rates / banner config: **untouched**.
- gacha live: **false** (env flag invariato).
- reward live: **false**.
- IAP/payment: **false**.
- Artifact live activation: **false** (legacy GET ora HTTP 423 locked).
- Artifact inventory live apply: **false**.
- Artifact/constellation gacha activation: **false** (POST mutation locks invariati).
- Battle Power: **non implementato** (verificato dal validator check [9]).
- Chat/Bot cleanup: **non implementato** (verificato dal validator check [9]).
- Red Dot: **non implementato** (verificato dal validator check [9]).
- 5★ true ultimate constraints: **preservati** (foundation validator continua a verificare `expected_slots == ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2"]` per 5★ — niente `ultimate` slot, no semantica true-ultimate).
- Borea semantica catalog-only/pending/hidden: **preservata** (foundation validator continua a verificare `release_group == "launch_extra_premium"` per Borea, e `divine_weapon_id`/`divine_weapon_name` obbligatori).

## Out-of-scope verification
Verifica statica check [9] del validator 115G:
- Nessun import di `battle_engine`, `gacha_runtime`, `reward_engine`, `red_dot_runtime`, `battle_power_runtime`, `chat_bot_runtime`, `character_bible_runtime` negli script del pack 115G.
- Nessuna scrittura su `data/design/**` (check [10]).

## Deferred (post-115G roadmap)
- **116A — Battle Power foundation / Menu Power 0**: foundation per il calcolo di Battle Power; richiede una pass di balance/balance preview *separata*, non parte di 115G.
- **116B — Chat/Bot quality + legacy chat cleanup**: cleanup chat/bot UI e routing, *separato*.
- **116C — Red Dot notification badge foundation**: badge di notifica, *separato* (NB: nessuna push notification implementata o suggerita autonomamente).

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 116A** prima del re-audit esplicito.
