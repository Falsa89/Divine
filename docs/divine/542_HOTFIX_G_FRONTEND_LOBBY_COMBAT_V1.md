# 542 — HOTFIX G — FRONTEND PRE-BATTLE → COMBAT PROPAGATES TEAMFORMATION V1

> Chiude il residuo P1 emerso nel re-audit HOTFIX F: il `team_formation_v1`
> (HOTFIX E contract) ora viene **propagato dal frontend lobby al combat
> view** dentro il payload JSON di `launch_context` ed è **fail-closed**
> validato in `combat.tsx` prima di costruire qualsiasi snapshot locale.
> Preview-only, zero battle simulate, zero reward, zero DB writes.

## 1) Verdict

**`HOTFIX_G_FRONTEND_LOBBY_COMBAT_V1_READY_FOR_REAUDIT`**

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
```

## 2) HEAD iniziale

```text
cd230e7f519269efcbbd10d012331badc41d0757
```

(chiusura HOTFIX F truth-sync, baseline da prompt).

## 3) HEAD finale / commit contenuto

- Commit HOTFIX G (contenuto patch): `<TRUTH_SYNC_PENDING>`
  (pipeline auto-commit: 6 file di scope — combat.tsx +96/-43, 4 validator
   scripts, manifest JSON, report MD)
- Auto-pipeline pre-HOTFIX G (`.emergent/emergent.yml` bump non-code):
  `<TRUTH_SYNC_PENDING>`
- Auto-pipeline post-HOTFIX G (`.emergent/emergent.yml` bump non-code):
  `<TRUTH_SYNC_PENDING>`
- Truth-sync di questo report: SHA emesso dal commit di chiusura (vedi
  `git log` posteriore).

### 3.bis) Pipeline TeamFormation V1 ora completamente coperta end-to-end

```text
Team Save V1 (HOTFIX E)
  ↓
GET /api/team/get-formation V1 normalize-on-read (HOTFIX E)
  ↓
real_player_snapshot expose team_formation_v1 (HOTFIX E)
  ↓
Lobby launch context preview consumes/exposes/blocks on team_formation_v1 (HOTFIX F)
  ↓
Combat preview consumes/exposes/blocks on team_formation_v1 (HOTFIX F)
  ↓
pre-battle-lobby.tsx state hotfixGTeamV1 + propaga V1 nel launch_context JSON (HOTFIX G)
  ↓
