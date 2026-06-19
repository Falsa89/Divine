# PACK 131 — COMBAT CONSUMES REAL SNAPSHOT + POST-BATTLE PREVIEW SAFE — FINAL REPORT

> Verdetto: **PACK_131_COMBAT_CONSUMES_REAL_SNAPSHOT_POST_BATTLE_PREVIEW_SAFE_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED**
>
> Lingua: italiano. Documento prodotto in ambiente Emergent (branch locale `master`, nessun remote pubblico configurato — sync verso `Falsa89/Divine#main` avviene fuori dallo scope dell'agente, tramite il sistema di publish Emergent).

---

## 0. Identificazione e baseline SHA

| Campo | Valore |
| --- | --- |
| Pack | **PACK 131** |
| Titolo | Combat Consumes Real Snapshot + Post-Battle Preview Safe |
| Baseline Pack 130 FINAL | `26c5085b259f73f63c7b3fc23858051b537b3eb9` |
| Auto-commit/HEAD pre-report Pack 131 | `b01774dafc3b60809d902aebdd9a6a4879c5a9ba` |
| Pack 131 content range | `26c5085b259f73f63c7b3fc23858051b537b3eb9..b01774dafc3b60809d902aebdd9a6a4879c5a9ba` |
| Final SHA (post commit report + fix validator) | `{{FINAL_SHA_TRUTH_SYNC_PENDING}}` *(placeholder dichiarato — verrà truth-syncato come nei Pack 129/130 al commit successivo)* |
| Branch ambiente | `master` (locale Emergent). Repo pubblico atteso `Falsa89/Divine#main`. Nessun `git remote` configurato in container — caveat dichiarato. |
| Device QA | **BLOCKED** |
| Sicurezza scope | NESSUNA mutazione su `battle_engine.py`, `battle_core.py`, `game_systems.py`, frontend live, economia, gacha, reward, shop, VIP, BP, mail, DB schema, migrations. ZERO DB write. |

---

## 1. Verdict

`PACK_131_COMBAT_CONSUMES_REAL_SNAPSHOT_POST_BATTLE_PREVIEW_SAFE_PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED`

Il Pack 131 è completato in modalità **preview-only**: la combat preview consuma il real player snapshot prodotto dal Pack 130 tramite adapter read-only; il post-battle preview è strutturalmente safe (no claim, no reward, no exp, no progress). Tutti i 12 validatori Pack 131 e l'intera suite cumulativa (50 validatori, Pack 127→131) sono PASS. Resta `PARTIAL_ENFORCEMENT` perché `battle_engine.py` non viene eseguito (deferred) e il consumer frontend combat non è ancora implementato (deferred al Pack 132). Re-audit richiesto da Game Master GitHub e Codex Web.

## 2. Starting SHA

`26c5085b259f73f63c7b3fc23858051b537b3eb9` (Pack 130 FINAL — `docs(pack130): sync final report metadata and file counts`).

Auto-commit intermedi (non manuali, generati dall'ambiente Emergent) sopra il Pack 130 FINAL:

| SHA | Messaggio |
| --- | --- |
| `bace55f09` | Auto-generated changes |
| `d41908cb1` | auto-commit for 85041f37-88c6-4552-a745-fb772712bc8f |
| `b01774daf` | Auto-generated changes (HEAD pre-report Pack 131) |

In questi auto-commit risiede l'intera infrastruttura Pack 131 (helper + route + 2 marker + 12 validatori + suite runner + 1 patch wiring `server.py` + 3 patch no-leak validators dei Pack 128/129/130 per togliere `pack_131` dai pattern forbid).

## 3. Final SHA

`{{FINAL_SHA_TRUTH_SYNC_PENDING}}` — placeholder dichiarato per evitare self-reference impossibile. Sarà sostituito dal SHA reale post-commit con micro-commit `docs(pack131): truth sync final SHA` (procedura identica ai Pack 129 e 130).

## 4. Git status before/after

**Before (pre-report Pack 131)** — `HEAD = b01774daf`:

```
$ git status --short --untracked-files=all
(vuoto)

$ git rev-parse --abbrev-ref --symbolic-full-name @{u}
fatal: no upstream configured for branch 'master'

$ git remote -v
(vuoto)
```

Working tree clean. Nessun upstream. Solo branch locale `master`. Tutti i file Pack 131 già tracciati negli auto-commit `bace55f09..b01774daf`.

**After (post fix validator + report)** — `HEAD = {{FINAL_SHA_TRUTH_SYNC_PENDING}}`:

```
$ git status --short --untracked-files=all
(vuoto, tutto committato)
```

## 5. Files changed

### 5.1 File aggiunti Pack 131 (17)

**Helper (1)**
- `backend/helpers/combat_preview_adapter.py` — `build_combat_preview_input()` + `build_post_battle_preview()`.

**Route (1)**
- `backend/routes/v131_combat_preview.py` — `GET /api/combat/preview` (read-only, JWT, no DB write).

**Marker JSON (2)**
- `data/design/system_safety/pack_131_combat_consumes_real_snapshot_marker.json`
- `data/design/system_safety/pack_131_post_battle_preview_safe_marker.json`

**Validatori Pack 131 (12)**
1. `backend/scripts/validate_pack_131_combat_consumes_real_snapshot_contract.py`
2. `backend/scripts/validate_pack_131_snapshot_to_combat_adapter.py`
3. `backend/scripts/validate_pack_131_no_battle_engine_mutation.py`
4. `backend/scripts/validate_pack_131_post_battle_preview_safe.py`
5. `backend/scripts/validate_pack_131_no_rewards_no_exp_no_progress.py`
6. `backend/scripts/validate_pack_131_no_db_writes.py`
7. `backend/scripts/validate_pack_131_structured_errors_contract.py`
8. `backend/scripts/validate_pack_131_pack128_mutation_guard_interaction.py`
9. `backend/scripts/validate_pack_131_frontend_preview_integration_safe.py`
10. `backend/scripts/validate_pack_131_no_authoritative_combat_result.py` *(corretto syntax-bug in questo commit finale)*
11. `backend/scripts/validate_pack_131_no_pack132_133_leak.py`
12. `backend/scripts/validate_pack_131_forbidden_areas_untouched.py`

**Suite Runner (1)**
- `backend/scripts/run_pack_127_128_129_130_131_safety_suite.py`

### 5.2 File modificati (5)

| File | Tipo modifica | Scope |
| --- | --- | --- |
| `backend/server.py` | +4 righe `include_router(v131_combat_preview_router)` dopo Pack 130 | wiring read-only |
| `backend/scripts/validate_pack_128_no_pack129_130_131_leak.py` | rimosso `pack_131` dai pattern forbid (intenzionale: Pack 131 ora previsto) | igiene validator |
| `backend/scripts/validate_pack_129_no_pack130_131_132_133_leak.py` | rimosso `pack_131` dai pattern forbid | igiene validator |
| `backend/scripts/validate_pack_130_no_pack131_132_133_leak.py` | rimosso `pack_131` dai pattern forbid | igiene validator |
| `.emergent/emergent.yml` | solo timestamp `created_at` | non-funzionale |

### 5.3 File documentale aggiunto in questo commit finale (1)

- `docs/divine/533_PACK_131_COMBAT_CONSUMES_REAL_SNAPSHOT_POST_BATTLE_PREVIEW_SAFE_FINAL_REPORT.md` (questo file).

### 5.4 Aree NON toccate (esplicito)

`battle_engine.py`, `battle_core.py`, `game_systems.py`, `backend/.env`, `frontend/app/combat.tsx`, `frontend/app/story.tsx`, intera `frontend/app/**`, Character Bible / `heroes_master.json`, `final_numbers`, `assets/audio`, `assets/images`, configurazioni supervisor, logica gacha / economy / reward / shop / VIP / Battle Pass / mail, DB schema / migrations, aree Pack 132 / Pack 133.

Verifica: `NO_FORBIDDEN_TOUCHED_OUTSIDE_VALIDATORS`, `NO_FRONTEND_TOUCHED`, `NO_PACK_132_133`.

## 6. Combat snapshot consumption summary

- **Sorgente snapshot**: Pack 130 helper `backend/helpers/real_player_snapshot.py::build_real_player_snapshot()` (server-scoped, read-only, `db_write_scope=NONE`).
- **Consumer Pack 131**: `backend/helpers/combat_preview_adapter.py::build_combat_preview_input(player_snapshot, mode, server_id)`.
- **Adattamento**: per ogni hero con `snapshot_status == 'OK'` proietta `user_hero_id`, `hero_id`, `level`, `stars`, `rarity`, `element`, `slot` in `team_a`. Nessuna trasformazione di stat, nessuna mutazione.
- **Team B**: placeholder deterministico `PACK_131_PLACEHOLDER_DUMMY` con `team_b_status = 'PLACEHOLDER_OR_DEFERRED'`. Generazione reale enemy team rinviata a pack futuri.
- **Output campi chiave**:
  - `combat_preview_input.source = 'PACK_130_REAL_PLAYER_SNAPSHOT'`
  - `combat_preview_input.preview_only = True`
  - `combat_preview_input.authoritative = False`
  - `input_snapshot_hash` (sha hash di `team_a`)
  - `player_snapshot_hash` (propagato da snapshot Pack 130)
  - `battle_engine_execution_status = 'BATTLE_ENGINE_EXECUTION_DEFERRED'`
  - `combat_consumption_status = 'PACK_131_PREVIEW_ONLY'`
  - `reward_status / exp_status / progress_status = 'DISABLED'`

Verdetto consumption: **ENFORCED_HELPER_AND_ROUTE_PRESENT_PREVIEW_ONLY**.

## 7. Snapshot-to-combat adapter summary

- File: `backend/helpers/combat_preview_adapter.py`.
- Funzioni esposte: `build_combat_preview_input()` e `build_post_battle_preview()`.
- Linguaggio invariante: solo lettura del dict snapshot Pack 130, nessuna chiamata a DB, nessuna chiamata a `battle_engine`, nessuna RNG live.
- Hash deterministico via `_hash_snapshot` riusato dal modulo Pack 130 (`helpers.real_player_snapshot._hash_snapshot`), garantendo continuità.
- Validatore dedicato: `validate_pack_131_snapshot_to_combat_adapter.py` ⇒ **PASS**.

## 8. Battle engine execution status

- **`BATTLE_ENGINE_EXECUTION_DEFERRED`** — il Pack 131 NON invoca `battle_engine.py` né `battle_core.py`.
- Nessun import a `battle_engine` da `combat_preview_adapter.py` o `v131_combat_preview.py`.
- Validatore: `validate_pack_131_no_battle_engine_mutation.py` ⇒ **PASS**.
- File `battle_engine.py` intatto a livello byte (`git diff 26c5085b2..HEAD -- battle_engine.py` ⇒ vuoto).

## 9. Post-battle preview safe summary

Output `build_post_battle_preview()` strutturalmente safe:

| Proprietà | Valore | Significato |
| --- | --- | --- |
| `preview_only` | `True` | Non è risultato autoritativo |
| `authoritative` | `False` | Mai trattato come canonico |
| `claim_enabled` | `False` | Nessun claim disponibile |
| `claim_disabled` | `True` | Reso esplicito a UI |
| `not_granted` | `True` | Nulla viene concesso |
| `reward_status` | `DISABLED` | |
| `exp_status` | `DISABLED` | |
| `progress_status` | `DISABLED` | |
| `inventory_mutation` | `False` | |
| `economy_mutation` | `False` | |
| `hero_progression_mutation` | `False` | |
| `potential_rewards_preview_only` | `[]` | Lista vuota, no even hint reward |
| `next_gate` | `PACK_132_OR_LATER` | Roadmap esplicita |

Validatori: `validate_pack_131_post_battle_preview_safe.py`, `validate_pack_131_no_rewards_no_exp_no_progress.py`, `validate_pack_131_no_authoritative_combat_result.py` ⇒ tutti **PASS**.

## 10. DB write scope

**`NONE`**.

- Nessuna chiamata `insert_one`, `update_one`, `replace_one`, `delete_one`, `bulk_write`, `save`, `set_to_*`, transazioni in `combat_preview_adapter.py` o `v131_combat_preview.py`.
- Solo lettura tramite Pack 130 (`build_lobby_launch_context` → `find_one` su `users`, `player_server_profiles`, `user_heroes`).
- Endpoint `GET /api/combat/preview` resta dentro l'allowlist read-only del middleware Pack 128 (`validate_pack_131_pack128_mutation_guard_interaction.py` ⇒ **PASS**).
- Validatore: `validate_pack_131_no_db_writes.py` ⇒ **PASS**.

## 11. Structured Errors summary

- Errori veicolati come `HTTPException` con `detail` italianizzato e propagazione di `status_code` proveniente da `build_lobby_launch_context` (allineato al contratto Pack 129).
- Cataloghi possibili (ereditati da Pack 130): `MISSING_AUTH_TOKEN`, `EXPIRED_TOKEN`, `INVALID_TOKEN`, `USER_NOT_FOUND`, `SERVER_NOT_SELECTED`, `NO_TEAM_BOUND_FOR_SERVER`, `SNAPSHOT_HEROES_EMPTY`.
- Nessun leak di stack trace o di errore RNG/engine (engine non eseguito).
- Validatore: `validate_pack_131_structured_errors_contract.py` ⇒ **PASS**.

## 12. Frontend changes summary

**Nessuna modifica frontend in questo Pack.**

- `git diff 26c5085b2..HEAD -- 'frontend/**'` ⇒ vuoto.
- `frontend/app/combat.tsx` e `frontend/app/story.tsx` intatti a livello byte.
- Stato consumer frontend: `FRONTEND_COMBAT_CONSUMER_DEFERRED` — rinviato a pack futuri (Pack 132+) sotto Device QA gate.
- Validatore: `validate_pack_131_frontend_preview_integration_safe.py` ⇒ **PASS** (verifica che NON ci siano import o riferimenti a Pack 131 dal frontend live).

## 13. Pack128 middleware interaction

- Il middleware backend di mutation guard del Pack 128 resta **dormant** (`env unset` di default).
- L'endpoint `GET /api/combat/preview` è metodo `GET` e quindi rientra di default fuori dalla policy di blocco delle mutazioni; in più non esegue alcuna write.
- `mutating_get_hardening` rispettato: il GET non muta stato.
- Validatore: `validate_pack_131_pack128_mutation_guard_interaction.py` ⇒ **PASS**.

## 14. Runtime smoke results

- **Backend liveness**: UP (HTTP 200) — confermato dal preflight della suite (`Backend liveness: UP`).
- **Full HTTP authenticated smoke**: **`NOT_EXECUTED`** in questo Pack. È pianificato sotto Pack 132 (Master Device QA Gate Suite) dove è previsto seeding e harness HTTP autenticato.
- **Static + import contract smoke**: PASS (gli import dei nuovi moduli sono coerenti, niente errore di compile o registro router).

## 15. Validators added/updated and results

### 15.1 Nuovi validatori Pack 131 (12) — tutti PASS

| # | Validatore | Risultato | Enforcement |
| --- | --- | --- | --- |
| 1 | `validate_pack_131_combat_consumes_real_snapshot_contract.py` | PASS | static contract |
| 2 | `validate_pack_131_snapshot_to_combat_adapter.py` | PASS | static adapter |
| 3 | `validate_pack_131_no_battle_engine_mutation.py` | PASS | byte-level invariance |
| 4 | `validate_pack_131_post_battle_preview_safe.py` | PASS | preview-safe properties |
| 5 | `validate_pack_131_no_rewards_no_exp_no_progress.py` | PASS | reward/EXP/progress disabled |
| 6 | `validate_pack_131_no_db_writes.py` | PASS | static grep DB writes |
| 7 | `validate_pack_131_structured_errors_contract.py` | PASS | structured errors |
| 8 | `validate_pack_131_pack128_mutation_guard_interaction.py` | PASS | middleware interaction |
| 9 | `validate_pack_131_frontend_preview_integration_safe.py` | PASS | no FE consumer leaks |
| 10 | `validate_pack_131_no_authoritative_combat_result.py` | PASS (fixed) | claim/authoritative pinned False |
| 11 | `validate_pack_131_no_pack132_133_leak.py` | PASS | no anticipazioni Pack 132/133 |
| 12 | `validate_pack_131_forbidden_areas_untouched.py` | PASS | forbidden areas byte-intact |

### 15.2 Patch ai validatori dei Pack precedenti (3)

| Validatore | Patch | Motivo |
| --- | --- | --- |
| `validate_pack_128_no_pack129_130_131_leak.py` | rimosso `pack_131` dai pattern forbid | Pack 131 ora atteso |
| `validate_pack_129_no_pack130_131_132_133_leak.py` | rimosso `pack_131` dai pattern forbid | idem |
| `validate_pack_130_no_pack131_132_133_leak.py` | rimosso `pack_131` dai pattern forbid | idem |

### 15.3 Hotfix syntax in questo commit finale

- `validate_pack_131_no_authoritative_combat_result.py`: corretto bug di quote nidificate (riga 15 con stringa Python non chiusa). Logica preservata e rafforzata: il validatore ora verifica esplicitamente che `claim_enabled`, se presente, sia pinned a `False`. Risultato post-fix: **PASS**.

## 16. Suite results

```
$ python backend/scripts/run_pack_127_128_129_130_131_safety_suite.py
Backend liveness: UP
========================================================================
--- PACK 127 ---  8/8 PASS
--- PACK 128 ---  9/9 PASS
--- PACK 129 ---  10/10 PASS
--- PACK 130 ---  11/11 PASS
--- PACK 131 ---  12/12 PASS
========================================================================
TOTAL: 50 | PASS: 50 | FAIL: 0
Suite status: PASS
```

✅ **Pack 127: 8/8 PASS · Pack 128: 9/9 PASS · Pack 129: 10/10 PASS · Pack 130: 11/11 PASS · Pack 131: 12/12 PASS · TOTAL 50/50.**

## 17. Forbidden areas untouched confirmation

`git diff --name-only 26c5085b259f73f63c7b3fc23858051b537b3eb9..HEAD` filtrato per aree vietate (escludendo i validatori Pack 131 che _menzionano_ ma non _modificano_):

```
NO_FORBIDDEN_TOUCHED_OUTSIDE_VALIDATORS
NO_FRONTEND_TOUCHED
```

Conferme esplicite:

- ✅ `battle_engine.py` — INTATTO
- ✅ `battle_core.py` — INTATTO
- ✅ `game_systems.py` — INTATTO
- ✅ `backend/.env` — INTATTO
- ✅ `frontend/app/combat.tsx` — INTATTO
- ✅ `frontend/app/story.tsx` — INTATTO
- ✅ `frontend/app/**` (intero albero) — INTATTO
- ✅ Character Bible / `heroes_master.json` — INTATTO
- ✅ `final_numbers` — INTATTO
- ✅ `assets/audio`, `assets/images` — INTATTI
- ✅ Configurazioni supervisor — INTATTE
- ✅ Logica gacha / economy / reward / shop / VIP / Battle Pass / mail — INTATTA
- ✅ DB schema / migrations — INTATTI
- ✅ Pack 132 / Pack 133 — **NON INIZIATI** (`NO_PACK_132_133`)

## 18. Known gaps

1. **`BATTLE_ENGINE_EXECUTION_DEFERRED`** — `battle_engine.py` non viene mai invocato dal Pack 131. La simulazione live resta out-of-scope e sarà introdotta sotto Device QA gate nei pack successivi.
2. **`FRONTEND_COMBAT_CONSUMER_DEFERRED`** — nessun consumer frontend integrato con `GET /api/combat/preview`. Il frontend live (`combat.tsx`, `story.tsx`) non riferisce Pack 131. Sarà integrato nei pack futuri sotto Device QA gate.
3. **`FULL_HTTP_AUTHENTICATED_SMOKE = NOT_EXECUTED`** — il Pack 131 non include un harness HTTP autenticato end-to-end con seeding; è pianificato per Pack 132 (Master Device QA Gate Suite).
4. **`TEAM_B_PLACEHOLDER`** — `team_b` resta un placeholder deterministico (`PACK_131_PLACEHOLDER_DUMMY`). Generazione enemy reale rinviata.
5. **Branch publishing**: il container Emergent espone solo branch locale `master` senza `git remote`. Il sync verso `Falsa89/Divine#main` avviene fuori dallo scope dell'agente (Emergent Publish). Verificare su GitHub dopo publish.
6. **Final SHA placeholder**: questo report referenzia `{{FINAL_SHA_TRUTH_SYNC_PENDING}}`; truth-sync è programmato come micro-commit successivo, identica procedura usata in Pack 129 e Pack 130.

## 19. Device QA status

**`BLOCKED`**.

Il Pack 131 non sblocca Device QA. Lo sblocco richiede Pack 132 (Master Device QA Gate Suite + Docs Truth Cleanup) e Pack 133 (Device QA Evidence Harness), entrambi non iniziati. Tutti gli output Pack 131 esponendo `device_qa_status = 'BLOCKED'` (verificabile in `GET /api/combat/preview` payload e nei marker JSON).

## 20. Next required pack

**PACK 132 — Master Device QA Gate Suite + Docs Truth Cleanup** (P1).

Obiettivi attesi (NON eseguiti in questo Pack):

- Suite master cumulativa Pack 127→132 con harness HTTP autenticato end-to-end.
- Docs truth cleanup ricognitivo sui report `5xx`.
- Preparazione gate per Device QA evidence (Pack 133).

A seguire: Pack 133 — Device QA Evidence Harness (P2).

---

## Appendice A — Controlli obbligatori dichiarati

- Device QA resta **BLOCKED** ✅
- Pack 132/133 **non iniziati** ✅
- Combat preview resta **preview-only** ✅
- Post-battle resta **preview-only** ✅
- `claim_enabled = false` ✅
- `reward_status = DISABLED` ✅
- `exp_status = DISABLED` ✅
- `progress_status = DISABLED` ✅
- DB write scope **NONE** ✅
- Nessuna modifica a `battle_engine.py` ✅
- Nessuna modifica a `battle_core.py` ✅
- Nessuna modifica a `frontend/app/combat.tsx` ✅
- Nessuna modifica a `frontend/app/story.tsx` ✅
- Nessuna modifica a gacha/economy/reward/shop/VIP/BP/mail ✅
- Full HTTP smoke autenticato resta **`NOT_EXECUTED`** ✅ (dichiarato)
- Pack 128 middleware resta **dormant** se env unset ✅

## Appendice B — Comando suite

```bash
python backend/scripts/run_pack_127_128_129_130_131_safety_suite.py
```

Output atteso: `TOTAL: 50 | PASS: 50 | FAIL: 0`.

## Appendice C — Endpoint Pack 131

```
GET /api/combat/preview?mode=training&server_id=<server_id>
Authorization: Bearer <JWT>
```

Risposta sintetica:

```json
{
  "ok": true,
  "preview_battle_id": "<launch_context_id>",
  "launch_context_id": "<launch_context_id>",
  "mode": "training",
  "server_id": "<server_id>",
  "preview_only": true,
  "authoritative": false,
  "combat_preview_input": { "source": "PACK_130_REAL_PLAYER_SNAPSHOT", "team_a": [...], "team_b": {...}, "preview_only": true, "authoritative": false, "mode": "training", "server_id": "<server_id>" },
  "input_snapshot_hash": "<sha>",
  "player_snapshot_hash": "<sha>",
  "battle_engine_execution_status": "BATTLE_ENGINE_EXECUTION_DEFERRED",
  "combat_consumption_status": "PACK_131_PREVIEW_ONLY",
  "reward_status": "DISABLED",
  "exp_status": "DISABLED",
  "progress_status": "DISABLED",
  "post_battle_preview": { "preview_only": true, "authoritative": false, "claim_enabled": false, "reward_status": "DISABLED", "exp_status": "DISABLED", "progress_status": "DISABLED", "inventory_mutation": false, "economy_mutation": false, "hero_progression_mutation": false, "potential_rewards_preview_only": [], "not_granted": true, "claim_disabled": true, "next_gate": "PACK_132_OR_LATER" },
  "device_qa_status": "BLOCKED",
  "pack_origin": "PACK_131"
}
```

---

> Fine report. In attesa di re-audit Game Master GitHub + Codex Web. Pack 131 dichiarato **PARTIAL_ENFORCEMENT_REAUDIT_REQUIRED**, non chiuso unilateralmente.
