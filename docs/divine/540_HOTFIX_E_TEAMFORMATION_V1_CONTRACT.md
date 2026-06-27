# 540 — HOTFIX E — TEAMFORMATION V1 CONTRACT / SNAPSHOT ALIGNMENT

> Chiude `CODEX_AUDIT3_TEAM_CONTRACT_P0_CONFIRMED`. Introduce un contratto
> TeamFormation V1 unificato `{user_hero_id, canonical_id, col, row}`,
> normalize-on-read per la lettura legacy, validazione save fail-closed
> con 10 blocker codes dedicati, e allineamento di
> `real_player_snapshot.py` (Pack 130) al contratto V1.

## 1) Verdict

**`HOTFIX_E_TEAMFORMATION_V1_READY_FOR_REAUDIT`**

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
```

### 1.bis) Old contract ambiguity — root cause (Codex Audit 3)

```text
- starter Pack 87:        team_formation = [{slot_index, user_hero_id}, ...]
- frontend save Pack 125: team_formation = [{hero_id: h.id, col, row}, ...]
- backend save Pack 125:  validava `hero_id` contro user_heroes.hero_id (= canonical)
- snapshot Pack 130:      trattava `user_hero_id OR hero_id` come owned id
⇒ il campo `hero_id` rappresentava cose diverse in punti diversi
⇒ Team → Lobby → Combat potevano rompersi o mascherare il P0
```

HOTFIX E rimuove l'ambiguità: V1 separa esplicitamente `user_hero_id` (owned
copy) e `canonical_id` (catalog), e centralizza tutto in un unico modulo
helper consumato da save, get, snapshot e frontend.

## 2) HEAD iniziale

```text
be87f54140488bdd75bd7f95dff2e7ef8c6fea1f
```

(chiusura HOTFIX D truth-sync, baseline confermata dal prompt).

## 3) HEAD finale / pre-commit

`<TRUTH_SYNC_PENDING>` — sarà popolato dopo il commit HOTFIX E, come
per Hotfix B/C/D.

## 4) Files changed

```text
frontend/app/(tabs)/battle.tsx                                           (modified)
backend/routes/v96_team_formation.py                                     (modified)
backend/helpers/real_player_snapshot.py                                  (modified)
backend/helpers/team_formation_contract.py                               (new)
backend/scripts/validate_hotfix_e_teamformation_v1_contract.py           (new)
backend/scripts/validate_hotfix_e_frontend_payload.py                    (new)
backend/scripts/validate_hotfix_e_snapshot_alignment.py                  (new)
backend/scripts/validate_hotfix_e_no_scope_drift.py                      (new)
data/design/system_safety/hotfix_e_teamformation_v1_contract.json        (new)
docs/divine/540_HOTFIX_E_TEAMFORMATION_V1_CONTRACT.md                    (this file)
```

`backend/server.py`: **non toccato**.
`frontend/utils/api.ts`, `frontend/app/servers.tsx`, `frontend/app/(tabs)/heroes.tsx`: **non toccati**.
`backend/battle_engine.py`, `backend/helpers/jwt_secret_preflight.py`,
`backend/routes/v96_auth.py`, `backend/routes/v130_lobby_launch_context.py`,
`backend/routes/v131_combat_preview.py`: **non toccati**.

## 5) Diff summary

```text
backend/helpers/team_formation_contract.py   +268 (new)
backend/routes/v96_team_formation.py         ~120 changed (Pydantic model + save body + get normalize)
backend/helpers/real_player_snapshot.py      ~50  changed (uh_ids da V1; slot map; expose v1+warnings)
frontend/app/(tabs)/battle.tsx               ~20  changed (payload V1; loader V1-aware)
+ 4 validator nuovi, 1 manifest JSON, 1 report MD
```

## 6) Old contract ambiguity evidence

Vedi sezione 1.bis. Pre-HOTFIX E:

| Sorgente | Forma persistita |
|---|---|
| Pack 87 starter claim | `{slot_index: 0..8, user_hero_id: <uuid>}` |
| Pack 125 frontend save | `{hero_id: h.id, col, row}` — `hero_id` era in realtà `user_heroes.id` |
| Pack 125 backend save | validava `hero_id` contro `user_heroes.hero_id` (canonical) — **mismatch** |
| Pack 130 snapshot | `entry.get('user_hero_id') or entry.get('hero_id')` — `hero_id` trattato come owned id |

## 7) New TeamFormation V1 contract evidence

File `backend/helpers/team_formation_contract.py`. Forma canonica:

```python
{
  "user_hero_id": "<owned user_heroes.id>",
  "canonical_id": "<catalog hero id = user_heroes.hero_id>",
  "col": 0..2,
  "row": 0..2,
}
```

Costanti esportate:

- `TEAM_FORMATION_CONTRACT_VERSION = "hotfix_e_team_formation_v1"`
- `TEAM_FORMATION_V1_MAX_MEMBERS = 6` (Pack 125 cap **invariato**, no inflation)
- 10 blocker codes (vedi punto 13)

Helper:

- `slot_index_to_grid(si) -> (col, row)` (legacy Pack 87)
- `normalize_slot_to_v1(entry, owned_maps) -> (slot_v1 | err)`
- `normalize_team_formation_to_v1(team, owned_maps) -> (v1_list, warnings)`
- `validate_v1_team_for_save(slots, owned_map, server_id) -> (validated | err)`

## 8) Frontend save payload evidence

In `frontend/app/(tabs)/battle.tsx` (`saveTeam`):

```ts
// HOTFIX E — Payload TeamFormation V1.
const team_formation: { user_hero_id: string; canonical_id: string;
                        col: number; row: number }[] = [];
