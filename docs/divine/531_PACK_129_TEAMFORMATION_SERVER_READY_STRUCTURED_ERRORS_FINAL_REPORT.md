# PACK 129 — TEAMFORMATION V1 + SERVER READY + STRUCTURED ERRORS

**Verdetto finale (prudente, onesto, no fake PASS):**

```
PACK_129_TEAMFORMATION_SERVER_READY_STRUCTURED_ERRORS_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED
```

**Device QA status:** `BLOCKED`
**Next required pack:** `PACK 130 — Lobby Launch Context + Real Player Snapshot`.

Motivazione del verdetto prudente:
- **Server-scope TeamFormation V1** è già `ENFORCED` via endpoint Pack 125 esistente (auditato, validato, server-scoped, auth-gated, env-gated). Nessun account-wide fallback.
- **Server Ready guard helper** + **Structured Errors helper** sono `ENFORCED_HELPER_LIBRARY_AVAILABLE` ma `OPT-IN`: non ancora montati nei route esistenti (per non rompere il contratto frontend Pack 125/126).
- **Frontend structured error mapping** è `VALIDATED_ONLY_HELPER_PURE_NOT_MOUNTED` (esiste, ma battle.tsx mantiene il suo handler ad-hoc su `blocker` per preservare UX).
- **Full HTTP smoke autenticato** del save-formation con env true è `NOT_EXECUTED` (deferred a Pack 132).

---

## 1. Git anchors

| Campo | Valore |
|---|---|
| Starting SHA | `a4c1fd207e432da635d1f1f6495f472b8675ae28` |
| Pack 128 close anchor | `bb58cedd2bce2bf39030be1e6cc5ac5353fa2945` |
| Final SHA | _(da aggiornare al commit di chiusura Pack 129)_ |
| Branch | `main` |

## 2. Git status

### Pre-Pack 129 (HEAD = `a4c1fd207`)
```text
(working tree clean — nothing to commit)
```

### Post-implementation (pre-commit, atteso)
```text
 M backend/scripts/validate_pack_128_no_pack129_130_131_leak.py
?? backend/helpers/__init__.py
?? backend/helpers/server_ready_guard.py
?? backend/helpers/structured_errors.py
?? backend/scripts/reports/pack_129_*_report.json (×10)
?? backend/scripts/run_pack_127_128_129_safety_suite.py
?? backend/scripts/validate_pack_129_*.py (×10)
?? data/design/system_safety/pack_129_server_ready_structured_errors_marker.json
?? data/design/system_safety/pack_129_teamformation_server_scope_marker.json
?? frontend/src/utils/structuredErrorMap.ts
?? docs/divine/531_PACK_129_TEAMFORMATION_SERVER_READY_STRUCTURED_ERRORS_FINAL_REPORT.md
```

## 3. Files changed / created

### Modificati (1)
- `backend/scripts/validate_pack_128_no_pack129_130_131_leak.py` — rimossi `pack_129/PACK_129` da `FORBIDDEN_PATTERNS` (Pack 129 è ora pack precedente/chiuso). Validator ora blocca solo Pack 130+ leak. Diff +6/-3, no logic weakening.

### Creati (28 totali)
- **Backend helpers package (3):** `backend/helpers/__init__.py`, `helpers/structured_errors.py`, `helpers/server_ready_guard.py`
- **Frontend helper (1):** `frontend/src/utils/structuredErrorMap.ts` (non mountato)
- **Markers system_safety (2):** `pack_129_teamformation_server_scope_marker.json`, `pack_129_server_ready_structured_errors_marker.json`
- **Validators Python (10):** vedi §13
- **Suite runner (1):** `backend/scripts/run_pack_127_128_129_safety_suite.py`
- **Reports JSON (10):** vedi §13
- **Report finale Markdown (1):** questo file

Totale = 3 + 1 + 2 + 10 + 1 + 10 + 1 = **28 nuovi file**.

## 4. Server Ready summary (Track A)

