# PACK 130 — LOBBY LAUNCH CONTEXT + REAL PLAYER SNAPSHOT

**Verdetto finale (prudente, onesto, no fake PASS):**

```
PACK_130_LOBBY_LAUNCH_CONTEXT_REAL_PLAYER_SNAPSHOT_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED
```

**Device QA status:** `BLOCKED`
**Next required pack:** `PACK 131 — Combat Consumes Real Snapshot + Post-Battle Preview Safe`

---

## 1. Git anchors

| Campo | Valore |
|---|---|
| Starting SHA | `872010a3b5694684607673efe3ed2328a79e041c` |
| Pack 129 close anchor | `bcd72f45751d875edfc2d65a6a4b5dcbce966356` |
| Final SHA (Pack 130 content commit auditato da Codex Web) | `2f490421e07fc119e17000a29628b0ffbbc77d19` |
| Branch | `main` |

## 2. Git status

### Pre-Pack 130
```text
(working tree clean)
```

### Post-implementation (pre-commit)
```text
 M backend/server.py
 M backend/scripts/validate_pack_128_no_pack129_130_131_leak.py
 M backend/scripts/validate_pack_129_no_pack130_131_132_133_leak.py
?? backend/helpers/lobby_launch_context.py
?? backend/helpers/real_player_snapshot.py
?? backend/routes/v130_lobby_launch_context.py
?? backend/scripts/reports/pack_130_*_report.json (×11)
?? backend/scripts/run_pack_127_128_129_130_safety_suite.py
?? backend/scripts/validate_pack_130_*.py (×11)
?? data/design/system_safety/pack_130_lobby_launch_context_marker.json
?? data/design/system_safety/pack_130_real_player_snapshot_marker.json
?? docs/divine/532_PACK_130_LOBBY_LAUNCH_CONTEXT_REAL_PLAYER_SNAPSHOT_FINAL_REPORT.md
```

## 3. Files changed (32 totali)

### Modificati (3)
- `backend/server.py` — diff minimo: 1 import + 1 `include_router` per Pack 130 (commentato)
- `backend/scripts/validate_pack_128_no_pack129_130_131_leak.py` — rimosso `pack_130/PACK_130` da `FORBIDDEN_PATTERNS` (Pack 130 è pack corrente/chiuso; validator continua a bloccare Pack 131+)
- `backend/scripts/validate_pack_129_no_pack130_131_132_133_leak.py` — rimosso `pack_130/PACK_130` da `FORBIDDEN` (stesso pattern)

### Creati (29 nuovi file)
- **Backend helpers (2):** `helpers/real_player_snapshot.py`, `helpers/lobby_launch_context.py`
- **Backend route (1):** `routes/v130_lobby_launch_context.py`
- **Markers (2):** `pack_130_lobby_launch_context_marker.json`, `pack_130_real_player_snapshot_marker.json`
- **Validators Python (11):** vedi §13
- **Reports JSON (11):** §13 (1 per validator)
- **Suite runner (1):** `run_pack_127_128_129_130_safety_suite.py`
- **Report finale MD (1):** questo file

Totale = 2 + 1 + 2 + 11 + 11 + 1 + 1 = **29 nuovi file** + 3 modificati = **32 file totali nel commit Pack 130**.

## 4. Lobby Launch Context summary (Track A)

**Endpoint:** `GET /api/lobby/launch-context/preview?mode=training&server_id=s1`

**Properties (tutte ENFORCED static + unit-runtime):**
- Auth-required (Bearer JWT HS256, stesso schema `server.get_current_user`)
- Server-scoped via Pack 129 `server_ready_guard.check_server_ready(db, user_id, server_id)`
- Read-only (GET → bypassa Pack 128 mutation middleware naturalmente)
- Mode allowlist: `training, story, boss, tower, event, arena`
- Structured errors via Pack 129 `build_structured_detail`
- **Zero DB write** (verificato static + helper isolation)
- **Zero reward / progress / inventory / economy mutation**
- **Zero battle_engine execution**

