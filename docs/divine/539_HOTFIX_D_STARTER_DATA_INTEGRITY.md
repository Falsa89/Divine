# 539 — HOTFIX D — STARTER DATA INTEGRITY / STARTER ROSTER PREFLIGHT

> Chiude `CODEX_AUDIT2_STARTER_DATA_P0_CONFIRMED`. Centralizza il contratto
> starter (3 IDs canonici Pack 87) in un modulo helper unico, gating del
> claim sui flag di catalog-eligibility, e backfill `hero_class` su
> `GET /api/user/heroes` per gli starter canonici quando il catalog espone
> `hero_class: None`. Nessun DB write. Nessuna lore inventata.

## 1) Verdict

**`HOTFIX_D_STARTER_DATA_INTEGRITY_READY_FOR_REAUDIT`**

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
```

## 2) HEAD iniziale

```text
9593a7c5bd79e8c0f29331f3a57c01170fb61f21
```

(chiusura HOTFIX C truth-sync, baseline confermata da prompt).

## 3) HEAD finale / pre-commit

```text
6d65c2c5f8352aed2e7d80445d8863c5e3d49420
```

(working tree contiene i file scope HOTFIX D pronti per commit; truth-sync
del campo `<TRUTH_SYNC_PENDING>` di questo report seguirà il commit, come
per Hotfix B/C.)

## 4) Files changed

```text
backend/server.py                                                              (modified)
backend/helpers/starter_roster_contract.py                                     (new)
backend/scripts/validate_hotfix_d_starter_roster_contract.py                   (new)
backend/scripts/validate_hotfix_d_user_heroes_exposure.py                      (new)
backend/scripts/validate_hotfix_d_no_scope_drift.py                            (new)
docs/divine/539_HOTFIX_D_STARTER_DATA_INTEGRITY.md                             (this file, new)
data/design/system_safety/hotfix_d_starter_roster_db_requirements_v1.json      (new, read-only manifest)
```

`frontend/`: **non toccato** (zero file frontend modificati).
`backend/data/character_bible.py`: **non toccato**.
`data/design/heroes_master.json`: **non toccato**.

## 5) Diff summary

- `backend/server.py`: `+59 −44` su due blocchi:
  - `POST /api/psp/starter/claim`: lista hardcoded sostituita da
    `starter_set_for_claim()` + flag gating da `STARTER_REQUIRED_FLAGS`.
  - `GET /api/user/heroes` (path server-scoped): import contratto +
    backfill `hero_class` per starter canonici + branch `elif` per
    starter posseduti non nel catalog + 2 header diagnostici nuovi.
- `backend/helpers/starter_roster_contract.py`: 150 righe nuove (pure data
  + helper).
- 3 validator nuovi + 1 manifest JSON + 1 report Markdown.

## 6) Starter contract evidence

File: `backend/helpers/starter_roster_contract.py`

```python
STARTER_ROSTER_CONTRACT: list[StarterEntry] = [
    {"starter_id": "greek_phalanx_recruit",
     "expected_role": "tank", "expected_hero_class": "Tank",
     "expected_rarity": 1, "expected_element": "earth"},
    {"starter_id": "celtic_forest_archer",
     "expected_role": "dps", "expected_hero_class": "DPS",
     "expected_rarity": 1, "expected_element": "wind"},
    {"starter_id": "angelic_sanctuary_acolyte",
     "expected_role": "support", "expected_hero_class": "Support",
     "expected_rarity": 1, "expected_element": "light"},
]