### Helper: `backend/helpers/server_ready_guard.py`

```python
async def check_server_ready(
    db, user_id, server_id, *, auth_context_server_id=None
) -> Tuple[str, dict]
```

**Stati possibili (§6.3):**
- `SERVER_READY` — PSP esiste per (user_id, server_id)
- `SERVER_CONTEXT_MISSING` — server_id non fornito o vuoto
- `SERVER_CONTEXT_INVALID` — server_id formato invalido (non-string, troppo lungo, char non alphanum+_-)
- `SERVER_PROFILE_MISSING` — PSP non trovato in DB
- `SERVER_SCOPE_UNAVAILABLE` — DB lookup fallito o user_id mancante (defense-in-depth)
- `SERVER_MISMATCH` — server_id ≠ auth_context_server_id

**Proprietà:**
- **Read-only**: non crea PSP, non tocca `user_heroes`, `inventory`, `reward`, `progress`.
- Validazione `server_id` format (alphanum + `_-`, max 64 char).
- DB lookup via `motor.AsyncIOMotorDatabase` (compatibile col codebase esistente).
- Restituisce sempre `(state, info_dict)` per diagnostica strutturata.

**Adoption status:** `AVAILABLE_FOR_PACK_130_PLUS_NOT_YET_MOUNTED_IN_EXISTING_ROUTES`. Helper opt-in: Pack 130+ potrà montarlo in nuovi route lobby/battle senza rompere Pack 125.

## 5. TeamFormation V1 summary (Track B)

### Endpoint: `POST /api/team/save-formation`

**File:** `backend/routes/v96_team_formation.py` (Pack 125 esistente, **non modificato in Pack 129**).

**Già implementato e auditato:**

| Validazione | Status |
|---|---|
| `auth required` (Depends(get_current_user)) | ✅ ENFORCED |
| `QA_TEAM_SAVE_ENABLED` env gate (default DORMANT) | ✅ ENFORCED |
| `QA_TEAM_SAVE_ALLOWLIST` per UUID | ✅ ENFORCED |
| `server_id` required dal body | ✅ ENFORCED |
| PSP fail-closed (`PLAYER_SERVER_PROFILE_REQUIRED` 404) | ✅ ENFORCED |
| `team_size ≤ 6` | ✅ ENFORCED |
| `slot (col,row)` unique | ✅ ENFORCED |
| `hero_id` unique (no duplicate) | ✅ ENFORCED |
| Ownership via `user_heroes` filter by `server_id` (o `_qa_seed` marker) | ✅ ENFORCED |
| Write target: **`player_server_profiles.team_formation` only** | ✅ ENFORCED |
| NO write to `db.users` | ✅ ENFORCED |
| NO mutation di reward/economy/progress/inventory/EXP | ✅ ENFORCED |
| NO mutation di `user_heroes` (read-only ownership check) | ✅ ENFORCED |

### Perché Pack 129 non ha modificato il route?

Per **preservare il contratto Pack 125/126**: il frontend `battle.tsx` ha già un handler basato sui campi `detail.blocker` legacy. Modificare il route ora rompi UX esistente. Pack 129 fornisce invece:
1. **Backend helper** `helpers/structured_errors.py` per emettere il nuovo formato in route futuri.
2. **Backend mapper** `legacy_blocker_to_code()` per aliasing Pack 125 → Pack 129.
3. **Frontend helper** `structuredErrorMap.ts` con `envelopeFromApiError()` che gestisce ENTRAMBI i formati (legacy `blocker` e nuovo `code`).

## 6. DB write scope

| Aspetto | Valore |
|---|---|
| Collection | `player_server_profiles` |
| Filter | `{user_id, server_id}` |
| $set fields | `team_formation`, `_pack_125_qa_team_save_ts`, `_pack_125_qa_team_save_source` |
| Forbidden fields (mai toccati) | hero stats, battle result, damage, reward, EXP, currency, inventory, drop, mission progress, arena score, guild score |