for (let col = 0; col < 3; col++) {
  for (let row = 0; row < 3; row++) {
    const h = grid[col]?.[row];
    if (h && h.id) {
      team_formation.push({
        user_hero_id: h.id,
        canonical_id: h.hero_id || h.canonical_id || h.id,
        col, row,
      });
    }
  }
}
```

Vecchio pattern `team_formation.push({hero_id: h.id, col, row})` **rimosso**
(verificato dal Validator 2 con regex).

## 9) Backend save validation evidence

In `backend/routes/v96_team_formation.py`:

```python
class TeamSlotV1(BaseModel):
    user_hero_id: str = Field(..., min_length=1, max_length=128)
    canonical_id: str = Field(..., min_length=1, max_length=128)
    col: int = Field(..., ge=0, le=2)
    row: int = Field(..., ge=0, le=2)

class SaveFormationRequest(BaseModel):
    server_id: str = Field(..., min_length=1)
    team_formation: List[TeamSlotV1] = Field(default_factory=list)
```

Validation pipeline:

1. cap dim ≤ `TEAM_FORMATION_V1_MAX_MEMBERS` (6) → `TEAM_FORMATION_TOO_MANY_MEMBERS`;
2. PSP `(uid, server_id)` deve esistere → `PLAYER_SERVER_PROFILE_REQUIRED`;
3. ownership: `user_hero_id` deve essere in `user_heroes(user_id=uid)` →
   `TEAM_FORMATION_OWNED_HERO_NOT_FOUND`;
4. server-scope: owned record deve avere `server_id` matchante (o `_qa_seed`)
   → `TEAM_FORMATION_SERVER_SCOPE_MISMATCH`;
5. canonical cross-check: `canonical_id == user_heroes.hero_id` →
   `TEAM_FORMATION_CANONICAL_MISMATCH`;
6. no duplicate `user_hero_id` → `TEAM_FORMATION_DUPLICATE_USER_HERO`;
7. no duplicate `(col, row)` → `TEAM_FORMATION_DUPLICATE_CELL`.

HTTP status mapping coerente con Hotfix B: 400 default, 404 owned not found,
409 server-scope mismatch, 409 PSP missing.

## 10) Backend get normalization evidence

`GET /api/team/get-formation?server_id=...` ora carica `user_heroes`
server-scoped, costruisce `owned_by_user_hero_id` + `owned_by_canonical_id`,
e chiama `normalize_team_formation_to_v1`. Response include:

```python
{
  "team_formation": v1_slots,              # forma V1 normalizzata (consumer FE / snapshot)
  "team_formation_raw": psp_team,          # forma raw persistita (QA visibility)
  "team_formation_contract_version": "hotfix_e_team_formation_v1",
  "team_formation_v1_warnings": [...],     # entries non normalizzabili
  ...
}
```

Nessun DB write durante il GET — normalizzazione esclusivamente on-read.

## 11) Legacy starter formation compatibility evidence

Lo starter Pack 87 persiste `{slot_index, user_hero_id}`. HOTFIX E lo legge
così:

- `user_hero_id` → direttamente come owned id;
- `slot_index` → mappato a `(col, row)` via `slot_index_to_grid(si)` con
  convenzione `col = si // 3, row = si % 3` (mirror del frontend grid).