**Response success (campi):**
```json
{
  "ok": true,
  "launch_context_id": "<sha256[:24]>",
  "mode": "training",
  "server_id": "s1",
  "user_id": "<uuid>",
  "player_snapshot": { "source": "server_scoped_team_formation", ... },
  "enemy_snapshot_status": "DEFERRED_TO_PACK_131_OR_LATER",
  "combat_consumption_status": "COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131",
  "reward_status": "DISABLED",
  "progress_status": "DISABLED",
  "device_qa_status": "BLOCKED",
  "pack_origin": "PACK_130",
  "launch_context_hash": "<sha256[:16]>"
}
```

## 5. Real Player Snapshot summary (Track B)

**Helper:** `backend/helpers/real_player_snapshot.py`

**Snapshot source:** `server_scoped_team_formation` — legge esclusivamente:
- `player_server_profiles` filtered by `{user_id, server_id}` → team_formation
- `user_heroes` filtered by `{user_id, server_id, user_hero_id|id IN [...]}` → stats player-side
- `heroes` (canonical) → display_name, rarity, element, role, faction, asset_key, asset_status

**Hero sanitization (`_sanitize_hero`):**
- Espone solo `SAFE_HERO_FIELDS` (campi esposti totali nel marker: 15; `SAFE_HERO_FIELDS` base nel codice: 13 + `snapshot_status`/`slot` aggiunti dal builder)
- Esclude `FORBIDDEN_HERO_FIELDS` (drop_table, reward_rate, admin_flags, debug, secret, battle_power_client_computed, raw_stats_authoritative, gacha_rate, shop_price, economy_internal)
- Esclude eroi `pending_assets` / `pending_contract` (Borea hidden invariant preservato)
- Esclude `FORBIDDEN_HERO_KEYS = ('greek_borea',)`
- `battle_power_status: DEFERRED` (no battle power calculation — Pack 131+)
- `player_snapshot_hash` = sha256[:16] deterministico per debug

**Casi limite gestiti:**
- PSP missing → `SERVER_PROFILE_MISSING`
- team_formation None → `TEAM_FORMATION_MISSING`
- team_formation `[]` → `TEAM_FORMATION_EMPTY`
- user_heroes 0 ownership → `TEAM_HERO_NOT_OWNED` (per hero)
- DB exception → `SNAPSHOT_BUILD_FAILED`

## 6. DB write scope

```
NONE
```

Verificato da validator `validate_pack_130_launch_context_no_db_writes.py`: 3 file Pack 130 (route + 2 helpers) scansionati per `update_*`, `insert_*`, `delete_*`, `replace_one`, `find_one_and_update`, `bulk_write`, `create_index` → **0 violations**.

## 7. Structured Errors summary

**Adozione Pack 129 contract:**
- `build_structured_detail()` usato per **ogni** errore Pack 130
- `state_to_structured_code()` per integrazione `server_ready_guard`

**Codici emessi:**
- Da Pack 129: `AUTH_REQUIRED`, `SERVER_CONTEXT_REQUIRED`, `SERVER_CONTEXT_INVALID`, `SERVER_PROFILE_MISSING`, `SERVER_SCOPE_UNAVAILABLE`, `SERVER_MISMATCH`
- Da Pack 130 (nuovi nel helper): `LOBBY_MODE_INVALID`, `TEAM_FORMATION_MISSING`, `TEAM_FORMATION_EMPTY`, `SNAPSHOT_BUILD_FAILED`, `COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131`

## 8. Frontend changes summary

**ZERO modifiche a `frontend/app/**`** — verificato da validator `validate_pack_130_frontend_lobby_integration_safe.py` via `git diff bcd72f45..HEAD --name-only | grep "^frontend/app/"` → 0 risultati.

Frontend lobby integration **VALIDATED_ONLY**: l'endpoint `GET /api/lobby/launch-context/preview` è disponibile ma **nessuna schermata frontend lo consuma ancora** (deferred a Pack 131+). Decisione presa per minimizzare rischio scope drift e preservare UX.

## 9. Pack 128 middleware interaction

- Pack 130 route è **GET only** → bypassa naturalmente il middleware Pack 128 (che intercetta solo `POST/PUT/PATCH/DELETE`)
- **Nessuna modifica all'allowlist Pack 128** necessaria
- Validator `validate_pack_130_pack128_mutation_guard_interaction.py` → PASS

## 10. Runtime smoke results