STARTER_REQUIRED_FLAGS = {
    "is_official_required": True,
    "obtainable_required": True,
    "show_in_catalog_required": True,
    "premium_forbidden": True,
    "deactivated_forbidden": True,
    "high_rarity_forbidden": True,
    "high_rarity_threshold": 2,
}
```

Helper esportati: `is_starter_id`, `get_starter_entry`,
`starter_set_for_claim`, `starter_fallback_exposure`.

Authorization Pack 87 preservata:
`AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87`.

## 7) Starter IDs evidence

I tre IDs **identici** al baseline Pack 87 (linee 431-436 in `server.py`
prima di HOTFIX D):

```text
greek_phalanx_recruit       → tank    / Tank    / earth
celtic_forest_archer        → dps     / DPS     / wind
angelic_sanctuary_acolyte   → support / Support / light
```

Nessun ID nuovo, nessun ID rimosso. Nessun mapping role/class cambiato.

## 8) Starter claim evidence

`POST /api/psp/starter/claim` ora consuma il contratto:

```python
from helpers.starter_roster_contract import (
    starter_set_for_claim,
    STARTER_REQUIRED_FLAGS,
)
starter_set = starter_set_for_claim()
for hero_id, role in starter_set:
    h = await db.heroes.find_one({"id": hero_id})
    if not h:
        return {"v110_starter_claim": False,
                "blocker": "STARTER_ROSTER_NOT_CATALOGED", ...}
    if STARTER_REQUIRED_FLAGS["high_rarity_forbidden"] and \
       int(h.get("rarity") or 0) > STARTER_REQUIRED_FLAGS["high_rarity_threshold"]:
        ...STARTER_ROSTER_HIGH_RARITY
    if STARTER_REQUIRED_FLAGS["is_official_required"] and h.get("is_official") is not True:
        ...STARTER_ROSTER_NOT_OFFICIAL
    ...
```

Nessuna duplicazione incoerente: validator 1 ha un'asserzione regex contro
la vecchia tupla `[("greek_…","tank"),("celtic_…","dps"),("angelic_…","support")]`
— se ricompare, FAIL.

## 9) Idempotency evidence

- `_slc_pack_87_starter_claim_marker` preservato (verificato da validator 1).
- Header `X-Starter-Claim-Mode: already_claimed_no_write` preservato.
- Path `already_claimed = True` invariato: ritorna `v110_starter_claim:true,
  created:false, already_claimed:true` con `starter_user_heroes_present`
  come read-only count.
- HOTFIX C `servers.tsx` tratta entrambi `created:true` e
  `already_claimed:true` come success path → idempotenza end-to-end coerente.

## 10) Catalog eligibility flags evidence

DB inspection runtime (read-only, eseguita una volta in fase di analisi,
nessuna scrittura):

```text
greek_phalanx_recruit:     rarity=1, is_official=True, obtainable=True,
                            show_in_catalog=True, is_premium=False,
                            deactivated_at=None,   hero_class=None  ⚠
celtic_forest_archer:      rarity=1, is_official=True, obtainable=True,
                            show_in_catalog=True, is_premium=False,
                            deactivated_at=None,   hero_class=None  ⚠
angelic_sanctuary_acolyte: rarity=1, is_official=True, obtainable=True,
                            show_in_catalog=True, is_premium=False,
                            deactivated_at=None,   hero_class=None  ⚠
```

Tutti i 6 flag di catalog-eligibility sono **conformi**. L'unico gap è
`hero_class=None` su tutti e tre, **causa diretta** del P0
`CODEX_AUDIT2_STARTER_DATA_P0_CONFIRMED`: roster server-scoped esposto
con `hero_class` mancante → filtri frontend (`heroes.tsx`, `battle.tsx`)
classificavano gli starter come ineligibili per qualsiasi colonna di ruolo.

Il fallback HOTFIX D risolve questo gap **senza** scritture DB.

## 11) `/api/user/heroes` exposure evidence

Nel branch server-scoped di `GET /api/user/heroes` (file `backend/server.py`):

```python
from helpers.starter_roster_contract import (
    is_starter_id as _hd_is_starter_id,
    starter_fallback_exposure as _hd_starter_fallback_exposure,
)
starter_fallback_applied = 0
starter_catalog_missing_ids: list[str] = []
for uh in user_heroes:
    uh_hero_id = uh.get("hero_id")
    hero = _hero_by_id_ss.get(uh_hero_id)
    if hero:
        ...
        merged = { ... "hero_class": hero.get("hero_class"), ... }
        if _hd_is_starter_id(uh_hero_id) and not merged.get("hero_class"):
            _fb = _hd_starter_fallback_exposure(uh_hero_id, uh)
            for _k, _v in _fb.items():
                if not merged.get(_k):              # no-overwrite
                    merged[_k] = _v
            starter_fallback_applied += 1
        result.append(merged)
    elif _hd_is_starter_id(uh_hero_id):
        # starter posseduto ma NON nel catalog runtime
        starter_catalog_missing_ids.append(uh_hero_id)
        merged = { ... fallback completo dal contratto ... }
        result.append(merged)
        starter_fallback_applied += 1