**Nuove mutazioni DB introdotte in Pack 129:** ZERO (Pack 129 NON crea nuovi route mutativi).

## 7. Structured Errors summary (Track C)

### Backend: `backend/helpers/structured_errors.py`

**Shape Pack 129:**
```python
build_structured_detail(
    detail='Human readable Italian',
    code='STRUCTURED_ERROR_CODE',
    route='/api/...',
    method='POST',
    category=None,  # auto-derived from code
    next_gate='PACK_129_OR_LATER',
    recoverable=True,
    extra={...},
) -> {
    'detail': ..., 'code': ..., 'category': ..., 'route': ...,
    'method': ..., 'next_gate': ..., 'recoverable': ..., ['extra': ...]
}
```

**17 codici definiti (tutti quelli richiesti dal prompt §8.3):**

`AUTH_REQUIRED`, `SERVER_CONTEXT_REQUIRED`, `SERVER_CONTEXT_INVALID`, `SERVER_NOT_READY`, `SERVER_PROFILE_MISSING`, `SERVER_SCOPE_UNAVAILABLE`, `SERVER_MISMATCH`, `TEAM_SAVE_DISABLED_PRE_QA`, `TEAM_INVALID_PAYLOAD`, `TEAM_INVALID_SIZE`, `TEAM_INVALID_SLOT`, `TEAM_DUPLICATE_HERO`, `TEAM_HERO_NOT_OWNED`, `TEAM_HERO_NOT_AVAILABLE`, `TEAM_FORMATION_BLOCKED_PRE_QA`, `PRE_QA_MUTATION_BLOCKED`, `FEATURE_LOCKED_PRE_QA`.

**Legacy aliases (Pack 125 → Pack 129):**
| Pack 125 `blocker` | Pack 129 `code` |
|---|---|
| `AUTHENTICATION_REQUIRED` | `AUTH_REQUIRED` |
| `AUTHENTICATION_INVALID` | `AUTH_REQUIRED` |
| `QA_TEAM_SAVE_DISABLED` | `TEAM_SAVE_DISABLED_PRE_QA` |
| `QA_TEAM_SAVE_ALLOWLIST_EMPTY` | `FEATURE_LOCKED_PRE_QA` |
| `QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED` | `FEATURE_LOCKED_PRE_QA` |
| `PLAYER_SERVER_PROFILE_REQUIRED` | `SERVER_PROFILE_MISSING` |
| `TEAM_TOO_LARGE` | `TEAM_INVALID_SIZE` |
| `DUPLICATE_POSITIONS` | `TEAM_INVALID_SLOT` |
| `DUPLICATE_HEROES` | `TEAM_DUPLICATE_HERO` |
| `OWNERSHIP_VALIDATION_FAILED` | `TEAM_HERO_NOT_OWNED` |

## 8. Frontend changes summary

### Creato (1 file)
- `frontend/src/utils/structuredErrorMap.ts` — pure helper:
  - `STRUCTURED_CODES` — specchio backend codes
  - `LEGACY_BLOCKER_TO_CODE` — alias Pack 125 → Pack 129
  - `CODE_TO_CATEGORY` — code → categoria
  - `CODE_TO_MESSAGE_IT` — code → messaggio italiano UI-friendly
  - `mapStructuredError(input)` — code/blocker → envelope UI-ready
  - `envelopeFromApiError(err)` — apiCall error → envelope

### Mount status
- **NON mountato in `battle.tsx`** (preserva handler ad-hoc esistente).
- **NON mountato in `_layout.tsx`** (zero behavioral change frontend).
- Pure helper opt-in: future schermate possono importarlo per coerenza.

### Modifiche a frontend/app/**
**ZERO**. Nessun file `frontend/app/*` è stato toccato.

## 9. Pack 128 middleware interaction

