# 538 — HOTFIX C — SERVER SELECT FAIL-CLOSED PSP / STARTER / ROSTER VISIBILITY

> Chiude il P0 confermato dagli audit: server selection poteva entrare in
> Home anche se PSP `ensure` o starter `claim` fallivano, lasciando il roster
> operativo vuoto e Device QA in stato falso. Ora il flow è **fail-closed**:
> persistenza di `v101_selected_server_id` e navigazione a Home **solo** dopo
> ensure + starter (idempotency-aware) + roster verify tutti verdi.

## 1) Verdict

**`HOTFIX_C_SERVER_SELECT_FAIL_CLOSED_READY_FOR_REAUDIT`**

- Device QA = `MANUAL_REQUIRED`
- Release ready = `NO`
- Secure / anti-hack safe = `NO`

## 2) HEAD iniziale

```text
d3faf78622a4108894d29df487c267d937a73edc
```

(coincide con la chiusura HOTFIX B truth-sync `b1ee3386c` + auto-commit di
pipeline `.emergent/emergent.yml`, non-code).

## 3) HEAD finale

- Commit HOTFIX C (contenuto patch): `3b56fff1516ea1e168a97a57be2648303346e104`
- Auto-pipeline post-HOTFIX C: `0c2d0944750c4968c65986e67995eb53756014a3`
  (`.emergent/emergent.yml` bump non-code)
- Truth-sync di questo report: SHA emesso dal commit di chiusura (vedi
  `git log` posteriore).

## 4) Files changed

```text
frontend/app/servers.tsx                                              (modified)
backend/scripts/validate_hotfix_c_server_select_fail_closed.py        (new)
backend/scripts/validate_hotfix_c_no_scope_drift.py                   (new)
docs/divine/538_HOTFIX_C_SERVER_SELECT_FAIL_CLOSED.md                 (this file, new)
```

`frontend/utils/api.ts`: **NON toccato** (preferenza esplicita dal prompt).

## 5) Diff summary

```text
frontend/app/servers.tsx   +396 −89   (rewrite di onEnter, +diag modal, +DiagError type)
```

Tutti gli altri file di scope sono nuovi (zero linee modificate altrove).

## 6) Server select — vecchio comportamento (115C)

```text
seleziona server
→ AsyncStorage.setItem('v101_selected_server_id') (immediato, pre-ensure)
→ AsyncStorage.setItem('v102_selected_server_name')
→ AsyncStorage.setItem('v102_selected_server_has_character')
→ fetch POST /api/psp/ensure (best-effort, .catch(() => { tolerated }))
→ fetch POST /api/psp/starter/claim (best-effort, .catch(() => { tolerated }))
→ router.replace('/(tabs)/home')      ← ESEGUITO ANCHE SU FAILURE
```

Conseguenze: l'utente entrava in Home con `v101_selected_server_id` salvato
ma con roster vuoto e Team/Formazione vuoti su quel server. Device QA falsa.

## 7) Server select — nuovo comportamento (HOTFIX C, fail-closed)

```text
seleziona server
→ Step 1: getAuthTokenCompat()
    se token mancante → DiagError(no_auth_token, NO_AUTH_TOKEN_SERVER_SELECT_BLOCKED)
                         resta su servers.tsx
→ Step 2: apiCallWithMeta POST /api/psp/ensure?server_id=…
    se ApiError o data.v110_psp_ensure !== true → DiagError(psp_ensure, <blocker>)
                         resta su servers.tsx
→ Step 3: apiCallWithMeta POST /api/psp/starter/claim?server_id=…
    se ApiError o data.v110_starter_claim !== true → DiagError(starter_claim, <blocker>)
    success: sia created:true sia already_claimed:true sono idempotency-valid
→ Step 4: apiCallWithMeta GET /api/user/heroes?server_id=…
    se ApiError → DiagError(roster_verify, <code>)
    se X-Blocker presente o X-Roster-Count===0 o heroes.length===0
                     → DiagError(roster_verify, ROSTER_EMPTY_AFTER_SERVER_PREP)
→ Step 5: PASS path
    AsyncStorage.setItem('v101_selected_server_id', s.server_id)
    AsyncStorage.setItem('v102_selected_server_name', s.server_name)
    AsyncStorage.setItem('v102_selected_server_has_character', …)
    router.replace('/(tabs)/home')
```

## 8) PSP ensure handling — evidence

- Endpoint reale: `POST /api/psp/ensure?server_id=<sid>` (backend `server.py`
  linee 273-345 — letto in read-only).
- Success contract dal backend (immutato): `v110_psp_ensure === true` +
  `created: true|false` + `already_existed: true|false` + emette
  `X-PSP-Ensure-Mode: fresh_start_created|already_exists_no_write`.
- HOTFIX C lato client: chiamata via `apiCallWithMeta`, ApiError catturato
  esplicitamente, qualsiasi fallimento popola `diagError` con `phase: 'psp_ensure'`,
  `code` da `eData.blocker` o fallback `PSP_ENSURE_FAILED`, `status` HTTP
  reale, `detail` da `eData.hint || eData.detail`.