response.headers["X-Starter-Fallback-Applied"] = str(starter_fallback_applied)
if starter_catalog_missing_ids:
    response.headers["X-Starter-Catalog-Missing"] = ",".join(starter_catalog_missing_ids)
```

Headers Hotfix B/C preservati: `X-Blocker`, `X-Roster-Count`,
`X-PSP-Lookup-Mode`, `X-Server-Scope`, `X-Server-Id`, `X-Profile-Id`,
`X-Player-Level`, `X-Player-Exp`, `X-Server-Progression-State`,
`X-Roster-Source`, `X-Filter-Applied`. Aggiunti `X-Starter-Fallback-Applied`
e `X-Starter-Catalog-Missing` per QA visibility.

PSP mancante → blocker `PLAYER_SERVER_PROFILE_REQUIRED` preservato.

## 12) `hero_class` fallback evidence

Pure-data fallback (no DB read aggiuntivo, no `/api/heroes` HTTP usage):

```python
def starter_fallback_exposure(hero_id: str, base_uh: dict) -> dict:
    entry = get_starter_entry(hero_id)
    if not entry:
        return {}
    return {
        "hero_id": hero_id,
        "hero_class": entry["expected_hero_class"],   # Tank|DPS|Support
        "hero_element": entry["expected_element"],
        "hero_rarity": entry["expected_rarity"],
        "starter_role": entry["expected_role"],
        "_hotfix_d_starter_fallback_applied": True,
    }