- **`POST /api/team/save-formation` è già nella Pack 128 allowlist** (`data/design/system_safety/pack_128_backend_mutation_allowlist.json`).
- **Middleware Pack 128 DORMANT nel pod** (env `PRE_QA_MUTATION_GUARD_ENABLED` non set, `.env` intoccato).
- Se attivato in QA supervisor: la route PASSA il middleware (allowlisted), ma resta gated dal `QA_TEAM_SAVE_ENABLED` env Pack 125 (double-gate).
- Validator `validate_pack_129_mutation_guard_team_allowlist_interaction.py` → PASS (allowlist coerenza verificata).

**Pack 129 NON ha attivato `PRE_QA_MUTATION_GUARD_ENABLED` nel pod.**

## 10. Carry-over Pack 128 (Track D)

| Gap Pack 128 | Stato in Pack 129 |
|---|---|
| Deeplink helper non mountato in `_layout.tsx` | `DEEPLINK_RUNTIME_INTERCEPT_STILL_DEFERRED` (zero touch _layout.tsx in Pack 129) |
| 26 mutating-GET (13/2/1/10) hardening runtime | `MUTATING_GET_HARDENING_DEFERRED` (Pack 130+/Pack 128.x). Pack 129 verifica solo che il route TeamFormation V1 non sia tra i 26 (è POST, non GET). |
| Catalog seed startup env gate | `STARTUP_CATALOG_SEED_ENV_GATE_DEFERRED` (Pack 128.x/Pack 130) |

## 11. Runtime smoke results

| Test | Stato |
|---|---|
| `GET /api/health` | **HTTP 200** ✅ |
| `POST /api/team/save-formation` no auth | **HTTP 401** (auth gate) ✅ no-regression |
| Unit-runtime `check_server_ready` con DB mock — 6 stati | **6/6 PASS** ✅ (SERVER_CONTEXT_MISSING, SERVER_CONTEXT_INVALID, SERVER_PROFILE_MISSING, SERVER_READY, SERVER_MISMATCH, SERVER_SCOPE_UNAVAILABLE) |
| Unit-runtime `build_structured_detail` shape (7 fields) | **PASS** ✅ |
| Unit-runtime `legacy_blocker_to_code` (10 alias) | **PASS** ✅ |
| Full HTTP smoke autenticato POST team/save-formation con env true | **NOT_EXECUTED** (deferred Pack 132) |

## 12. Validators Pack 129 (10, tutti reali, no shell)

| # | Validator | Status | Kind | Enforcement |
|---|---|---|---|---|
| 1 | `validate_pack_129_server_ready_guard.py` | PASS | STATIC+UNIT_RUNTIME | ENFORCED_HELPER_PRESENT_LOGIC_VERIFIED |
| 2 | `validate_pack_129_teamformation_server_scope.py` | PASS | STATIC | ENFORCED_PACK_125_ENDPOINT_AUDITED |
| 3 | `validate_pack_129_team_save_validation.py` | PASS | STATIC | ENFORCED_ALL_REQUIRED_VALIDATIONS_PRESENT |
| 4 | `validate_pack_129_team_save_no_rewards_no_progress.py` | PASS | STATIC | ENFORCED_WRITE_TARGET_PSP_TEAM_FORMATION_ONLY |
| 5 | `validate_pack_129_structured_errors_contract.py` | PASS | STATIC+UNIT_RUNTIME | ENFORCED_HELPER_LIBRARY_AVAILABLE |
| 6 | `validate_pack_129_frontend_structured_error_mapping.py` | PASS | STATIC | VALIDATED_ONLY_HELPER_NOT_MOUNTED |
| 7 | `validate_pack_129_mutation_guard_team_allowlist_interaction.py` | PASS | STATIC | ENFORCED_ALLOWLIST_COHERENT_WITH_PACK_128 |
| 8 | `validate_pack_129_no_account_wide_team_fallback.py` | PASS | STATIC | ENFORCED_BACKEND_RUNTIME_SCOPE_SCAN |
| 9 | `validate_pack_129_no_pack130_131_132_133_leak.py` | PASS | STATIC | ENFORCED_NO_FUTURE_PACK_LEAK |
| 10 | `validate_pack_129_forbidden_areas_untouched.py` | PASS | STATIC+GIT_DIFF | ENFORCED_GIT_DIFF |