## 9) Starter claim handling — evidence

- Endpoint reale: `POST /api/psp/starter/claim?server_id=<sid>` (backend
  `server.py` linee 368-526 — letto in read-only).
- Idempotency contract reale dal backend:
  - first-time: HTTP 200, `v110_starter_claim:true, created:true, already_claimed:false`,
    header `X-Starter-Claim-Mode: starter_claimed_first_time`;
  - già reclamato: HTTP 200, `v110_starter_claim:true, created:false,
    already_claimed:true`, header `X-Starter-Claim-Mode: already_claimed_no_write`.
  - **Entrambi** sono trattati come success path da HOTFIX C
    (`if (!cData.v110_starter_claim)` blocca solo quando il flag è falso).
- Codici di blocco veri esistenti: `PLAYER_SERVER_PROFILE_REQUIRED`,
  `STARTER_ROSTER_HIGH_RARITY`, `STARTER_ROSTER_NOT_OFFICIAL`,
  `STARTER_ROSTER_NOT_OBTAINABLE`, `STARTER_ROSTER_NOT_CATALOG_VISIBLE`,
  `STARTER_ROSTER_DEACTIVATED`, `STARTER_ROSTER_PREMIUM_FORBIDDEN`,
  `SERVER_ID_REQUIRED`. **Nessun codice idempotente è stato inventato**:
  vengono propagati così come emessi dal backend.

## 10) Roster verification — evidence

- Endpoint: `GET /api/user/heroes?server_id=<sid>` invocato via
  `apiCallWithMeta` (HOTFIX B) per leggere status + headers + body.
- Roster considerato OK se: `heroes.length > 0` AND `roster_count !== 0`
  AND **nessun** `X-Blocker` presente.
- Roster vuoto produce `DiagError` con `code = X-Blocker || 'ROSTER_EMPTY_AFTER_SERVER_PREP'`,
  `detail` discriminato tra "Roster iniziale non creato" e "Roster bloccato
  da diagnostico server".

## 11) Diagnostics UI — evidence

Card diagnostica modale (`diagStyles.overlay` in `servers.tsx`) mostra:

```text
[Title]    Server non pronto
[Codice]   <code/blocker>
[Fase]     no_auth_token|psp_ensure|starter_claim|roster_verify|network
[HTTP]     <status>            (se presente)
[Server]   <server_id>
[Roster count]   <diagnostics.roster_count>   (se presente)
[PSP lookup]     <diagnostics.psp_lookup_mode> (se presente)
[Scope]          <diagnostics.server_scope>    (se presente)
[X-Blocker]      <diagnostics.blocker>          (se presente)
[Dettaglio]      <detail/message>               (multilinea)

[Cambia server]   [Riprova]
```

- **Riprova**: user-triggered, riavvia il flow per lo **stesso** server. No retry automatici, no `setInterval/setTimeout` su `onEnter` (verificato dal validator 1).
- **Cambia server**: chiude la card e torna alla lista.

## 12) `selected_server_id` persistence — evidence

- Pre-HOTFIX C: `AsyncStorage.setItem('v101_selected_server_id', …)` veniva
  invocato **all'apertura** di `onEnter`, prima di ensure/claim.
- Post-HOTFIX C: la persistenza è confinata al blocco `Step 5: PASS`,
  raggiungibile **solo** dopo:
  1. `token` presente,
  2. `v110_psp_ensure === true`,
  3. `v110_starter_claim === true` (idempotent-valid),
  4. `heroes.length > 0` AND nessun `X-Blocker` AND `roster_count !== 0`.
- Marker locali secondari (`pack86_psp_ensure_last_mode`,
  `pack87_starter_claim_last_mode`, `pack87_starter_user_hero_ids`) sono
  scritti **dopo** il rispettivo step verde, mai prima.
- Compatibility note: il consumer di `v101_selected_server_id` (es.
  `useServerScope`) non vede regressioni di shape — la chiave e il valore
  sono identici, cambia solo il **timing** (post-success).

## 13) ApiError / apiCallWithMeta usage — evidence

- Import canonico: `import { apiCallWithMeta, ApiError, ApiDiagnostics } from '../utils/api';`
- 3 chiamate `apiCallWithMeta<any>(…)` (PSP ensure, starter claim, roster GET).
- Helper `apiErrorToDiag(e, phase, fallbackCode, s)` discrimina
  `e instanceof ApiError` (riusa `e.code`, `e.status`, `e.detail`,
  `e.diagnostics`) da fallback `network`.
- Nessun `catch (e) {}` silenzioso reintrodotto (verificato da V1 con
  regex `/catch\s*\(\s*\)\s*\{\s*\}/` + variazioni `.catch(() => { tolerated })`).

## 14) Validators results

