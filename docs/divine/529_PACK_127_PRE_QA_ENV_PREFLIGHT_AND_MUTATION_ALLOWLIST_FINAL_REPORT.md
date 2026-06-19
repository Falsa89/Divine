# PACK 127 — PRE-QA ENV PREFLIGHT + BACKEND MUTATION ALLOWLIST + STARTUP/BOT/SEED SAFETY

**Verdetto finale (prudente, onesto, no fake PASS):**

```
PACK_127_PRE_QA_ENV_PREFLIGHT_AND_MUTATION_ALLOWLIST_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED
```

**Device QA status:** `BLOCKED`
**Next required pack:** `PACK 128 — Route / Deeplink Lockdown` (con sub-pack dedicato a **backend mutation middleware reale**, vedi §10).

---

## 1. Git anchors

| Campo | Valore |
|---|---|
| Starting SHA | `5e8ef0284a879ba33b7bce7da94c333fa62bd873` |
| Final SHA | `c645fbb74a7696aee9b3e2840c0d2789544e3d9a` |
| Branch | `main` |
| Working tree pre-anchor | file Pack 127 presenti prima della chiusura semantica (vedi §2 — stato osservato durante l'iterazione, prima dell'auto-commit `28260e3a3` e dell'anchor `c645fbb74`) |
| Working tree post-anchor | **clean** (`nothing to commit, working tree clean`) |

### Mini-chain commit Pack 127

```text
Content commit Pack 127:
5233371a439f8c1d0191678bc6a9c0a6d256e8fc

Pre-anchor auto commit:
28260e3a3beea47adeccc2cff36b2137ecc30113

Final semantic anchor:
c645fbb74a7696aee9b3e2840c0d2789544e3d9a

Anchor commit message:
feat(pack127): pre-qa env preflight and mutation allowlist audit
```

Il commit `c645fbb74` è un **empty semantic anchor commit rispetto a `28260e3a3`**. Il contenuto effettivo Pack 127 (12 file, 463 inserzioni) è stato persistito nel **content commit `5233371a4`**, già verificato indipendentemente da Codex Web.

## 2. Stato git durante / dopo Pack 127

### Stato osservato durante l'iterazione (pre-anchor, prima del content commit `5233371a4`)

```text
 M backend/scripts/validate_pack_127_backend_no_startup_writes.py
?? backend/scripts/reports/pack_127_backend_mutation_allowlist_report.json
?? backend/scripts/reports/pack_127_backend_no_startup_writes_report.json
?? backend/scripts/reports/pack_127_battle_simulate_fail_closed_report.json
?? backend/scripts/reports/pack_127_borea_hidden_runtime_invariant_report.json
?? backend/scripts/reports/pack_127_bot_system_disabled_report.json
?? backend/scripts/reports/pack_127_no_mutating_get_report.json
?? backend/scripts/reports/pack_127_pre_qa_env_preflight_report.json
?? backend/scripts/reports/pack_127_stale_ready_pass_declassification_report.json
?? data/design/system_safety/pack_127_backend_mutation_allowlist.json
?? data/design/system_safety/pack_127_stale_ready_pass_declassification.json
?? docs/divine/529_PACK_127_PRE_QA_ENV_PREFLIGHT_AND_MUTATION_ALLOWLIST_FINAL_REPORT.md
```

### Stato finale post-anchor (`c645fbb74`)

```text
clean — nothing to commit, working tree clean
```

> NB: nessun file in `backend/.env`, `battle_engine.py`, `battle_core.py`, `frontend/`, Character Bible, `assets/`, supervisor configs è stato modificato (vedi §11).

## 3. File modificati / creati

### Modificato (1)
- `backend/scripts/validate_pack_127_backend_no_startup_writes.py` — correzione regex (era greedy 8000-char e includeva `/api/register` adiacente, generando un falso positivo `db.users.insert`). Ora estrae i corpi delle funzioni startup delimitati dall'indentazione e separa **FORBIDDEN** (user-data / live economy) da **WARNING** (catalog auto-seed).

### Creati — Validator reports (8 JSON)
- `backend/scripts/reports/pack_127_pre_qa_env_preflight_report.json`
- `backend/scripts/reports/pack_127_backend_no_startup_writes_report.json`
- `backend/scripts/reports/pack_127_bot_system_disabled_report.json`
- `backend/scripts/reports/pack_127_battle_simulate_fail_closed_report.json`
- `backend/scripts/reports/pack_127_backend_mutation_allowlist_report.json`
- `backend/scripts/reports/pack_127_no_mutating_get_report.json`
- `backend/scripts/reports/pack_127_borea_hidden_runtime_invariant_report.json`
- `backend/scripts/reports/pack_127_stale_ready_pass_declassification_report.json`

### Creati — Marker dichiarativi (2 JSON)
- `data/design/system_safety/pack_127_backend_mutation_allowlist.json`
- `data/design/system_safety/pack_127_stale_ready_pass_declassification.json`

### Già presente (intoccato)
- `data/design/system_safety/pack_127_pre_qa_env_preflight_marker.json`

## 4. Esito di ciascuno degli 8 validator

| # | Validator | Exit | Status | Note |
|---|---|---|---|---|
| 1 | `validate_pack_127_pre_qa_env_preflight.py` | 0 | **PASS** | 2 NOTE: `BOTS_DISABLED` e `BOT_KILL_SWITCH` non esplicitamente `true` nel `backend/.env` (env è `<unset>`); il validator richiede `MANUAL_REQUIRED` per runtime QA. |
| 2 | `validate_pack_127_backend_no_startup_writes.py` | 0 | **PASS** (con 3 NOTE) | Nessuna scrittura vietata su user-data (`db.users`, `db.gacha_pulls`, `db.transactions`, `db.mail`, `grant_starter_heroes`, `seed_legacy_heroes`) trovata nei 3 handler `@app.on_event("startup")`. **3 NOTE Pack 128**: l'handler `seed_database` (server.py:1437) esegue `db.heroes.delete_many` + `db.heroes.insert_one` + `db.heroes.update_one` **senza env gate** (idempotente: solo se `count<30`, ma comunque catalogo non gated). |
| 3 | `validate_pack_127_bot_system_disabled.py` | 0 | **PASS** | Env `BOTS_DISABLED` / `BOT_KILL_SWITCH` non set (`<unset>`); runtime kill-switch dichiarato `MANUAL_REQUIRED`. 1 bot file scansionato; gate env presente nel codice (`server.py:1521` legge `BOTS_DISABLED`/`BOT_KILL_SWITCH` ma di default non disabilita). |
| 4 | `validate_pack_127_battle_simulate_fail_closed.py` | 0 | **PASS** (parziale — vedi §7) | Static: trovata referenza `/api/battle/simulate` in 5 file. Runtime smoke senza auth: **HTTP 401 "Token mancante"** (fail-closed anonimo OK). **Smoke autenticato NON_EXECUTED** (vedi §7 — gap reale). |
| 5 | `validate_pack_127_backend_mutation_allowlist.py` | 0 | **PASS dichiarativo** | Allowlist declarativa creata in `data/design/system_safety/pack_127_backend_mutation_allowlist.json` con 7 route consentite. Runtime middleware enforcement **DEFERRED to PACK 128**. |
| 6 | `validate_pack_127_no_mutating_get.py` | 0 | **PASS (audit-only)** | 73 file route scansionati. **26 GET route con pattern di mutazione (`.insert_one`, `.update_one`, `.delete_one`, ecc.) flagged** — molti idempotenti "init-on-read" ma rappresentano attack surface. Lista in `pack_127_no_mutating_get_report.json`. Hardening runtime → PACK 128. |
| 7 | `validate_pack_127_borea_hidden_runtime_invariant.py` | 0 | **PASS** | `greek_borea` in `heroes_master.json`: `asset_status=pending_assets`, `contract_status=pending_contract`, `release_group=launch_extra_premium`. Non player-visible. `qa_team_seed_canonical_heroes.py`: borea presente solo come `FORBIDDEN_KEYWORDS`. |
| 8 | `validate_pack_127_stale_ready_pass_declassification.py` | 0 | **PASS** | Marker creato con `device_qa_status=BLOCKED` e declassificazione esplicita di: `PACK_118_DEVICE_READY`, `PACK_126_FIX_*`, `FASE_G_AUDIT_COVERAGE`, `FASE_H_CLASSIFICATION`. |

## 5. Tabella categorizzata `ENFORCED / VALIDATED_ONLY / NOT_EXECUTED / FAIL`

| Controllo | Categoria | Evidenza |
|---|---|---|
| `/api/battle/simulate` anonimo fail-closed | **ENFORCED** | Runtime smoke HTTP 401 (`Token mancante`) — `Depends(get_current_user)` in `battle_engine.py:1145` |
| `/api/battle/simulate` autenticato con marker preview → 409 | **ENFORCED** | Guard `PREVIEW_SIMULATE_MUTATION_BLOCKED` in `battle_engine.py:1166` (lettura statica, non smoke runtime) |
| `/api/battle/simulate` autenticato con body **non-preview** | **NOT_EXECUTED** | Smoke runtime autenticato non eseguito; staticamente, il path live mutating del legacy battle engine **resta raggiungibile** se chiamato senza marker preview da utente autenticato (gap reale, vedi §7) |
| Backend mutation allowlist | **VALIDATED_ONLY** | Documento `pack_127_backend_mutation_allowlist.json` declarativo; **nessun middleware FastAPI runtime** che blocca route non-allowlisted |
| Startup writes (user-data forbidden) | **ENFORCED (static)** | I 3 handler startup ispezionati non contengono `db.users.insert`, `db.gacha_pulls.insert`, `db.transactions.insert`, `db.mail.insert`, `grant_starter_heroes(`, `seed_legacy_heroes(` |
| Startup catalog seed (`db.heroes.*`) senza env gate | **VALIDATED_ONLY** (finding NOTE) | `server.py:1437` `seed_database` esegue mutazioni catalogo senza `*_ENABLED`/`*_KILL_SWITCH`; idempotente ma non gated → hardening **PACK 128** |
| Bot system kill-switch | **VALIDATED_ONLY** | Codice in `server.py:1521` legge env `BOTS_DISABLED`/`BOT_KILL_SWITCH`. Env nel pod **non set** (`<unset>`). Runtime kill-switch effettivo richiede aggiornamento supervisor in QA → `MANUAL_REQUIRED` |
| QA team save allowlist wildcard `*` | **ENFORCED (validator)** | Validator FAIL se `QA_TEAM_SAVE_ALLOWLIST=*`. Env attuale `<unset>` (safe). Solo UUID autorizzato: `651253e2-da8d-466b-98f3-82f008d158ed` |
| Borea hidden invariant | **ENFORCED (static)** | `heroes_master.json` + `qa_team_seed_canonical_heroes.py` confermano non-summonable / non-runtime-active |
| No mutating GET (26 flagged) | **VALIDATED_ONLY** (audit-only) | Lista completa in `pack_127_no_mutating_get_report.json`. Block runtime → **PACK 128** |
| Declassificazione READY/PASS storici | **ENFORCED (doc)** | Marker `pack_127_stale_ready_pass_declassification.json` con `device_qa_status=BLOCKED` |
| Smoke autenticato `/api/battle/simulate` | **NOT_EXECUTED** | Vedi §7 — `RUNTIME_AUTHENTICATED_SMOKE_NOT_EXECUTED` |
| Runtime middleware mutation block | **NOT_EXECUTED** | Nessun middleware FastAPI è stato creato in Pack 127 per intercettare route non-allowlisted in tempo reale |
| Falsi PASS | **FAIL = 0** | Nessuna riga FAIL nei report JSON onesti |

## 6. Stato `/api/battle/simulate`

- **Route definita in:** `backend/battle_engine.py:1144` (`@router.post("/battle/simulate")`), file esplicitamente **NON modificato** in questo pack (vincolo utente).
- **Auth gate:** `Depends(get_current_user)` → richiede Bearer token JWT valido.
- **Preview guard:** se body contiene `battle_engine_mode=preview` o `preview=true` o `reward_policy=preview` o `progress_policy=preview`, ritorna **HTTP 409 `PREVIEW_SIMULATE_MUTATION_BLOCKED`** (v108_POSTQA_A).
- **Runtime smoke senza auth:** `HTTP 401 {"detail":"Token mancante"}` ✅ ENFORCED.
- **Runtime smoke autenticato (con QA JWT) — body senza marker preview:** **NON_EXECUTED**. Staticamente, il legacy battle engine mutating eseguirebbe la richiesta (reward/EXP/gold). Questo è il **gap reale** che PACK 131 risolverà sostituendo il consumo a runtime con lo snapshot reale (vedi roadmap).
- **Conclusione onesta:** `/api/battle/simulate` è **fail-closed anonimo** ma **NON fail-closed runtime per ogni utente autenticato senza marker preview**. Verdetto: **PARTIAL**.

## 7. Stato bot / startup writes

| Aspetto | Valore | Categoria |
|---|---|---|
| Handler startup totali | 3 (`server.py:52`, `:1437`, `:1511`) | informativo |
| Scritture user-data forbidden negli startup | **0** | ENFORCED |
| Mutazioni catalogo `db.heroes.*` in `seed_database` (server.py:1437) senza env gate | **rilevate** | VALIDATED_ONLY (NOTE Pack 128) |
| Bot startup handler (`server.py:1511`) | gate env presente (`BOTS_DISABLED`/`BOT_KILL_SWITCH`) | ENFORCED (codice) |
| Env runtime `BOTS_DISABLED` / `BOT_KILL_SWITCH` nel pod | `<unset>` | NOT_EXECUTED (MANUAL_REQUIRED in QA supervisor) |
| `ops_c_wiring_startup_check` (server.py:52) | solo spawn subprocess, nessuna scrittura DB | safe |

## 8. Stato QA allowlist wildcard

- **Validator pre-QA env preflight:** richiede esplicitamente che `QA_TEAM_SAVE_ALLOWLIST != "*"`. Se wildcard → **FAIL** automatico.
- **Env attuale nel pod:** `QA_TEAM_SAVE_ALLOWLIST=<unset>` ✅ safe (no wildcard).
- **Unico UUID autorizzato per QA save:** `651253e2-da8d-466b-98f3-82f008d158ed`.
- **NESSUN segreto stampato** nei log/report (solo l'UUID QA già noto).
- `backend/.env` **non modificato** (rispetto vincolo utente).

## 9. Stato Borea invariant

- `heroes_master.json` → `greek_borea`:
  - `asset_status=pending_assets`
  - `contract_status=pending_contract`
  - `release_group=launch_extra_premium`
  - **NON player-visible**, NON in pool gacha runtime, NON in seed canonico player.
- `qa_team_seed_canonical_heroes.py` → borea referenziato **solo** come `FORBIDDEN_KEYWORDS` (deny-list nel seeder).
- **Status:** ENFORCED ✅

## 10. Aree forbidden — conferma intatte

Verificato `git status` finale: nessuna delle seguenti aree è stata toccata in Pack 127.

| Area | Stato |
|---|---|
| `backend/battle_engine.py` | ✅ Intatto |
| `backend/battle_core.py` | ✅ Intatto |
| `backend/game_systems.py` | ✅ Intatto |
| `backend/.env` | ✅ Intatto |
| `frontend/app/**` | ✅ Intatto (zero modifiche frontend) |
| `frontend/components/**` | ✅ Intatto |
| `data/design/heroes_master.json` (Character Bible) | ✅ Intatto |
| `data/design/final_numbers/**` | ✅ Intatto |
| `assets/audio/**`, `assets/images/**` | ✅ Intatto |
| Supervisor configs (`/etc/supervisor/`) | ✅ Intatto |
| Gacha / Economy / Reward / Shop / VIP / Battle Pass / Mail / Live systems | ✅ Intatto |

## 11. Gap residui e blocker per Device QA

| # | Gap | Owner Pack |
|---|---|---|
| G1 | Backend mutation middleware runtime mancante (l'allowlist è solo dichiarativa) | **PACK 128** (sub-pack dedicato — NON nascondere nel generico Route/Deeplink Lockdown) |
| G2 | `/api/battle/simulate` autenticato senza marker preview esegue ancora il legacy mutating engine | **PACK 131** (Combat Consumes Real Snapshot) |
| G3 | 26 GET route con pattern di mutazione (init-on-read e simili) non bloccate a runtime | **PACK 128** |
| G4 | `seed_database` (catalogo heroes) non gated da env esplicito | **PACK 128** |
| G5 | Env runtime `BOTS_DISABLED=true` / `BOT_KILL_SWITCH=true` non set nel pod | **MANUAL_REQUIRED** in supervisor QA (non gestito qui per vincolo `.env` intoccato) |
| G6 | Smoke runtime autenticato `/api/battle/simulate` non eseguito | **PACK 132** (Device QA Gate Suite) o sub-pack runtime di Pack 128 |
| W1 | (warning legacy non-bloccante) Route static audit su `servers.tsx` segnala mancanza lock marker | **deferred per richiesta utente** dal Pack 123 |

## 12. Riassunto verdict

```
PACK_127_PRE_QA_ENV_PREFLIGHT_AND_MUTATION_ALLOWLIST_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED

ENFORCED:
  - /api/battle/simulate anonimo fail-closed (HTTP 401)
  - Preview guard 409 PREVIEW_SIMULATE_MUTATION_BLOCKED (statico)
  - Nessuna scrittura forbidden user-data negli startup handler
  - Borea hidden invariant
  - QA allowlist wildcard validator (no `*`)
  - Declassificazione READY/PASS storici (BLOCKED device QA)

VALIDATED_ONLY (validatore/marker dichiarativo, no runtime middleware):
  - Backend mutation allowlist (7 route)
  - Catalog seed startup (db.heroes.*) → NOTE Pack 128
  - Bot kill-switch codice gate (env <unset> nel pod → MANUAL_REQUIRED QA)
  - 26 GET con pattern mutativi (audit-only)

NOT_EXECUTED:
  - Smoke runtime autenticato di /api/battle/simulate (gap G2/G6)
  - Runtime middleware mutation block (gap G1)

FAIL:
  - 0
```

## 13. Next required pack

**`PACK 128 — Route / Deeplink Lockdown + Backend Mutation Middleware Runtime`**

Sub-pack obbligatorio dedicato a:
1. Implementare middleware FastAPI che blocchi route HTTP method/path non in allowlist.
2. Hardening dei 26 GET con pattern mutativi (lista in `pack_127_no_mutating_get_report.json`).
3. Gate env esplicito su `seed_database` (es. `CATALOG_SEED_AUTORIZED=true` con allowlist UUID).
4. Frontend route lockdown / deeplink whitelist.

Solo dopo Pack 128 → Pack 129 (TeamFormation V1) → Pack 130 (Lobby Launch Context) → Pack 131 (Combat Real Snapshot — chiude gap G2) → Pack 132 (Device QA Gate Suite — chiude gap G6) → Pack 133 (Device QA Evidence Harness).

**Device QA resta `BLOCKED` fino a chiusura completa di Pack 127→133.**

---

_Report generato senza fake PASS. Ogni controllo categorizzato onestamente. Tutti i numeri/path sono verificabili nei report JSON in `backend/scripts/reports/pack_127_*_report.json` e nei marker in `data/design/system_safety/pack_127_*.json`._