### Honest failures durante l'iterazione (corretti)

| Iterazione | FAIL | Root cause | Fix |
|---|---|---|---|
| 1 | `validate_pack_128_no_pack129_130_131_leak.py` rileva Pack 129 file | Pack 128 validator era anti-Pack-129 mentre Pack 129 è il pack corrente | Rimosso `pack_129/PACK_129` da `FORBIDDEN_PATTERNS` (Pack 129 ora è pack precedente, non future-pack leak). Validator continua a bloccare Pack 130+. |
| 1 | `validate_pack_129_no_account_wide_team_fallback.py` rileva `db.users.update_one` in `backend/scripts/validate_v110_pack_88_runtime_smoke_e2e.py` | Validator scansionava anche `scripts/` (test/audit files) | Restretto scope a `backend/{routes,middleware,helpers}/` + `server.py, battle_engine.py, battle_core.py, game_systems.py` (production runtime surface) |

## 13. Suite results

```
backend/scripts/run_pack_127_128_129_safety_suite.py
TOTAL: 27 | PASS: 27 | FAIL: 0
Suite status: PASS
```

- Pack 127: 8/8 PASS
- Pack 128: 9/9 PASS (post-update validator no_pack129_leak)
- Pack 129: 10/10 PASS
- **Nessun validator precedente indebolito**, nessun test rimosso, nessuna REQUIRED → OPTIONAL conversion.

## 14. Forbidden areas untouched

Verificato via `git diff bb58cedd2..HEAD --name-only` (validator `validate_pack_129_forbidden_areas_untouched.py`):

| Area | Stato |
|---|---|
| `backend/battle_engine.py` | ✅ Intatto |
| `backend/battle_core.py` | ✅ Intatto |
| `backend/game_systems.py` | ✅ Intatto |
| `backend/.env` | ✅ Intatto |
| `data/design/heroes_master.json` (Character Bible) | ✅ Intatto |
| `data/design/final_numbers/**` | ✅ Intatto |
| `frontend/app/combat.tsx`, `story.tsx`, `frontend/app/**` | ✅ **Tutto intatto (zero modifiche frontend/app)** |
| `frontend/assets/audio/**`, `frontend/assets/images/**` | ✅ Intatto |
| Supervisor configs | ✅ Intatto |
| Gacha / Economy / Reward / Shop / VIP / BP / Mail / Live systems logic | ✅ Intatto |
| DB schema / migrations distruttive | ✅ Zero |
| `backend/routes/v96_team_formation.py` (Pack 125 endpoint) | ✅ Intatto (helpers Pack 129 sono opt-in additivi) |

## 15. Known gaps

| # | Gap | Owner Pack |
|---|---|---|
| G1 | `QA_TEAM_SAVE_ENABLED` non set nel pod → endpoint risponde TEAM_SAVE_DISABLED_PRE_QA. Default fail-closed safe, MANUAL_REQUIRED in QA supervisor. | Pack 132 supervisor QA setup |
| G2 | Frontend `structuredErrorMap.ts` non mountato nelle screen (`battle.tsx` ha handler ad-hoc) | Pack 130/131 quando si migrano screen al nuovo contratto |
| G3 | Backend `server_ready_guard.check_server_ready` non ancora utilizzato in route esistenti | Pack 130 (Lobby Launch Context) lo monterà nei nuovi route |
| G4 | Backend `structured_errors.build_structured_detail` non ancora adottato in v96_team_formation.py (preserva contratto Pack 125) | Pack 131+ migration opt-in |
| G5 | Smoke HTTP autenticato completo POST `/api/team/save-formation` con env true | Pack 132 (Device QA Gate Suite) |
| G6 | Deeplink helper Pack 128 non mountato in `_layout.tsx` | Pack 130+ (Track D Pack 128 carry-over) |
| G7 | 26 mutating-GET hardening runtime guards | Pack 128.x / Pack 130 |
| G8 | Catalog seed startup env gate (`server.py:1437 seed_database`) | Pack 128.x / Pack 130 |

