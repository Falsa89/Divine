# 543 — FIX CHIRURGICO — TEAM FORMATION SERVER_REQUIRED DA useServerScope NON PRONTO

> Bug device QA: la schermata "FORMAZIONE SQUADRA" mostrava blocker
> `SERVER_REQUIRED` ("Nessun server selezionato — pre-QA gate") anche
> quando l'utente aveva già selezionato un server e l'account aveva
> eroi. Root cause: `battle.tsx` valutava `selected_server_id` prima
> che `useServerScope` finisse di leggere AsyncStorage. Fix minimo
> read-only sul componente.

## 1) Verdict

**`FIX_TEAM_SERVER_REQUIRED_SCOPE_READY_FOR_REAUDIT`**

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
```

## 2) HEAD iniziale

```text
aabaf8e2ee1642ca067fe9a48406ccdfc95a0eab
```

(HOTFIX G truth-sync, baseline da prompt).

## 2.bis) Catena commit FIX 543

```text
aabaf8e2ee1642ca067fe9a48406ccdfc95a0eab  HOTFIX G truth-sync (BASELINE)
  ↓
f334ead92                                  Auto-pipeline .emergent/emergent.yml (+1/-1, non-code)
  ↓
571d6d3f5                                  Auto-pipeline .emergent/emergent.yml (+1/-1, non-code)
  ↓
df6467cfd                                  COMMIT CONTENUTO FIX 543
                                           "auto-commit for 8a1cc320-d57f-429c-8d83-37442bfa5948"
                                           Emergent Pack 125 Agent, 2026-06-28 23:12:26 UTC
                                           3 file di scope, +646 / -3:
                                           - frontend/app/(tabs)/battle.tsx               +44/-3
                                           - backend/scripts/validate_fix_team_server_required_scope_ready.py  +231 (new)
                                           - docs/divine/543_FIX_TEAM_SERVER_REQUIRED_SCOPE_READY.md           +371 (new, con TRUTH_SYNC_PENDING)
  ↓
c56ede909                                  Auto-pipeline .emergent/emergent.yml (+1/-1, non-code)
  ↓
[truth-sync commit]                        Truth-sync di questo report
                                           (sostituisce i placeholder con gli SHA reali sopra).
                                           SHA visibile in `git log` post-commit come HEAD finale FIX 543.