- `canonical_id` non presente nel record starter → derivato dal record
  `user_heroes` matchato (`owned_by_user_hero_id[uh].hero_id`).

Le formazioni starter esistenti continuano quindi a essere leggibili
senza alcuna migrazione DB.

## 12) `real_player_snapshot` alignment evidence

In `backend/helpers/real_player_snapshot.py`:

```python
from helpers.team_formation_contract import normalize_team_formation_to_v1 as _hf_e_normalize
v1_team, v1_warnings = _hf_e_normalize(
    team_formation, owned_by_user_hero_id_pre, owned_by_canonical_id_pre,
)
uh_ids: List[str] = [str(entry.get('user_hero_id'))
                      for entry in v1_team if entry.get('user_hero_id')]
```

- Il vecchio pattern `entry.get('user_hero_id') or entry.get('hero_id')`
  per la costruzione di `uh_ids` è stato **rimosso** (verificato dal
  Validator 3).
- `slot_by_uh_id` ora derivato dalla forma V1, `canonical_id` esposto
  solo come metadata.
- Snapshot output include `team_formation_v1` + `team_formation_v1_warnings`
  per downstream visibility (`combat_preview_adapter`, `lobby_launch_context`
  — fuori scope HOTFIX E).
- Zero DB writes nel modulo snapshot (verificato dal Validator 3 con
  blacklist `insert_one/update_one/delete_one/...`).

## 13) Duplicate / mismatch blocker evidence

10 blocker codes esportati dal contratto + verificati nel route:

```text
TEAM_FORMATION_V1_REQUIRED
TEAM_FORMATION_USER_HERO_ID_REQUIRED
TEAM_FORMATION_CANONICAL_ID_REQUIRED
TEAM_FORMATION_OWNED_HERO_NOT_FOUND
TEAM_FORMATION_SERVER_SCOPE_MISMATCH
TEAM_FORMATION_CANONICAL_MISMATCH
TEAM_FORMATION_DUPLICATE_USER_HERO
TEAM_FORMATION_DUPLICATE_CELL
TEAM_FORMATION_TOO_MANY_MEMBERS
TEAM_FORMATION_LEGACY_AMBIGUOUS    (emesso da get-normalization quando
                                    legacy hero_id matcha più owned record)
```

Più `PLAYER_SERVER_PROFILE_REQUIRED` (preservato Pack 88).

## 14) Validators results

```text
validate_hotfix_e_teamformation_v1_contract   PASS  (rc=0, 10 blocker codes verificati)
validate_hotfix_e_frontend_payload            PASS  (rc=0, payload V1 + loader V1-aware)
validate_hotfix_e_snapshot_alignment          PASS  (rc=0, no DB writes, no canonical-as-owned)
validate_hotfix_e_no_scope_drift              PASS  (rc=0, 8 file in scope, 0 drift)
```

Hotfix A+B+C+D **non indeboliti**:

```text
validate_security_hotfix_a_battle_simulate_guard   PASS
validate_security_hotfix_a_jwt_secret_preflight    PASS
validate_hotfix_b_api_error_contract               PASS
validate_hotfix_b_blocker_visibility               PASS
validate_hotfix_c_server_select_fail_closed        PASS
validate_hotfix_d_starter_roster_contract          PASS
validate_hotfix_d_user_heroes_exposure             PASS
```

## 15) Smoke results

- `python -m py_compile backend/routes/v96_team_formation.py
  backend/helpers/real_player_snapshot.py
  backend/helpers/team_formation_contract.py
  backend/scripts/validate_hotfix_e_*.py`: **OK** (exit 0).
- `from backend.helpers.team_formation_contract import normalize_team_formation_to_v1,
  validate_v1_team_for_save`: importabile.