## 16. Device QA status

```
DEVICE_QA_STATUS: BLOCKED
```

Confermato in entrambi i marker Pack 129. Device QA resta `BLOCKED` fino a chiusura completa Pack 130 → 131 → 132 → 133.

## 17. Next required pack

**`PACK 130 — Lobby Launch Context + Real Player Snapshot`**

Sub-task suggeriti (non implementati qui):
1. Montare `server_ready_guard.check_server_ready()` nei nuovi route lobby launch.
2. Iniziare adozione opt-in di `build_structured_detail()` nei nuovi route (no Pack 125 modification).
3. Real player snapshot reader (read-only) basato su `player_server_profiles` + `user_heroes` filtered by `server_id`.
4. Address Pack 128 carry-over gaps G6/G7/G8 se sicuri.

---

## 18. Categorizzazione `ENFORCED / VALIDATED_ONLY / NOT_EXECUTED / FAIL`

| Controllo | Categoria | Evidenza |
|---|---|---|
| TeamFormation V1 server-scoped (Pack 125 endpoint) | **ENFORCED (static audit)** | Validator 2,3,4 PASS; PSP filter + ownership + size + slot + duplicate + write target verified |
| No account-wide team fallback | **ENFORCED (backend runtime scope scan)** | Validator 8 PASS (0 violations su routes/middleware/helpers + server.py) |
| Server Ready guard helper presente | **ENFORCED (code + unit-runtime)** | Validator 1: 6/6 stati verificati via DB mock |
| Server Ready guard mountato in route esistenti | **NOT_EXECUTED** | Opt-in per Pack 130+; Pack 129 lo espone come libreria |
| Structured Errors contract codes + builder | **ENFORCED (helper presente, unit-runtime shape OK)** | Validator 5 PASS: 17 codici + 10 alias + shape 7-field verificata |
| Structured Errors adoption in route esistenti | **NOT_EXECUTED** | Opt-in per Pack 131+ (preserva contratto Pack 125) |
| Frontend structured error map | **VALIDATED_ONLY** | Validator 6 PASS, helper presente ma NON mountato in battle.tsx |
| Pack 128 middleware allowlist coerenza | **ENFORCED** | Validator 7: POST team/save-formation in allowlist |
| `QA_TEAM_SAVE_ENABLED` env attivo nel pod | **NOT_EXECUTED** | `.env` intoccato; default fail-closed safe |
| `PRE_QA_MUTATION_GUARD_ENABLED` env attivo nel pod | **NOT_EXECUTED** | Pack 128 middleware DORMANT (richiesto) |
| Full HTTP smoke autenticato team/save-formation | **NOT_EXECUTED** | Pack 132 |
| Forbidden areas untouched | **ENFORCED (git diff)** | Validator 10 PASS su `bb58cedd2..HEAD` |
| No Pack 130/131/132/133 leak | **ENFORCED (fs scan)** | Validator 9 PASS |
| Suite Pack 127+128+129 | **ENFORCED** | 27/27 PASS |
| Fake PASS | **FAIL = 0** | 2 FAIL onesti durante iterazione, corretti |

---

_Report generato senza fake PASS. Ogni controllo categorizzato onestamente. Tutti i numeri/path sono verificabili nei report JSON in `backend/scripts/reports/pack_129_*_report.json` e nei marker in `data/design/system_safety/pack_129_*.json`. Il suite report locale `backend/reports/pack_127_128_129_safety_suite_*.json` è artefatto di esecuzione **NON tracciato** su `main`; riproducibilità garantita rieseguendo `python3 backend/scripts/run_pack_127_128_129_safety_suite.py` dopo checkout del commit Pack 129._