combat.tsx parsifica launch_context JSON + valida V1 fail-closed (HOTFIX G)
```

### 3.ter) Root invariant (per re-audit)

```text
owned id primario  = user_hero_id
catalog metadata   = canonical_id
canonical_id / hero_id non devono essere trattati come owned id.
team_formation_v1_size dichiarato == lunghezza reale degli slot V1.
```

Garantito da:

- `frontend/app/pre-battle-lobby.tsx` (HOTFIX G): stato React
  `hotfixGTeamV1` + `hotfixGTeamV1Warnings` popolati dalla risposta di
  `GET /api/team/get-formation`; guard fail-closed nello `startBattle()`
  PRIMA di `router.push(target...)`; payload `launchContext` esteso con
  `team_formation_v1`, `team_formation_v1_warnings`, `team_formation_v1_size`
  e marker `hotfix_g_frontend_v1_propagation: true`.
- `frontend/app/combat.tsx` (HOTFIX G): `JSON.parse(params.launch_context)`
  in `hotfixGRawLaunchContext`; estrazione `team_formation_v1`,
  `team_formation_v1_warnings`, `team_formation_v1_size`; quattro blocker
  fail-closed (`FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED|AMBIGUOUS|`
  `SIZE_MISMATCH|CANONICAL_AS_OWNED`); early-return con
  `setPhase('preview_locked')` — niente `buildPreviewCombatSnapshot`,
  niente `/api/battle/simulate`, niente `refreshUser/grantAffinity`.

## 4) Files changed

```text
frontend/app/combat.tsx                                                           (modified)
backend/scripts/validate_hotfix_g_frontend_lobby_to_combat_v1_payload.py          (new)
backend/scripts/validate_hotfix_g_combat_requires_v1_preview.py                   (new)
backend/scripts/validate_hotfix_g_no_live_battle_or_reward_path.py                (new)
backend/scripts/validate_hotfix_g_no_scope_drift.py                               (new)
data/design/system_safety/hotfix_g_frontend_lobby_combat_v1.json                  (new)
docs/divine/542_HOTFIX_G_FRONTEND_LOBBY_COMBAT_V1.md                              (this file)
```

`frontend/app/pre-battle-lobby.tsx` era già stato committato in HEAD
`cd230e7f...` con state `hotfixGTeamV1` + payload V1 + guard fail-closed
prima di questo job. Pertanto il diff in working-tree contiene solo le
modifiche di `combat.tsx` necessarie per *consumare* davvero il V1 dal
JSON di `launch_context` (HEAD precedente lo leggeva erroneamente da
`previewCtxLocal`, che NON contiene V1).

`backend/helpers/real_player_snapshot.py`, `backend/helpers/team_formation_contract.py`,
`backend/routes/v96_team_formation.py`, `backend/routes/v130_lobby_launch_context.py`,
`backend/routes/v131_combat_preview.py`, `backend/server.py`,
`backend/battle_engine.py`, `backend/helpers/jwt_secret_preflight.py`,
`backend/routes/v96_auth.py`, `frontend/utils/api.ts`,
`frontend/app/servers.tsx`, `frontend/app/(tabs)/battle.tsx`,
`frontend/app/(tabs)/heroes.tsx`: **non toccati**.

## 5) Diff summary

```text
frontend/app/combat.tsx                       +96 −43   (parse launch_context JSON, 4 blocker V1, early-return fail-closed)
+ 4 validator nuovi, 1 manifest JSON, 1 report MD
```

Pre-battle-lobby.tsx (già in HEAD):

```text
+ const [hotfixGTeamV1, setHotfixGTeamV1] = useState<TeamFormationV1Slot[]>([]);
+ const [hotfixGTeamV1Warnings, setHotfixGTeamV1Warnings] = useState<TeamFormationV1Warning[]>([]);
+ setHotfixGTeamV1(tfV1Raw || []);
+ setHotfixGTeamV1Warnings(tfWarnings);
+ const hgAmbiguous = hotfixGTeamV1Warnings.filter(w => w?.blocker === 'TEAM_FORMATION_LEGACY_AMBIGUOUS');
+ if (!Array.isArray(hotfixGTeamV1) || hotfixGTeamV1.length === 0) { ...FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED... return; }
+ if (hgAmbiguous.length > 0)              { ...FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS... return; }
+ const launchContext = { ..., team_formation_v1: hotfixGTeamV1, team_formation_v1_warnings: hotfixGTeamV1Warnings, team_formation_v1_size: hotfixGTeamV1.length, hotfix_g_frontend_v1_propagation: true };
```

## 6) Residual P1 evidence from HOTFIX F

HOTFIX F aveva chiarito:

```text
Backend lobby/combat preview routes consumano e bloccano su team_formation_v1.
Frontend pre-battle-lobby preferisce team_formation_v1 lato lettura.
Frontend combat.tsx logga solo diagnostica V1 (senza propagazione).
```

Ma il combat view ancora:

- **NON parsificava** `params.launch_context` (JSON string emesso dalla lobby);
- leggeva `team_formation_v1` da `previewCtxLocal`
  (`previewContextFromParams(params)`), che ritorna SOLO i 5 flag preview
  (`is_preview`, `reward_policy`, `progress_policy`, `battle_engine_mode`,
  `mode`) e **non** include V1;
- non aveva early-return su blocker V1: dopo aver loggato il blocker,
  proseguiva fino a `buildPreviewCombatSnapshot` costruendo un team
  preview canonico locale, in contraddizione con il fail-closed dichiarato.

Inoltre la lobby NON inseriva ancora V1 nel `launchContext` JSON router
param (codice della lobby in HEAD `cd230e7f...` lo aggiungeva).

HOTFIX G chiude entrambi i gap: la lobby propaga V1 dentro il JSON di
`launch_context`, e il combat lo parsifica, valida e fa early-return su
qualunque condizione fail-closed.

## 7) Lobby propagation evidence (frontend)

In `frontend/app/pre-battle-lobby.tsx` (HEAD `cd230e7f...`):

```ts
// HOTFIX G — state per propagazione V1 verso /combat.
const [hotfixGTeamV1, setHotfixGTeamV1] =
  useState<TeamFormationV1Slot[]>([]);