```

### 2.ter) SHA finali FIX 543

| Etichetta | SHA |
|---|---|
| Baseline ufficiale (HOTFIX G) | `aabaf8e2ee1642ca067fe9a48406ccdfc95a0eab` |
| Auto-pipeline pre-commit (metadata) | `f334ead92`, `571d6d3f5` |
| **Commit contenuto FIX 543** | **`df6467cfd00c6a7a7632e48f4f739a07a5c1cdea`** |
| Auto-pipeline post-commit (metadata) | `c56ede909` |
| HEAD finale FIX 543 (truth-sync) | visibile in `git log` post-commit |

## 3) File modificati

```text
frontend/app/(tabs)/battle.tsx                                                  (modified, +44/-3)
backend/scripts/validate_fix_team_server_required_scope_ready.py                (new, ~210 righe)
docs/divine/543_FIX_TEAM_SERVER_REQUIRED_SCOPE_READY.md                         (this file)
```

File NON toccati (verifica content-side):
`backend/**`, `frontend/utils/api.ts`, `frontend/app/servers.tsx`,
`frontend/app/pre-battle-lobby.tsx`, `frontend/app/combat.tsx`,
`frontend/app/(tabs)/heroes.tsx`, asset, character bible,
`heroes_master.json`, DB migrations, reward/economy/battle formulas.

## 4) Root cause

`frontend/src/hooks/useServerScope.ts` espone uno stato iniziale:

```ts
const [state, setState] = useState<ServerScope>({
  selected_server_id: null,
  ...
  loading: true,
  refreshToken: 0,
  isReady: false,
});
```

La lettura di `v101_selected_server_id` da `AsyncStorage` avviene dentro
un `useEffect(() => { (async () => await refresh())(); }, [refresh])`
asincrono. Il primo render di `battle.tsx` aveva quindi
`selected_server_id = null` e `loading = true` e `isReady = false`.

Il vecchio codice di `battle.tsx`:

```ts
const { selected_server_id } = useServerScope();   // ← NIENTE loading/isReady
...
const loadData = async () => {
  if (!selected_server_id) {
    setRosterDiag({ error_code: 'SERVER_REQUIRED', ... });
    return;
  }
  ...
};
...
useFocusEffect(useCallback(() => { loadData(); }, [userHeroesVersion]));
...
if (!selected_server_id) return <View>{/* "Server richiesto" UI */}</View>;
```

Conseguenza: `loadData()` partiva al primo render (focus iniziale), trovava
`selected_server_id = null` perché `useServerScope` non aveva ancora letto
AsyncStorage, e impostava il blocker `SERVER_REQUIRED`. La UI mostrava
"Server richiesto" / "Nessun eroe disponibile / blocker/code:
SERVER_REQUIRED". Quando poi `useServerScope` finiva il refresh,
`loadData` NON veniva rieseguito perché le dipendenze di `useFocusEffect`
non includevano `selected_server_id` né lo `refreshToken` del hook.

## 5) Evidenza screenshot

Device QA report:

```text
FORMAZIONE SQUADRA
Nessun eroe disponibile
blocker/code: SERVER_REQUIRED
Nessun server selezionato (pre-QA gate.)
```

Pattern identico al messaggio generato in `loadData()` linea ex-152:

```ts
setRosterDiag({
  status: null,
  diagnostics: null,
  error_code: 'SERVER_REQUIRED',
  error_detail: 'Nessun server selezionato (pre-QA gate).',
});
```

con surface UI in `noHeroesBox` dentro `rosterPanel`.

## 6) Fix applicato

Tre cambi mirati, tutti dentro `frontend/app/(tabs)/battle.tsx`:

### 6.1) Destructuring esteso da `useServerScope`

```ts
// FIX 543 — Aspettiamo che useServerScope sia pronto prima di emettere
// SERVER_REQUIRED.
const {
  selected_server_id,
  loading: serverScopeLoading,
  isReady: serverScopeReady,
  refreshToken: serverScopeRefreshToken,
} = useServerScope();
```

### 6.2) Guard "scope-ready" in `loadData()` PRIMA del check
`!selected_server_id`

```ts
const loadData = async () => {
  try {
    // FIX 543 — Server scope readiness gate.
    if (serverScopeLoading || !serverScopeReady) {
      setLoading(true);
      return;
    }
    // Pre-QA Stabilization 115C — fail-closed se manca server_id.
    // Ora valutato SOLO dopo che useServerScope ha terminato la lettura.
    if (!selected_server_id) {
      setHeroes([]);
      ...
      setRosterDiag({ error_code: 'SERVER_REQUIRED', ... });
      setLoading(false);
      return;
    }
    ...
  }
};
```

### 6.3) Render gate "scope-ready" PRIMA del branch `if (!selected_server_id)`

```ts
// FIX 543 — Render gate: aspettiamo che useServerScope sia pronto prima
// di valutare `selected_server_id`.
if (serverScopeLoading || !serverScopeReady || loading) return (
  <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.container}>
    <ActivityIndicator size="large" color={COLORS.accent} />
  </LinearGradient>
);

// Pre-QA Stabilization 115C — stato server-required (no fallback account-wide).
// Ora valutato SOLO dopo che useServerScope ha terminato la lettura.
if (!selected_server_id) {
  return (
    <LinearGradient ...>
      ...
      <Text>Server richiesto</Text>
      ...
    </LinearGradient>
  );
}
```

### 6.4) `useFocusEffect` deps estese

```ts
useFocusEffect(
  useCallback(() => {
    loadData();
  }, [
    userHeroesVersion,
    selected_server_id,
    serverScopeLoading,
    serverScopeReady,
    serverScopeRefreshToken,
  ]),
);
```

Ogni transizione `loading=true → loading=false`, `isReady=false → true`,
`selected_server_id=null → "S1"` o cambio server scatena un re-run di
`loadData()`.

## 7) Come viene atteso `useServerScope`

```text
PRIMO RENDER:
  state = { selected_server_id: null, loading: true, isReady: false, ... }
  ↓
  battle.tsx render gate → ActivityIndicator
  loadData() (via useFocusEffect) → guard scope-ready → setLoading(true); return
  ↓ (useEffect interno di useServerScope esegue `refresh()`)