- `sudo supervisorctl restart backend` → RUNNING.
- `curl http://localhost:8001/api/health` → **HTTP 200**.
- JSON validity di `data/design/system_safety/hotfix_e_teamformation_v1_contract.json`: OK.
- Frontend lint `eslint frontend/app/(tabs)/battle.tsx`: **0 errori**,
  12 warning **tutti pre-esistenti** (Dimensions, ROW_YS, _logE, _se,
  refreshUser, V2Effect, hooks deps — non introdotti da HOTFIX E).
- Endpoint mutativi runtime durante test: **0 chiamati**.

## 16) Scope guard confirmation

`validate_hotfix_e_no_scope_drift.py` ha rilevato 8 file in scope:

```text
+ backend/helpers/real_player_snapshot.py
+ backend/helpers/team_formation_contract.py
+ backend/routes/v96_team_formation.py
+ backend/scripts/validate_hotfix_e_frontend_payload.py
+ backend/scripts/validate_hotfix_e_no_scope_drift.py
+ backend/scripts/validate_hotfix_e_snapshot_alignment.py
+ backend/scripts/validate_hotfix_e_teamformation_v1_contract.py
+ frontend/app/(tabs)/battle.tsx
```

`EXPLICIT_FORBIDDEN` list copre: `battle_engine.py`, `jwt_secret_preflight.py`,
`server.py`, `v96_auth.py`, `v130_lobby_launch_context.py`,
`v131_combat_preview.py`, `api.ts`, `servers.tsx`, `heroes.tsx`,
`heroes_master.json`, `character_bible.py`, `starter_roster_contract.py`
(HOTFIX D intoccabile). Nessuno appare nel diff.

## 17) DB writes durante test

**0**. Validators 100% statici. Backend restart non muta dati. Il save endpoint
NON è stato chiamato dai validator. Il modulo snapshot NON contiene scritture
(blacklist verificata).

## 18) Endpoint mutativi runtime test

**0** chiamati. Lista vietata rispettata:

```text
POST /api/team/save-formation     ← non chiamato
POST /api/psp/ensure              ← non chiamato
POST /api/psp/starter/claim       ← non chiamato
POST /api/battle/simulate         ← non chiamato
```

Nessun nuovo endpoint mutativo introdotto da HOTFIX E.

## 19) Remaining P0 / P1 / P2

### P0 ancora aperti dopo HOTFIX E

- Re-audit Game Master + Codex Web congiunto Hotfix A+B+C+D+E.
- Suite Pack 127-133 con drift atteso: previsione **≥17 FAIL**
  (= 13 da Hotfix A+B+C documentati in 538, + 2 da Hotfix D backend
  drift, + ≥2 nuovi da HOTFIX E su `v96_team_formation.py` e
  `real_player_snapshot.py` verso Pack 130/131 frontend/runtime
  validators). Drift di snapshot, NON regressioni semantiche.

### P1

- `BATTLE_SIMULATE_LIVE_ENABLED` residual P1 (fuori scope).
- Lobby launch context / combat preview adapter consumo
  `team_formation_v1` (oggi continuano a leggere il vecchio shape via
  fallback; safe perché V1 e legacy convivono nel response).
- Bug fuori scope `heroes.tsx:230 filtered.map(...)`: **non corretto**.
- DB migration legacy `team_formation` (fuori scope HOTFIX E).

### P2

- Catalogo / I Miei Eroi / Formazione naming canonization.
- Localizzazione testi blocker (oggi solo codici).

## 20) Next recommended step

1. Commit HOTFIX E (auto-pipeline o manuale) e truth-sync di questo report
   sostituendo `<TRUTH_SYNC_PENDING>` con lo SHA reale.
2. Game Master + Codex Web re-audit Hotfix A+B+C+D+E.
3. Se promosso, fork dedicato per estendere il consumo di
   `team_formation_v1` in `combat_preview_adapter` /
   `lobby_launch_context` (HOTFIX F candidato — read-only).
4. In parallelo, fork per il bug fuori scope `heroes.tsx filtered.map`
   (HOTFIX G candidato).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = HOTFIX_E_TEAMFORMATION_V1_READY_FOR_REAUDIT
```