const [hotfixGTeamV1Warnings, setHotfixGTeamV1Warnings] =
  useState<TeamFormationV1Warning[]>([]);
...
setHotfixGTeamV1(tfV1Raw || []);
setHotfixGTeamV1Warnings(tfWarnings);
...
const startBattle = () => {
  ...
  // HOTFIX G — guard fail-closed prima di router.push.
  const hgAmbiguous = hotfixGTeamV1Warnings.filter(
    (w: any) => w?.blocker === 'TEAM_FORMATION_LEGACY_AMBIGUOUS',
  );
  if (!Array.isArray(hotfixGTeamV1) || hotfixGTeamV1.length === 0) {
    if (__DEV__) console.warn('[hotfix_g][pre-battle-lobby] V1 missing/empty:', {
      blocker: 'FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED',
      warnings: hotfixGTeamV1Warnings,
    });
    return;
  }
  if (hgAmbiguous.length > 0) {
    if (__DEV__) console.warn('[hotfix_g][pre-battle-lobby] V1 ambiguous:', {
      blocker: 'FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS',
      ambiguous: hgAmbiguous,
    });
    return;
  }
  // HOTFIX G — launch_context payload esteso V1.
  const launchContext = {
    battle_engine_mode: 'preview', is_preview: true,
    reward_policy: 'preview', progress_policy: 'preview',
    server_id: selectedServerId || 'unknown', mode,
    encounter_id: encounter.encounter_id,
    source_id: encounter.source_id,
    source_type: encounter.source_type,
    qa_fallback_used: qaFallbackEnabled && !launchAllowedNormal,
    team_formation_v1: hotfixGTeamV1,
    team_formation_v1_warnings: hotfixGTeamV1Warnings,
    team_formation_v1_size: hotfixGTeamV1.length,
    hotfix_g_frontend_v1_propagation: true,
  };
  const target = `/combat?...&launch_context=${encodeURIComponent(JSON.stringify(launchContext))}&...`;
  router.push(target as any);
};
```

`user_hero_id` resta owned id primario (`ownedKey = String(e.user_hero_id || e.hero_id || '')`),
`canonical_id` è solo `canonicalHint` separato. Nessuna chiamata POST a
endpoint mutativi introdotta.

## 8) Combat propagation evidence (frontend)

In `frontend/app/combat.tsx` (modificato in questo job):

```ts
if (PREVIEW_REWARD_LOCK_ACTIVE) {
  ...
  // HOTFIX G — Estrazione V1 dal payload JSON di `launch_context`.
  let hotfixGRawLaunchContext: any = null;
  try {
    const rawLc = (params as any)?.launch_context;
    if (typeof rawLc === 'string' && rawLc.length > 0) {
      hotfixGRawLaunchContext = JSON.parse(rawLc);
    } else if (rawLc && typeof rawLc === 'object') {
      hotfixGRawLaunchContext = rawLc;
    }
  } catch (_e) { hotfixGRawLaunchContext = null; }

  const v1Slots: HotfixFLaunchContextV1Slot[] = Array.isArray(
    hotfixGRawLaunchContext?.team_formation_v1,
  ) ? (hotfixGRawLaunchContext.team_formation_v1 as ...) : [];
  const v1Warnings: any[] = Array.isArray(
    hotfixGRawLaunchContext?.team_formation_v1_warnings,
  ) ? (... as any[]) : [];
  const v1SizeDeclared: number = Number.isFinite(
    hotfixGRawLaunchContext?.team_formation_v1_size,
  ) ? Number(hotfixGRawLaunchContext.team_formation_v1_size) : -1;

  const v1Ambiguous = v1Warnings.filter(
    (w: any) => w?.blocker === 'TEAM_FORMATION_LEGACY_AMBIGUOUS',
  );
  const v1SizeMismatch =
    v1SizeDeclared >= 0 && v1SizeDeclared !== v1Slots.length;
  const v1CanonicalAsOwned = v1Slots.some(
    (s: any) =>
      !s ||
      typeof s.user_hero_id !== 'string' ||
      s.user_hero_id.length === 0 ||
      s.user_hero_id === s.canonical_id,
  );
  const hotfixGV1Blocker: string | null =
    !Array.isArray(v1Slots) || v1Slots.length === 0
      ? 'FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED'
      : v1Ambiguous.length > 0
      ? 'FRONTEND_COMBAT_TEAMFORMATION_V1_AMBIGUOUS'
      : v1SizeMismatch
      ? 'FRONTEND_COMBAT_TEAMFORMATION_V1_SIZE_MISMATCH'
      : v1CanonicalAsOwned
      ? 'FRONTEND_COMBAT_TEAMFORMATION_V1_CANONICAL_AS_OWNED'
      : null;

  if (hotfixGV1Blocker) {
    if (__DEV__) console.warn('[hotfix_g][combat] V1 blocker, no fake team:', { ... });
    // Fail-closed: NIENTE snapshot locale, NIENTE simulate, NIENTE reward.
    setPhase('preview_locked' as any);
    setError(''); setLogLines([]); logLinesRef.current = [];
    return;
  }
  const snap = buildPreviewCombatSnapshot(previewCtxLocal);
  ...
}
```

Punti chiave:

- `JSON.parse(rawLc)` resolve V1 dal canale corretto (la lobby lo
  iniettava già in HEAD ma il combat lo cercava nel canale sbagliato).
- 4 blocker fail-closed (REQUIRED / AMBIGUOUS / SIZE_MISMATCH /
  CANONICAL_AS_OWNED), tutti con early-return — NESSUN ramo di codice
  successivo (snapshot locale, simulate, refreshUser, grantAffinity)
  viene eseguito quando il blocker è impostato.
- `setPhase('preview_locked')` riusa il branch esistente per UI
  diagnostica preview-only.

## 9) No fake team / no canonical-as-owned evidence

Validator 1 verifica nel `pre-battle-lobby.tsx`:

- assenza del pattern `user_hero_id = canonical_id`;
- assenza di `const ownedKey = String(e.canonical_id...)` (i.e.
  `canonical_id` NON è la sorgente primaria di owned id).

Validator 2 verifica nel `combat.tsx`:

- presenza del blocker esplicito `FRONTEND_COMBAT_TEAMFORMATION_V1_CANONICAL_AS_OWNED`
  con check `s.user_hero_id === s.canonical_id`;
- assenza del pattern `user_hero_id = canonical_id`;
- assenza di `const ownedKey = String(<id>.canonical_id...)`.

## 10) Size-mismatch / anti-tamper evidence

Il guard `v1SizeDeclared >= 0 && v1SizeDeclared !== v1Slots.length`
emette il blocker `FRONTEND_COMBAT_TEAMFORMATION_V1_SIZE_MISMATCH`
quando il numero dichiarato `team_formation_v1_size` non coincide con
la lunghezza reale di `team_formation_v1`. Questo evita tampering del
payload JSON da parte di client modificati (anche se il guard rimane
**diagnostico** preview-only: niente reward, niente progress, niente
autoritarietà di runtime).

## 11) Warnings / blocker evidence

10 blocker totali coinvolti nella pipeline V1 frontend (6 nuovi in
HOTFIX G):

```text
FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED           (lobby, no router.push)
FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS          (lobby, no router.push)
FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED          (combat, preview_locked)
FRONTEND_COMBAT_TEAMFORMATION_V1_AMBIGUOUS         (combat, preview_locked)
FRONTEND_COMBAT_TEAMFORMATION_V1_SIZE_MISMATCH     (combat, preview_locked)
FRONTEND_COMBAT_TEAMFORMATION_V1_CANONICAL_AS_OWNED(combat, preview_locked)
```

Più i preservati upstream:

```text
TEAM_FORMATION_LEGACY_AMBIGUOUS                    (warnings da HOTFIX E)
LOBBY_TEAMFORMATION_V1_REQUIRED|EMPTY|AMBIGUOUS    (backend HOTFIX F)
COMBAT_PREVIEW_TEAMFORMATION_V1_REQUIRED|EMPTY|AMBIGUOUS (backend HOTFIX F)
```

`team_formation_v1_warnings` viaggia integro dal backend (`HOTFIX E/F`)
fino al `combat.tsx`, dove il log dev distingue `uh` (user_hero_id) da
`c` (canonical_id) per ogni slot.

## 12) Preview-only / no reward evidence

Marker espliciti nel codice frontend:

- `pre-battle-lobby.tsx`: `launchContext.reward_policy: 'preview'`,
  `progress_policy: 'preview'`, `battle_engine_mode: 'preview'`,
  `is_preview: true`.
- `combat.tsx`: `PREVIEW_REWARD_LOCK_ACTIVE = !!(v108LaunchEnvelope.is_valid &&
  v108LaunchEnvelope.is_preview)`; quando attivo, sia il branch normale
  sia il branch `skip()` saltano `refreshUser()` e `grantAffinity(...)`.

Validator 3 verifica:

- nessun `grant_reward(`, `grant_exp(`, `grant_gold(`, `grant_drop(`,
  `grant_account_exp(`, `grant_affinity_runtime(` nei file di scope
  HOTFIX G;
- ogni `refreshUser()` e `grantAffinity(` in `combat.tsx` è preceduto
  entro 200 char da `!PREVIEW_REWARD_LOCK_ACTIVE`;
- `frontend/utils/api.ts` non modificato (ApiError marker HOTFIX B
  preservato);
- `backend/battle_engine.py` non modificato (marker
  `BATTLE_SIMULATE_LIVE_ENABLED` di Hotfix A preservato).

## 13) No battle simulate evidence

- `pre-battle-lobby.tsx`: assenza totale della stringa
  `/api/battle/simulate` (verificata dal Validator 1 e 3).
- `combat.tsx`: l'unico riferimento a `apiCall('/api/battle/simulate'`
  (linea pre-esistente) resta **gated** da:
  - `LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA` (early-return all'apertura di
    `startBattle()` se `LEGACY_COMBAT_ENTRY_MUTATING`);
  - `PREVIEW_REWARD_LOCK_ACTIVE` (early-return prima della call se in
    preview);
  - Hotfix A backend fail-closed (`BATTLE_SIMULATE_LIVE_ENABLED=false`).
  Validator 3 verifica che le posizioni di entrambi i guard precedano
  la chiamata.

## 14) PREVIEW_LOCKED render branch evidence

Quando `hotfixGV1Blocker` è settato, il combat view chiama
`setPhase('preview_locked')`. Il render branch è già definito da
HOTFIX F+precedenti (linea pre-esistente in `combat.tsx`) e mostra:

```text
🔒 Battaglia legacy bloccata
La combat senza launch_context valido userebbe il path legacy mutante backend.
In pre-QA è disattivato. Nessun reward, EXP, drop, progression o affinity grant
può essere applicato.
LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA
PRE_QA_COMBAT_REQUIRES_LAUNCH_CONTEXT
```

(il branch viene riusato come UI fail-closed; il blocker reale è loggato
in `__DEV__` con tutti i campi diagnostici).

## 15) Validators results

```text
validate_hotfix_g_frontend_lobby_to_combat_v1_payload   PASS  (rc=0)
validate_hotfix_g_combat_requires_v1_preview            PASS  (rc=0)
validate_hotfix_g_no_live_battle_or_reward_path         PASS  (rc=0)
validate_hotfix_g_no_scope_drift                        PASS  (rc=0, 6 file in scope working-tree)
```

Hotfix A+B+C+D+E+F **non indeboliti** (13/13 validator content-side PASS):

```text
validate_security_hotfix_a_battle_simulate_guard                  PASS
validate_security_hotfix_a_jwt_secret_preflight                   PASS
validate_hotfix_b_api_error_contract                              PASS
validate_hotfix_b_blocker_visibility                              PASS
validate_hotfix_c_server_select_fail_closed                       PASS
validate_hotfix_d_starter_roster_contract                         PASS
validate_hotfix_d_user_heroes_exposure                            PASS
validate_hotfix_e_teamformation_v1_contract                       PASS
validate_hotfix_e_frontend_payload                                PASS
validate_hotfix_e_snapshot_alignment                              PASS
validate_hotfix_f_lobby_consumes_teamformation_v1                 PASS
validate_hotfix_f_combat_preview_consumes_teamformation_v1        PASS
validate_hotfix_f_no_live_battle_or_reward_path                   PASS
```

## 16) Smoke results

- `python -m py_compile backend/scripts/validate_hotfix_g_*.py`: **OK**
  (4/4 compilati senza errori).
- `sudo supervisorctl restart backend` → RUNNING (pid 3329, uptime 23s
  al momento della verifica).
- `curl http://localhost:8001/api/health` → HTTP **200**,
  `{"status":"ok","game":"Divine Waifus","version":"1.0.0","bots":20}`.
- Lint frontend (`combat.tsx`): 38 warning **pre-esistenti** (import
  order, unused vars, exhaustive-deps, 2 `react/no-unescaped-entities`
  linea 1420 — tutti documentati anche in HOTFIX F report § 16).
  Nessun nuovo warning/error introdotto da HOTFIX G.
- Endpoint mutativi runtime: **0 chiamati**.
- DB writes runtime: **0**.

## 17) Scope guard confirmation

`validate_hotfix_g_no_scope_drift.py` ha rilevato 6 file di
codice/scripts modificati in working-tree vs HEAD `cd230e7f...`:

```text
+ backend/scripts/validate_hotfix_g_combat_requires_v1_preview.py
+ backend/scripts/validate_hotfix_g_frontend_lobby_to_combat_v1_payload.py
+ backend/scripts/validate_hotfix_g_no_live_battle_or_reward_path.py
+ backend/scripts/validate_hotfix_g_no_scope_drift.py
+ data/design/system_safety/hotfix_g_frontend_lobby_combat_v1.json
+ frontend/app/combat.tsx
```

`pre-battle-lobby.tsx` non appare nel diff working-tree perché le sue
modifiche HOTFIX G erano già state committate in HEAD baseline. Verifica
content-side da Validator 1 (PASS).

`EXPLICIT_FORBIDDEN` list copre 16 file critici (battle_engine,
real_player_snapshot, team_formation_contract, server.py, api.ts,
servers.tsx, battle.tsx, heroes.tsx, jwt_secret_preflight, v96_auth,
v96_team_formation, v130/v131 backend routes, heroes_master.json,
character_bible.py). Nessuno appare nel diff.

## 18) DB writes durante test

**0**. Validators 100% statici. Backend restart non muta dati. Le
modifiche a `combat.tsx` non introducono mai una scrittura DB lato
frontend (la modifica si limita a parsing JSON + flow control React).

## 19) Endpoint mutativi runtime test

**0**. Lista vietata rispettata:

```text
POST /api/team/save-formation     ← non chiamato
POST /api/psp/ensure              ← non chiamato (Pack 86 baseline
                                    pre-esistente in lobby — idempotente
                                    backend, NON aggiunto da HOTFIX G)
POST /api/psp/starter/claim       ← non chiamato
POST /api/battle/simulate         ← non chiamato (gated da HOTFIX A
                                    backend + LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA
                                    + PREVIEW_REWARD_LOCK_ACTIVE)
```

## 20) Next recommended step

1. Commit HOTFIX G (TBD): contenuto patch `<TRUTH_SYNC_PENDING>`;
   baseline HOTFIX F `cd230e7f519269efcbbd10d012331badc41d0757`. Truth-sync
   atteso col SHA reale dopo l'auto-pipeline commit.
2. Game Master + Codex Web re-audit Hotfix A+B+C+D+E+F+G.
3. Se promosso, candidato HOTFIX H read-only: hardening esplicito di
   `combat_preview_adapter.build_combat_preview_input` con marker V1
   esplicito sul `team_a` proiettato.
4. Fork dedicato per chiudere il residuo P1 `BATTLE_SIMULATE_LIVE_ENABLED=true`
   (ereditato da Hotfix A — escape valve legacy da rimuovere).
5. Fork separato per il bug fuori scope `heroes.tsx:230 filtered.map(...)`
   (segnalato come P2).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = HOTFIX_G_FRONTEND_LOBBY_COMBAT_V1_READY_FOR_REAUDIT
```