SECONDO RENDER:
  state = { selected_server_id: "S1" o null, loading: false, isReady: true, refreshToken: 1, ... }
  ↓
  useFocusEffect ri-trigger (deps cambiate)
  loadData() → guard scope-ready PASSA → branch SERVER_REQUIRED valutato
                                          su valore REALE di AsyncStorage.
  ↓
  se selected_server_id == "S1":  fetch /api/user/heroes?server_id=S1 + /api/team/get-formation
  se selected_server_id == null:  render branch "Server richiesto" → /servers
```

## 8) Come viene ricaricato il roster al cambio server

```text
Utente seleziona nuovo server in /servers
  ↓
AsyncStorage.setItem('v101_selected_server_id', ...)
  ↓
useServerScope ha già un AppState listener:
  AppState 'active' → refresh() → setState con nuovo id + bump refreshToken
  ↓ (oppure utente torna su BattleTab focus → useFocusEffect re-run)
useFocusEffect deps include serverScopeRefreshToken + selected_server_id
  → loadData() ri-eseguito
  → fetch /api/user/heroes?server_id=<nuovo> + /api/team/get-formation?server_id=<nuovo>
```

## 9) Endpoint roster finale

```text
GET /api/user/heroes?server_id=<selected_server_id>     ← owned roster
GET /api/team/get-formation?server_id=<selected_server_id>  ← saved team V1
GET /api/constellations                                  ← catalog (no scope)
GET /api/synergies/team                                  ← derived (no scope)
GET /api/synergies/team_v2                               ← derived V2 (no scope)
```

Nessun fallback a `/api/heroes` come owned roster (verificato da
validator). Nessun nuovo endpoint introdotto.

## 10) Validator result

```text
$ python backend/scripts/validate_fix_team_server_required_scope_ready.py
FIX 543 — VALIDATOR (team_server_required_scope_ready): PASS
  file: frontend/app/(tabs)/battle.tsx
  file modificati in scope (2):
    + backend/scripts/validate_fix_team_server_required_scope_ready.py
    + frontend/app/(tabs)/battle.tsx