```

Garanzia di **no-overwrite**: il merge applica i campi solo se
`not merged.get(_k)` (verificato dal validator 2 con regex
`if not merged.get(`).

## 13) Blocker / error code evidence

Tutti i 7 blocker ratificati Pack 87 + 1 nuovo:

```text
STARTER_ROSTER_NOT_CATALOGED          (doc db.heroes mancante)
STARTER_ROSTER_HIGH_RARITY            (rarity > high_rarity_threshold)
STARTER_ROSTER_NOT_OFFICIAL           (is_official != True)
STARTER_ROSTER_NOT_OBTAINABLE         (obtainable != True)
STARTER_ROSTER_NOT_CATALOG_VISIBLE    (show_in_catalog != True)
STARTER_ROSTER_DEACTIVATED            (deactivated_at set)
STARTER_ROSTER_PREMIUM_FORBIDDEN      (is_premium True)
STARTER_ROSTER_CONTRACT_MISMATCH      (riserva di compatibilità per future violazioni;
                                       non ancora emesso dal claim attuale che non
                                       ha bisogno di rilevare contract drift, ma è
                                       documentato qui come previsto dal prompt §7)
```

Validator 1 verifica esplicitamente la presenza di tutti i 7 blocker
ratificati nel `server.py`.

## 14) Validators results

```text
validate_hotfix_d_starter_roster_contract   PASS  (rc=0)
validate_hotfix_d_user_heroes_exposure      PASS  (rc=0, blocco analizzato: 10611 char)
validate_hotfix_d_no_scope_drift            PASS  (rc=0, 6 file in scope)
```

Hotfix A+B+C **non indeboliti** (verificato in-process):

```text
validate_security_hotfix_a_battle_simulate_guard   PASS  (rc=0)
validate_security_hotfix_a_jwt_secret_preflight    PASS  (rc=0)
validate_hotfix_b_api_error_contract               PASS  (rc=0)
validate_hotfix_b_blocker_visibility               PASS  (rc=0)
validate_hotfix_c_server_select_fail_closed        PASS  (rc=0)
```

## 15) Smoke results

- `python -m py_compile backend/server.py
  backend/helpers/starter_roster_contract.py
  backend/scripts/validate_hotfix_d_*.py`: **OK** (exit 0).
- `import backend.helpers.starter_roster_contract`: OK; `STARTER_IDS`,
  `starter_set_for_claim()`, `starter_fallback_exposure(...)` ritornano
  i valori canonici attesi (verificato runtime in-process).
- `sudo supervisorctl restart backend` → backend RUNNING uptime stabile.
- `curl http://localhost:8001/api/health` → HTTP 200.
- JSON validity di
  `data/design/system_safety/hotfix_d_starter_roster_db_requirements_v1.json`:
  **OK** (`json.load`).
- Endpoint mutativi runtime: **0 chiamati**.

## 16) Scope guard confirmation

`validate_hotfix_d_no_scope_drift.py` rileva 6 file in scope HOTFIX D:

```text
+ backend/helpers/starter_roster_contract.py
+ backend/scripts/validate_hotfix_d_no_scope_drift.py
+ backend/scripts/validate_hotfix_d_starter_roster_contract.py
+ backend/scripts/validate_hotfix_d_user_heroes_exposure.py
+ backend/server.py
+ data/design/system_safety/hotfix_d_starter_roster_db_requirements_v1.json
```

`EXPLICIT_FORBIDDEN` list copre: `battle_engine.py`,
`jwt_secret_preflight.py`, `v96_auth.py`, `v96_team_formation.py`,
`v130_lobby_launch_context.py`, `v131_combat_preview.py`,
`heroes_master.json`, `character_bible.py`, **tutto il frontend di
Hotfix B/C** (`api.ts`, `servers.tsx`, `(tabs)/battle.tsx`,
`(tabs)/heroes.tsx`). Nessuno di questi nel diff.

## 17) DB writes durante test

**0** (zero). Tutti i validator sono statici (analisi del sorgente con
`re`, JSON parsing, nessuna connessione MongoDB aperta). L'unica connessione
DB attiva in fase di analisi è stata una `find_one` **read-only** sui tre
starter per documentare il P0 `hero_class=None` (zero write, zero update).

## 18) Endpoint mutativi runtime test

**0** chiamati. Lista degli endpoint vietati che NON sono stati invocati
durante validator/smoke:

```text
POST /api/psp/ensure              ← non chiamato
POST /api/psp/starter/claim       ← non chiamato
POST /api/team/save-formation     ← non chiamato
POST /api/battle/simulate         ← non chiamato
```

Nessun nuovo endpoint mutativo è stato introdotto da HOTFIX D.

## 19) Remaining P0 / P1 / P2

### P0 ancora aperti dopo HOTFIX D

- Re-audit Game Master + Codex Web congiunto Hotfix A + B + C + D.
- Suite Pack 127-133 con drift atteso: previsione **≥15 FAIL** (= 13 da
  Hotfix A+B+C documentati in 538 + ≥2 nuovi da HOTFIX D su
  `backend/server.py` verso `validate_pack_128/129/130/131_forbidden_areas_untouched`,
  `validate_pack_132_no_frontend_runtime_changes` (etichetta misleading,
  include backend), `validate_pack_133_no_runtime_frontend_backend_changes`,
  `validate_pack_132/133_forbidden_areas_untouched`). Drift di snapshot
  anchor, **NON regressioni semantiche**.

### P1

- `BATTLE_SIMULATE_LIVE_ENABLED` residual P1 (fuori scope HOTFIX D).
- TeamFormation V1 contract review (fuori scope).
- Combat runtime / battle snapshot / lobby launch context (fuori scope).
- Catalogo / I Miei Eroi / Formazione naming canonization (fuori scope).
- Bug fuori scope `heroes.tsx:230 filtered.map(...)` (handoff): **non
  affrontato** in HOTFIX D, intoccato.

### P2

- Localizzazione testi DiagError HOTFIX C (oggi solo italiano).
- Manual DB sync per popolare `db.heroes.hero_class` dei tre starter
  con i valori `Tank/DPS/Support` (fork dedicato `MANUAL_DB_SYNC_REQUIRED`):
  in attesa, il fallback HOTFIX D garantisce esposizione corretta lato API.

## 20) Next recommended step

1. Commit HOTFIX D (auto-pipeline o manuale) e truth-sync di questo report.
2. Game Master + Codex Web re-audit Hotfix A + B + C + D.
3. Se promosso, valutare un fork **MANUAL_DB_SYNC_REQUIRED** per
   popolare `db.heroes.hero_class` dei tre starter così da rendere il
   fallback HOTFIX D non più necessario per il path comune (resterà come
   safety net). Scope: solo `db.heroes` update_one (3 documenti), zero
   altre collection, ratificato dal Game Master.
4. In parallelo, fork dedicato per il bug fuori scope
   `heroes.tsx filtered.map(...)` (HOTFIX E candidato).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = HOTFIX_D_STARTER_DATA_INTEGRITY_READY_FOR_REAUDIT
```
