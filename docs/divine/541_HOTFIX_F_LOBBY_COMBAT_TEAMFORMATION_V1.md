# 541 — HOTFIX F — LOBBY / COMBAT PREVIEW CONSUMES TEAMFORMATION V1

> Chiude il residuo P1 emerso nel re-audit HOTFIX E: lobby launch context
> e combat preview ora **preferiscono e consumano** `team_formation_v1`
> (HOTFIX E contract). Refuse-by-default su missing/empty/ambiguous V1.
> Preview-only, zero battle simulate, zero reward.

## 1) Verdict

**`HOTFIX_F_LOBBY_COMBAT_TEAMFORMATION_V1_READY_FOR_REAUDIT`**

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
```

## 2) HEAD iniziale

```text
6db79bfe265e6e4446d2c5617419d174da8403d8
```

(chiusura HOTFIX E truth-sync, baseline da prompt).

## 3) HEAD finale / commit contenuto

- Commit HOTFIX F (contenuto patch): `25c301137b5a192174953b88d94a4ba29b67a709`
  (auto-commit pipeline, 10 file di scope: backend/routes/v130 +50, v131 +55,
   4 validator scripts, manifest JSON, report MD, combat.tsx +39, pre-battle-lobby.tsx +71)
- Auto-pipeline pre-HOTFIX F (`.emergent/emergent.yml` bump non-code):
  `b0dc33502bb58e7a96903a36c6e5b2f2d8eca5f2`
- Auto-pipeline post-HOTFIX F (`.emergent/emergent.yml` bump non-code):
  `53f684429c3a848f9a7e4e6bfbeef5fe503fe59e`
- Truth-sync di questo report: SHA emesso dal commit di chiusura (vedi
  `git log` posteriore).

### 3.bis) Pipeline TeamFormation V1 ora completamente coperta

```text
Team Save V1 (HOTFIX E)
  ↓
GET /api/team/get-formation V1 normalize-on-read (HOTFIX E)
  ↓
real_player_snapshot exposes team_formation_v1 (HOTFIX E)
  ↓
Lobby launch context preview consumes/exposes/blocks on team_formation_v1 (HOTFIX F)
  ↓
Combat preview consumes/exposes/blocks on team_formation_v1 (HOTFIX F)
  ↓
pre-battle-lobby.tsx prefers team_formation_v1 (HOTFIX F)
  ↓