rc=0
```

Verifiche statiche eseguite:

1. ✅ `loading: serverScopeLoading` destructured
2. ✅ `isReady: serverScopeReady` destructured
3. ✅ `refreshToken: serverScopeRefreshToken` destructured
4. ✅ Guard `if (serverScopeLoading || !serverScopeReady)` presente in `loadData()` e precede il setRosterDiag `SERVER_REQUIRED`
5. ✅ Render gate `if (serverScopeLoading || !serverScopeReady || loading) return ActivityIndicator` precede il branch `if (!selected_server_id)` del render
6. ✅ `useFocusEffect/useCallback` deps include `selected_server_id`, `serverScopeRefreshToken`, `serverScopeLoading`, `serverScopeReady`
7. ✅ Endpoint roster owned: `/api/user/heroes?server_id=${encodeURIComponent(selected_server_id)}`
8. ✅ Nessun riferimento ad `apiCall('/api/heroes'`
9. ✅ Nessun nuovo endpoint mutativo (`/api/psp/ensure`, `/api/psp/starter/claim`, `/api/battle/simulate` assenti dal file)
10. ✅ Scope drift: solo i 2 file consentiti modificati; nessun `EXPLICIT_FORBIDDEN` toccato

Invariant precedenti (re-run dopo il fix):

```text
validate_security_hotfix_a_battle_simulate_guard                  PASS rc=0
validate_security_hotfix_a_jwt_secret_preflight                   PASS rc=0
validate_hotfix_b_api_error_contract                              PASS rc=0
validate_hotfix_b_blocker_visibility                              PASS rc=0
validate_hotfix_c_server_select_fail_closed                       PASS rc=0
validate_hotfix_d_starter_roster_contract                         PASS rc=0
validate_hotfix_d_user_heroes_exposure                            PASS rc=0
validate_hotfix_e_teamformation_v1_contract                       PASS rc=0
validate_hotfix_e_frontend_payload                                PASS rc=0
validate_hotfix_e_snapshot_alignment                              PASS rc=0
validate_hotfix_f_lobby_consumes_teamformation_v1                 PASS rc=0
validate_hotfix_f_combat_preview_consumes_teamformation_v1        PASS rc=0
validate_hotfix_f_no_live_battle_or_reward_path                   PASS rc=0
validate_hotfix_g_frontend_lobby_to_combat_v1_payload             PASS rc=0
validate_hotfix_g_combat_requires_v1_preview                      PASS rc=0
validate_hotfix_g_no_live_battle_or_reward_path                   PASS rc=0
validate_hotfix_g_no_scope_drift                                  rc=1 (atteso: nuovi file fuori dal suo allow-list)
```

Backend health: HTTP 200, `{"status":"ok","game":"Divine Waifus","version":"1.0.0","bots":20}`.

## 11) DB writes = 0

Il fix è puramente lato componente React. Zero modifiche backend, zero
nuove query, zero scritture su MongoDB.

## 12) Endpoint mutativi chiamati = 0

```text
POST /api/team/save-formation     ← NON chiamato durante il test
                                     (pre-esistente in saveTeam(), invariato)
POST /api/psp/ensure              ← NON presente in battle.tsx
POST /api/psp/starter/claim       ← NON presente in battle.tsx
POST /api/battle/simulate         ← NON presente in battle.tsx
```

Il validator esegue solo lettura statica del file `.tsx` (regex + count
sostringhe + AST-light) e `git diff/ls-files`. Nessuna chiamata HTTP.

## 13) File fuori scope = 0

Diff working-tree (post-fix, pre-commit):

```text
M  frontend/app/(tabs)/battle.tsx                                          (allowed)
?? backend/scripts/validate_fix_team_server_required_scope_ready.py        (allowed)
?? docs/divine/543_FIX_TEAM_SERVER_REQUIRED_SCOPE_READY.md                  (allowed)
```

Verifica file critici intatti vs HEAD `aabaf8e2`:

```text
backend/battle_engine.py                          0 modifiche
backend/server.py                                 0 modifiche
backend/helpers/jwt_secret_preflight.py           0 modifiche
backend/helpers/team_formation_contract.py        0 modifiche
backend/helpers/real_player_snapshot.py           0 modifiche
backend/routes/v96_team_formation.py              0 modifiche
backend/routes/v130_lobby_launch_context.py       0 modifiche
backend/routes/v131_combat_preview.py             0 modifiche
frontend/utils/api.ts                             0 modifiche
frontend/app/servers.tsx                          0 modifiche
frontend/app/pre-battle-lobby.tsx                 0 modifiche
frontend/app/combat.tsx                           0 modifiche
frontend/app/(tabs)/heroes.tsx                    0 modifiche
```

## 14) Device QA = MANUAL_REQUIRED

Il fix risolve la root cause identificata, ma la conferma device-side
richiede:

1. avvio app su device,
2. login account test con server già selezionato in AsyncStorage,
3. cold-start navigando direttamente al tab Battaglia,
4. verifica che la UI passi da `ActivityIndicator` → roster popolato
   (NON `SERVER_REQUIRED`),
5. logout/cambio server → ritorno a Battaglia → verifica re-load.

### 14.bis) Esito device-side post-FIX 543 (riportato dall'utente)

```text
La schermata "FORMAZIONE SQUADRA" non mostra più SERVER_REQUIRED.
Gli eroi sono visibili e possono essere mossi nel team.
```

Questo conferma che il fix scope-ready guard chiude effettivamente la
race condition `useServerScope` → `loadData()`. Lo stato `Device QA`
resta comunque `MANUAL_REQUIRED` perché:

- non è stata eseguita una checklist QA completa (cambio server, logout,
  modalità offline, restart a freddo dopo update OTA);
- la verifica utente è osservazionale single-path, non un piano di
  validazione device-side strutturato.

## 15) Release ready = NO

Il fix è preview-only. Nessun cambio di contratto V1, nessun cambio di
endpoint, nessun cambio di reward/economy/progress, nessun cambio di
combat. Resta una sola superficie corretta (un componente client).

## 16) Secure / anti-hack safe = NO

Il fix è chirurgico sul client. Le invariant di sicurezza upstream
(`HOTFIX A` battle-simulate guard, JWT preflight) NON sono coinvolte e
restano attive (re-verificate sopra).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = FIX_TEAM_SERVER_REQUIRED_SCOPE_READY_FOR_REAUDIT
```