| Test | Stato |
|---|---|
| `GET /api/health` post-mount router Pack 130 | **HTTP 200** ✅ |
| `GET /api/lobby/launch-context/preview` no auth | **HTTP 401 "Token mancante"** ✅ (auth gate) |
| `GET /api/lobby/launch-context/preview` con fake token | **HTTP 401 "Token non valido"** ✅ |
| Unit-runtime no_auth → `AUTH_REQUIRED` | ✅ |
| Unit-runtime invalid mode → `LOBBY_MODE_INVALID` | ✅ |
| Unit-runtime missing server → `SERVER_CONTEXT_REQUIRED` | ✅ |
| Unit-runtime success path (DB mock) → ok=True, snapshot_team_size=1, combat_consumption=`COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131`, reward=DISABLED, progress=DISABLED, device_qa=BLOCKED | ✅ |
| Unit-runtime snapshot helper: 3 DB ops captured, **tutte server-scoped** (`user_id` + `server_id` co-presenti) | ✅ |
| Full HTTP smoke con JWT QA reale | **NOT_EXECUTED** (Pack 132) |

## 11. Validators added/updated and results (Pack 130 = 11)

| # | Validator | Status |
|---|---|---|
| 1 | `validate_pack_130_lobby_launch_context_contract.py` | PASS (static + unit-runtime, 4 smoke pairs verificate) |
| 2 | `validate_pack_130_real_player_snapshot_server_scope.py` | PASS (3 DB ops, tutti server-scoped) |
| 3 | `validate_pack_130_launch_context_no_db_writes.py` | PASS (0 write ops in 3 file) |
| 4 | `validate_pack_130_snapshot_no_client_trust.py` | PASS (GET-only, no BaseModel body, helper sanitized) |
| 5 | `validate_pack_130_launch_context_structured_errors.py` | PASS (6 codes + server_ready adoption verified) |
| 6 | `validate_pack_130_pack128_mutation_guard_interaction.py` | PASS (Pack 130 route is GET, allowlist mod not needed) |
| 7 | `validate_pack_130_frontend_lobby_integration_safe.py` | PASS (zero frontend/app changes) |
| 8 | `validate_pack_130_no_combat_consumes_snapshot.py` | PASS (combat.tsx/battle_engine/battle_core NOT importing Pack 130 helpers) |
| 9 | `validate_pack_130_no_rewards_no_progress.py` | PASS (14 forbidden reward/progress patterns checked) |
| 10 | `validate_pack_130_no_pack131_132_133_leak.py` | PASS |
| 11 | `validate_pack_130_forbidden_areas_untouched.py` | PASS (git diff `bcd72f45..HEAD`) |

### Honest FAIL durante iterazione (corretti)
- Pack 128 validator `validate_pack_128_no_pack129_130_131_leak.py` rilevava i file Pack 130 come leak (Pack 130 è pack corrente). Aggiornato: rimosso `pack_130/PACK_130` da `FORBIDDEN_PATTERNS`; continua a bloccare Pack 131+ — stesso pattern già applicato in Pack 129 per il proprio successore.

## 12. Suite results

```
backend/scripts/run_pack_127_128_129_130_safety_suite.py
TOTAL: 38 | PASS: 38 | FAIL: 0
```
- Pack 127: 8/8
- Pack 128: 9/9
- Pack 129: 10/10
- Pack 130: 11/11

**Nessun validator precedente indebolito**, nessun test rimosso, nessuna REQUIRED → OPTIONAL.

## 13. Forbidden areas untouched

Validator `validate_pack_130_forbidden_areas_untouched.py` → PASS su `git diff bcd72f45..HEAD`:

| Area | Stato |
|---|---|
| `backend/battle_engine.py`, `battle_core.py`, `game_systems.py` | ✅ Intatti |
| `backend/.env` | ✅ Intatto |
| `backend/routes/v96_team_formation.py` (Pack 125) | ✅ Intatto |
| `data/design/heroes_master.json` (Character Bible) | ✅ Intatto |
| `data/design/final_numbers/**` | ✅ Intatto |
| `frontend/app/**` (compreso `combat.tsx`, `story.tsx`) | ✅ Intatto |
| `frontend/assets/audio/**`, `images/**` | ✅ Intatto |
| Supervisor configs | ✅ Intatto |
| Gacha/Economy/Reward/Shop/VIP/BP/Mail logic | ✅ Intatto |
| DB schema / migrations | ✅ Zero |