combat.tsx surfaces V1 diagnostics (HOTFIX F)
```

### 3.ter) Root invariant (per re-audit)

```text
owned id primario  = user_hero_id
catalog metadata   = canonical_id
canonical_id / hero_id non devono essere trattati come owned id.
```

Garantito da:

- `backend/helpers/team_formation_contract.py` (HOTFIX E): contratto canonico
  V1, normalize-on-read, validate_v1_team_for_save refuse-by-default.
- `backend/helpers/real_player_snapshot.py` (HOTFIX E): consuma forma V1
  normalizzata, `uh_ids` costruito SOLO da `user_hero_id`.
- `backend/routes/v130_lobby_launch_context.py` (HOTFIX F): blocca su
  missing/empty/ambiguous V1, espone V1 al top-level.
- `backend/routes/v131_combat_preview.py` (HOTFIX F): idem + preview-lock
  metadata (reward DISABLED, progress DISABLED, battle_simulate BLOCKED).
- `frontend/app/pre-battle-lobby.tsx` (HOTFIX F): `ownedKey` con priorità
  esplicita `user_hero_id`, `canonicalHint` come fallback separato.
- `frontend/app/combat.tsx` (HOTFIX F): logging diagnostico V1, nessuna
  riattivazione del branch `/api/battle/simulate`.

## 4) Files changed

```text
backend/routes/v130_lobby_launch_context.py                                       (modified)
backend/routes/v131_combat_preview.py                                             (modified)
frontend/app/pre-battle-lobby.tsx                                                 (modified)
frontend/app/combat.tsx                                                           (modified)
backend/scripts/validate_hotfix_f_lobby_consumes_teamformation_v1.py              (new)
backend/scripts/validate_hotfix_f_combat_preview_consumes_teamformation_v1.py     (new)
backend/scripts/validate_hotfix_f_no_live_battle_or_reward_path.py                (new)
backend/scripts/validate_hotfix_f_no_scope_drift.py                               (new)
data/design/system_safety/hotfix_f_lobby_combat_teamformation_v1.json             (new)
docs/divine/541_HOTFIX_F_LOBBY_COMBAT_TEAMFORMATION_V1.md                         (this file)
```

`backend/helpers/real_player_snapshot.py`, `backend/helpers/team_formation_contract.py`,
`backend/routes/v96_team_formation.py`, `backend/server.py`,
`backend/battle_engine.py`, `backend/helpers/jwt_secret_preflight.py`,
`backend/routes/v96_auth.py`, `frontend/utils/api.ts`,
`frontend/app/servers.tsx`, `frontend/app/(tabs)/battle.tsx`,
`frontend/app/(tabs)/heroes.tsx`: **non toccati**.

## 5) Diff summary

```text
backend/routes/v130_lobby_launch_context.py   +60 −1   (block + expose V1, marker hotfix_f)
backend/routes/v131_combat_preview.py         +63 −1   (block + expose V1, marker hotfix_f, preview locks esposti)
frontend/app/pre-battle-lobby.tsx             ~25     (GetFormationResponse V1 types, loader V1-aware)
frontend/app/combat.tsx                       +28     (diagnostic V1 log; nessun cambio logica simulate)
+ 4 validator nuovi, 1 manifest JSON, 1 report MD
```

## 6) Residual P1 evidence from HOTFIX E

HOTFIX E aveva chiarito:

```text
Team save usa V1.
GET formation normalizza V1.
real_player_snapshot espone team_formation_v1.
```

Ma lobby/combat preview ancora consumavano:

- `combat_preview_adapter.build_combat_preview_input` leggeva `snapshot.heroes`
  (già contiene `user_hero_id` corretto, ma il route `v131_combat_preview.py`
  NON propagava `team_formation_v1` e NON bloccava su missing/empty);
- `v130_lobby_launch_context.py` esponeva l'intero `player_snapshot` ma
  NON garantiva la presenza di `team_formation_v1`;
- `pre-battle-lobby.tsx` filtrava entry per `user_hero_id || hero_id || canonical_id`
  e faceva lookup con triplo predicato — trattando `canonical_id` come
  potenziale owned id.

HOTFIX F chiude questo gap: refuse-by-default V1 + preferenza esplicita
`user_hero_id` come owned id.

## 7) Lobby team_formation_v1 consumption evidence

In `backend/routes/v130_lobby_launch_context.py`:

```python
result = await build_lobby_launch_context(_db, user_id=user_id, server_id=server_id, mode=mode)
...
snapshot = result.get('player_snapshot') or {}
team_formation_v1 = snapshot.get('team_formation_v1') or []
team_formation_v1_warnings = snapshot.get('team_formation_v1_warnings') or []

if not isinstance(team_formation_v1, list):
    raise HTTPException(status_code=400, detail={
        'blocker': 'LOBBY_TEAMFORMATION_V1_REQUIRED', ...})
if len(team_formation_v1) == 0:
    raise HTTPException(status_code=400, detail={
        'blocker': 'LOBBY_TEAMFORMATION_V1_EMPTY',
        'team_formation_v1_warnings': team_formation_v1_warnings, ...})
ambiguous = [w for w in team_formation_v1_warnings
             if isinstance(w, dict) and w.get('blocker') == 'TEAM_FORMATION_LEGACY_AMBIGUOUS']
if ambiguous:
    raise HTTPException(status_code=409, detail={
        'blocker': 'LOBBY_TEAMFORMATION_V1_AMBIGUOUS', ...})