```text
backend/scripts/validate_hotfix_c_server_select_fail_closed.py   PASS  (rc=0)
backend/scripts/validate_hotfix_c_no_scope_drift.py              PASS  (rc=0)
```

Inoltre, **HOTFIX A e B non sono stati indeboliti** (verificato in-process):

```text
validate_security_hotfix_a_battle_simulate_guard.py   PASS  (rc=0)
validate_security_hotfix_a_jwt_secret_preflight.py    PASS  (rc=0)
validate_hotfix_b_api_error_contract.py               PASS  (rc=0)
validate_hotfix_b_blocker_visibility.py               PASS  (rc=0)
```

## 15) Smoke results

- `python -m py_compile backend/scripts/validate_hotfix_c_*.py`:**OK** (exit 0).
- Frontend lint (`eslint frontend/app/servers.tsx`): **0 errori**, 7 warning
  **tutti pre-esistenti** (Constants unused, import-in-body, `_e` underscore).
  Nessun nuovo warning introdotto da HOTFIX C oltre i 4 `_e` underscore-prefix
  (intentional, convention del repo).
- Endpoint mutativi **NON** chiamati durante validator/smoke (validator V1 è
  100% statico: parsing del sorgente con `re`, zero `requests`/`fetch`).
- DB writes durante test: **0**.

## 16) Scope guard confirmation

`validate_hotfix_c_no_scope_drift.py` ha rilevato 3 file in scope:

```text
+ backend/scripts/validate_hotfix_c_no_scope_drift.py
+ backend/scripts/validate_hotfix_c_server_select_fail_closed.py
+ frontend/app/servers.tsx
```

(il report 538 .md verrà aggiunto al commit). EXPLICIT_FORBIDDEN list nel
validator copre: `backend/battle_engine.py`, `backend/helpers/jwt_secret_preflight.py`,
`backend/server.py`, `backend/routes/v96_auth.py`,
`backend/routes/v96_team_formation.py`,
`backend/routes/v130_lobby_launch_context.py`,
`backend/routes/v131_combat_preview.py`, `frontend/utils/api.ts`.
Nessuno di questi è apparso nel diff.

## 17) DB writes durante test

**0** (zero). Tutto l'audit è statico. Nessuna connessione MongoDB aperta dal
validator. La unica scrittura runtime è la `AsyncStorage` locale del client
(non DB) ed è confinata al PASS path.

## 18) Endpoint mutativi eseguiti durante test

**0**. Lista degli endpoint mutativi non chiamati dai validator:

```text
POST /api/psp/ensure              ← non chiamato dal validator
POST /api/psp/starter/claim       ← non chiamato dal validator
POST /api/team/save-formation     ← non chiamato (mai)
POST /api/battle/simulate         ← non chiamato (mai)
```

Queste POST esistono nel codice app come user-triggered (HOTFIX C non aggiunge
nuovi endpoint, conserva i due esistenti e li rende **decisive** invece di
best-effort). HOTFIX C **non introduce alcun nuovo endpoint mutativo**.

## 19) Remaining P0 / P1 / P2

### P0 ancora aperti dopo HOTFIX C

- Re-audit Game Master / Codex Web congiunto Hotfix A + B + C (atteso).
- Suite Pack 127-133 con drift atteso: 13 FAIL previsti
  (= 11 da Hotfix A+B documentati in 537 + 2 nuovi da HOTFIX C su
  `frontend/app/servers.tsx` verso `pack_130_frontend_lobby_integration_safe`
  e `pack_131_frontend_preview_integration_safe` — drift di snapshot, NON
  regressioni semantiche).

### P1

- Promozione dell'anchor Pack 128–133 a includere Hotfix A+B+C come
  baseline aggiornato (decisione Game Master).
- Verifica device-side che il diagnostic modal sia tappabile con tab bar
  visibile (manual QA).
- Bug fuori scope `heroes.tsx:230 filtered.map(...)` (handoff): **non
  affrontato** in HOTFIX C, intoccato.

### P2

- Localizzazione testi modale (oggi solo italiano).
- Telemetria opzionale dell'esito phase-by-phase (oggi solo
  `AsyncStorage` markers locali per stato onboarding).

## 20) Next recommended step

1. Commit HOTFIX C (auto-pipeline o manuale) e truth-sync di questo report:
   commit contenuto = `3b56fff1516ea1e168a97a57be2648303346e104`,
   baseline HOTFIX B = `b1ee3386c085eed2163c8d62ad623f7f34dbc76c`.
2. Game Master + Codex Web re-audit Hotfix A + B + C.
3. Se promosso, fork dedicato per affrontare il bug fuori scope
   `heroes.tsx filtered.map(...)` (HOTFIX D candidato — read-only safety
   come Hotfix A/B/C).

---

```text
Device QA = MANUAL_REQUIRED
Release ready = NO
Secure / anti-hack safe = NO
Verdict = HOTFIX_C_SERVER_SELECT_FAIL_CLOSED_READY_FOR_REAUDIT
```