## 14. Known gaps (per Pack 131+)

| # | Gap | Owner |
|---|---|---|
| G1 | Frontend lobby integration non eseguita (zero frontend/app/** changes) | Pack 131+ (mount lobby screen consumer) |
| G2 | Battle Power status `DEFERRED` — no derived source of truth | Pack 131+ |
| G3 | Combat runtime non consuma snapshot Pack 130 | **Pack 131** (target principale) |
| G4 | Full HTTP smoke con JWT QA reale | Pack 132 |
| G5 | Pack 128 deeplink helper non mountato in `_layout.tsx` | Pack 131+ carry-over |
| G6 | 26 mutating-GET hardening runtime | Pack 128.x / Pack 131+ |
| G7 | Catalog seed startup env gate | Pack 128.x / Pack 131+ |
| G8 | `QA_TEAM_SAVE_ENABLED` non set nel pod | MANUAL Pack 132 |

## 15. Device QA status

```
DEVICE_QA_STATUS: BLOCKED
```
Confermato in entrambi i marker Pack 130 + tutti i marker precedenti.

## 16. Next required pack

**`PACK 131 — Combat Consumes Real Snapshot + Post-Battle Preview Safe`**

Pack 131 dovrà:
1. Far consumare a `combat.tsx` lo snapshot di `GET /api/lobby/launch-context/preview`
2. Implementare post-battle preview safe (NO reward, NO progress, NO claim)
3. Sostituire il path mutating del legacy battle engine per `/api/battle/simulate` con il real snapshot path
4. Mantenere Device QA BLOCKED

---

## 17. Categorizzazione `ENFORCED / VALIDATED_ONLY / NOT_EXECUTED / FAIL`

| Controllo | Categoria | Evidenza |
|---|---|---|
| Backend route GET /api/lobby/launch-context/preview presente e mounted | **ENFORCED** | Backend health 200, auth gate 401 OK |
| Server-scope (tutti DB lookup con `user_id + server_id`) | **ENFORCED** | Validator 2: 3 DB ops captured, tutti server-scoped |
| Read-only (no DB write) | **ENFORCED** | Validator 3: 11 write patterns checked, 0 violations |
| Sanitization snapshot (forbidden fields excluded) | **ENFORCED** | Helper code + validator 4 |
| Borea hidden invariant preservato | **ENFORCED** | `greek_borea` in FORBIDDEN_HERO_KEYS + pending_assets exclusion |
| Structured errors Pack 129 contract adottato | **ENFORCED** | Validator 5: build_structured_detail + state_to_structured_code |
| GET-only → bypassa Pack 128 mutation middleware | **ENFORCED** | Validator 6 |
| Frontend lobby integration | **VALIDATED_ONLY** | Validator 7: zero frontend/app changes (decisione safety) |
| Combat NON consuma snapshot | **ENFORCED** | Validator 8: combat.tsx/battle_engine/battle_core NOT importing Pack 130 helpers |
| No reward / progress / economy / inventory | **ENFORCED** | Validator 9: 14 patterns, 0 violations |
| No Pack 131/132/133 file leak | **ENFORCED** | Validator 10 |
| Forbidden areas untouched | **ENFORCED (git diff)** | Validator 11 |
| Full HTTP smoke autenticato | **NOT_EXECUTED** | Pack 132 |
| Battle Power calc | **DEFERRED** | Pack 131+ |
| Combat consumption del snapshot | **DEFERRED_TO_PACK_131** | esplicito nel response field |
| Suite Pack 127+128+129+130 | **ENFORCED** | 38/38 PASS |
| Fake PASS | **FAIL = 0** | 1 FAIL onesto (Pack 128 validator pack_130 leak) corretto |

---

_Report generato senza fake PASS. Tutti i numeri/path verificabili in `backend/scripts/reports/pack_130_*_report.json` e nei marker `data/design/system_safety/pack_130_*.json`. Suite report locale `backend/reports/pack_127_128_129_130_safety_suite_*.json` è artefatto NON tracciato; riproducibilità garantita rieseguendo lo script._