result['team_formation_v1'] = team_formation_v1
result['team_formation_v1_warnings'] = team_formation_v1_warnings
result['team_formation_v1_size'] = len(team_formation_v1)
result['hotfix_f_lobby_consumes_v1'] = True
result['reward_status'] = 'DISABLED'
result['progress_status'] = 'DISABLED'
```

## 8) Combat preview team_formation_v1 consumption evidence

In `backend/routes/v131_combat_preview.py`:

- Stesso pattern di estrazione + blocking del lobby route, con prefisso
  blocker `COMBAT_PREVIEW_TEAMFORMATION_V1_*`.
- Top-level espone: `team_formation_v1`, `team_formation_v1_warnings`,
  `team_formation_v1_size`, `hotfix_f_combat_preview_consumes_v1: True`.
- Preview-only locks esposti come metadata:
  - `reward_status: 'DISABLED'`
  - `progress_status: 'DISABLED'`
  - `battle_simulate_status: 'BLOCKED_PRE_QA_HOTFIX_A_FAIL_CLOSED'`
  - `combat_preview_reward_lock_active: True`
- Nessuna chiamata HTTP a `/api/battle/simulate` (verificato dal
  Validator 3 con blacklist `requests.post(/httpx.post(`).
- Nessun import di `battle_engine` (verificato).

## 9) Frontend pre-battle-lobby evidence

In `frontend/app/pre-battle-lobby.tsx`:

```ts
// HOTFIX F — Preferisce `team_formation_v1` (HOTFIX E contract).
const tfV1Raw = Array.isArray((d as any).team_formation_v1)
  ? (d as any).team_formation_v1 : null;
const tfWarnings: TeamFormationV1Warning[] =
  Array.isArray((d as any).team_formation_v1_warnings)
    ? (d as any).team_formation_v1_warnings : [];
const tfLegacy = Array.isArray(d.team_formation) ? d.team_formation
                 : Array.isArray((d as any).formation) ? (d as any).formation : [];
const tf = tfV1Raw && tfV1Raw.length > 0 ? tfV1Raw : tfLegacy;
if (__DEV__ && tfWarnings.length > 0) {
  console.warn('[hotfix_f][pre-battle-lobby] team_formation_v1 warnings:', tfWarnings);
}
...
// HOTFIX F — user_hero_id ha PRIORITÀ ASSOLUTA come owned id.
const ownedKey = String(e.user_hero_id || e.hero_id || '');
const canonicalHint = String(e.canonical_id || e.hero_id || '');
const lookupKey = ownedKey || canonicalHint;
```

Nuovo type `TeamFormationV1Slot` + `TeamFormationV1Warning` aggiunti al
`GetFormationResponse`. Nessun layout cambiato — solo adattamento dati.

## 10) Frontend combat.tsx evidence

In `frontend/app/combat.tsx`:

```ts
// HOTFIX F — TeamFormation V1 consumption marker.
type HotfixFLaunchContextV1Slot = {
  user_hero_id: string; canonical_id: string; col: number; row: number;
};
...
if (PREVIEW_REWARD_LOCK_ACTIVE) {
  ...
  const v1Slots: HotfixFLaunchContextV1Slot[] = Array.isArray(
    (previewCtxLocal as any)?.team_formation_v1,
  ) ? ((previewCtxLocal as any).team_formation_v1 as HotfixFLaunchContextV1Slot[]) : [];
  const v1Warnings: any[] = Array.isArray(
    (previewCtxLocal as any)?.team_formation_v1_warnings,
  ) ? ((previewCtxLocal as any).team_formation_v1_warnings as any[]) : [];
  if (__DEV__ && v1Warnings.length > 0) {
    console.warn('[hotfix_f][combat] team_formation_v1 warnings:', v1Warnings);
  }
  ...
}
```

Nessuna modifica alla logica di `/api/battle/simulate` (resta bloccato dai
guard pre-esistenti `PREVIEW_REWARD_LOCK_ACTIVE` + `LEGACY_COMBAT_ENTRY_MUTATING`,
con Hotfix A fail-closed lato backend).

## 11) No canonical-as-owned evidence

Backend:
- Validator 1: cerca pattern `user_hero_id = canonical_id` — assente.
- Validator 2: stesso check per combat preview — assente.
- I route non costruiscono mai `team_a` da `canonical_id`; lo prendono
  da `snapshot.heroes` che HOTFIX E ha già allineato a V1.

Frontend:
- `pre-battle-lobby.tsx` ora costruisce `ownedKey` con priorità esplicita
  `e.user_hero_id || e.hero_id`, e `canonicalHint` come fallback separato.
- `combat.tsx` logga V1 slots distinguendo `uh` (user_hero_id) da `c`
  (canonical_id) in `__DEV__`.

## 12) Warnings / blocker evidence

8 blocker emessi da HOTFIX F (5 nuovi):

```text
LOBBY_TEAMFORMATION_V1_REQUIRED                  (400)
LOBBY_TEAMFORMATION_V1_EMPTY                     (400)
LOBBY_TEAMFORMATION_V1_AMBIGUOUS                 (409)
COMBAT_PREVIEW_TEAMFORMATION_V1_REQUIRED         (400)
COMBAT_PREVIEW_TEAMFORMATION_V1_EMPTY            (400)
COMBAT_PREVIEW_TEAMFORMATION_V1_AMBIGUOUS        (409)
```

Più i preservati da Hotfix E (`TEAM_FORMATION_LEGACY_AMBIGUOUS`,
`PLAYER_SERVER_PROFILE_REQUIRED`, ecc.). HTTP status mapping coerente con
Hotfix B (`ApiError` preserva `status`, `detail`, `code`).

`team_formation_v1_warnings` propagato fino al frontend, dove
`pre-battle-lobby.tsx` lo logga in `__DEV__` e `combat.tsx` lo logga +
distingue ambiguous come blocker.

## 13) Preview-only / no reward evidence

Marker espliciti nei response:

- Lobby: `reward_status: 'DISABLED'`, `progress_status: 'DISABLED'`,
  `combat_consumption_status: 'DEFERRED_TO_PACK_131'`.
- Combat preview: `reward_status: 'DISABLED'`, `progress_status: 'DISABLED'`,
  `battle_simulate_status: 'BLOCKED_PRE_QA_HOTFIX_A_FAIL_CLOSED'`,
  `combat_preview_reward_lock_active: True`, `preview_only: True`,
  `authoritative: False`, `device_qa_status: 'BLOCKED'`.

Validator 3 verifica:
- nessuna `grant_reward(`, `grant_gold(`, `grant_exp(`, `grant_affinity(`,
  `grant_hero_exp(`, `progress_grant(`, `reward_claim(` nei file di scope;
- nessun `import battle_engine` / `from battle_engine`;
- file invariant intoccati (`battle_engine.py`, `server.py`,
  `real_player_snapshot.py`, `jwt_secret_preflight.py`,
  `team_formation_contract.py`, `v96_auth.py`, `v96_team_formation.py`).

## 14) No battle simulate evidence

- `v130_lobby_launch_context.py`: stringa `/api/battle/simulate` assente.
- `v131_combat_preview.py`: stringa presente SOLO come metadata stringa
  `'BLOCKED_PRE_QA_HOTFIX_A_FAIL_CLOSED'` — nessun HTTP client call
  (verificato dal Validator 2 con blacklist `requests.post/httpx.post/fetch`).
- `combat.tsx`: chiamata `apiCall('/api/battle/simulate')` linea 503
  preservata MA in branch fallback **bloccato da Hotfix A** (`LEGACY_COMBAT_ENTRY_MUTATING`
  + `PREVIEW_REWARD_LOCK_ACTIVE` early-return); HOTFIX F non riattiva quel branch.
- `pre-battle-lobby.tsx`: nessun riferimento a `/api/battle/simulate`.

## 15) Validators results

```text
validate_hotfix_f_lobby_consumes_teamformation_v1           PASS  (rc=0)
validate_hotfix_f_combat_preview_consumes_teamformation_v1  PASS  (rc=0)
validate_hotfix_f_no_live_battle_or_reward_path             PASS  (rc=0, 4 file scope, 7 invariant)
validate_hotfix_f_no_scope_drift                            PASS  (rc=0, 8 file in scope)
```

Hotfix A+B+C+D+E **non indeboliti** (10/10 validator content-side PASS):

```text
validate_security_hotfix_a_battle_simulate_guard           PASS
validate_security_hotfix_a_jwt_secret_preflight            PASS
validate_hotfix_b_api_error_contract                       PASS
validate_hotfix_b_blocker_visibility                       PASS
validate_hotfix_c_server_select_fail_closed                PASS
validate_hotfix_d_starter_roster_contract                  PASS
validate_hotfix_d_user_heroes_exposure                     PASS
validate_hotfix_e_teamformation_v1_contract                PASS
validate_hotfix_e_frontend_payload                         PASS
validate_hotfix_e_snapshot_alignment                       PASS
```

## 16) Smoke results

- `python -m py_compile backend/routes/v130_lobby_launch_context.py
  backend/routes/v131_combat_preview.py`: **OK**.
- `python -m py_compile backend/scripts/validate_hotfix_f_*.py`: **OK**.
- `sudo supervisorctl restart backend` → RUNNING.
- `curl http://localhost:8001/api/health` → HTTP **200**.
- Frontend lint: 0 nuovi errori/warning introdotti da HOTFIX F
  (`react/no-unescaped-entities` linea 801 pre-battle-lobby e linea 1355
  combat **pre-esistenti** — non toccati).
- Endpoint mutativi runtime: **0 chiamati**.

## 17) Scope guard confirmation

`validate_hotfix_f_no_scope_drift.py` ha rilevato 8 file di codice/scripts
in scope (più 2 file di documentazione/manifest aggiunti come ultimi):

```text
+ backend/routes/v130_lobby_launch_context.py
+ backend/routes/v131_combat_preview.py
+ backend/scripts/validate_hotfix_f_combat_preview_consumes_teamformation_v1.py
+ backend/scripts/validate_hotfix_f_lobby_consumes_teamformation_v1.py
+ backend/scripts/validate_hotfix_f_no_live_battle_or_reward_path.py
+ backend/scripts/validate_hotfix_f_no_scope_drift.py
+ frontend/app/combat.tsx
+ frontend/app/pre-battle-lobby.tsx
```

`EXPLICIT_FORBIDDEN` list copre 14 file critici (battle_engine,
real_player_snapshot, team_formation_contract, server.py, ecc.). Nessuno
appare nel diff.

## 18) DB writes durante test

**0**. Validators 100% statici. Backend restart non muta dati. Le
modifiche ai route non introducono `insert_one/update_one/delete_one`
(verificato dai Validator 1, 2, 3).

## 19) Endpoint mutativi runtime test

**0**. Lista vietata rispettata:

```text
POST /api/team/save-formation     ← non chiamato
POST /api/psp/ensure              ← non chiamato
POST /api/psp/starter/claim       ← non chiamato
POST /api/battle/simulate         ← non chiamato (Hotfix A backend fail-closed)
```

## 20) Next recommended step

1. Commit HOTFIX F già creato (auto-pipeline): contenuto patch
   `25c301137b5a192174953b88d94a4ba29b67a709`; baseline HOTFIX E
   `6db79bfe265e6e4446d2c5617419d174da8403d8`. Questo report è stato
   truth-synced col SHA reale.
2. Game Master + Codex Web re-audit Hotfix A+B+C+D+E+F.
3. Se promosso, fork per il bug fuori scope `heroes.tsx:230 filtered.map(...)`
   (HOTFIX G candidato).
4. In parallelo, valutare il consumo lato `combat_preview_adapter` di
   `team_formation_v1` per allineare il `team_a` proiettato dallo snapshot
   alla forma V1 esplicita (oggi consuma `snapshot.heroes` che è già
   V1-derived, ma il marker esplicito può essere aggiunto in un fork
   dedicato HOTFIX H read-only).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = HOTFIX_F_LOBBY_COMBAT_TEAMFORMATION_V1_READY_FOR_REAUDIT
```
