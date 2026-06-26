# 537 — HOTFIX B — API ERROR CONTRACT + BLOCKER VISIBILITY

> Patch P0 di observability frontend. Read-only, zero DB writes, zero endpoint
> mutativi. Risolve la regressione 115C in cui `apiCall` lanciava `new Error`
> perdendo status HTTP, body strutturato e header diagnostici, trasformando
> blocker server-side in "roster vuoto" silenzioso.

| Campo                  | Valore                                                                 |
| ---------------------- | ---------------------------------------------------------------------- |
| Tipo                   | HOTFIX (Security/Observability)                                        |
| Ambito                 | Frontend (`utils/api.ts` + 2 tab) + 3 validator Python                  |
| DB writes              | NO (zero)                                                              |
| Endpoint mutativi      | NO (POST `/api/psp/ensure`, `/api/psp/starter/claim`, `/api/team/save-formation` NON chiamati né modificati) |
| Generated at (UTC)     | `2026-06-26T14:41:26Z`                                                 |
| Baseline (Hotfix A)    | `d0461f806b7cd55d375ecbc95a703bc4c66a7b48`                             |
| Commit SHA (HOTFIX B)  | `99d9cd38d6e8748d3103e964a044db15779381e7`                             |
| Classificazione finale | `PASS` (3/3 validator HOTFIX B verde, zero scope drift, py_compile OK) |

---

## 1) Obiettivo

`apiCall()` deve **preservare** lo status HTTP, il body, `detail`, `code`, e gli
header diagnostici (`X-Blocker`, `X-Roster-Count`, `X-PSP-Lookup-Mode`,
`X-Server-Scope`). Deve essere possibile **leggere i metadata anche su 200 OK**
(es. roster legittimamente vuoto server-scoped). `heroes.tsx` e `battle.tsx`
devono **mostrare** blocker/code/server scope/roster count invece di mascherare
qualunque problema come "lista vuota generica".

## 2) Problema (Audit 4 P0)

In `frontend/utils/api.ts` (versione 115C), `apiCall` rilanciava qualunque
risposta non-ok come:

```ts
throw new Error(error.detail || `HTTP ${response.status}`);
```

Conseguenze:

- lo `status` HTTP si perdeva (consumer leggeva solo `error.message`);
- `data` strutturato (`detail` come oggetto con `blocker`/`code`/`message`) si
  appiattiva a stringa o si perdeva del tutto;
- gli **header di risposta** (compresi `X-Blocker`, `X-Roster-Count`,
  `X-PSP-Lookup-Mode`, `X-Server-Scope` emessi dal backend) non venivano mai
  esposti alla UI;
- gli empty state di `heroes.tsx` e del roster di `battle.tsx` catturavano
  l'errore con `catch (e) {}` silenzioso, mostrando "Nessun eroe trovato" /
  "Nessun eroe disponibile" anche su 403 / 423 / 404 / 5xx.

## 3) Scope autorizzato (esatto)

```text
frontend/utils/api.ts
frontend/app/(tabs)/battle.tsx
frontend/app/(tabs)/heroes.tsx
backend/scripts/validate_hotfix_b_api_error_contract.py
backend/scripts/validate_hotfix_b_blocker_visibility.py
backend/scripts/validate_hotfix_b_no_scope_drift.py
docs/divine/537_HOTFIX_B_API_ERROR_CONTRACT*.md
```

**Verificato** dal Validator 3 (`no_scope_drift`) — output: 6 file in scope,
zero file fuori scope (eccezione `backend/scripts/reports/*.json`: auto-generati
dai validator Pack, esplicitamente ignorati).

## 4) Non in scope (intoccato per design)

- `backend/server.py`, `backend/battle_engine.py`
- `backend/routes/v96_team_formation.py`, `backend/routes/v96_auth.py`
- `backend/routes/v130_lobby_launch_context.py`, `backend/routes/v131_combat_preview.py`
- `backend/helpers/jwt_secret_preflight.py` (Hotfix A territory)
- `frontend/app/(tabs)/servers.tsx`, `frontend/app/pre-battle-lobby.tsx`
- Tutte le superfici gacha/shop/VIP/Battle Pass/mail
- Reward/economy formulas, Character Bible, heroes_master, assets, final_numbers
- Bug fuori scope `heroes.tsx:230 filtered.map(...)` — **non corretto** in questa patch.

## 5) Modifica 1/3 — `frontend/utils/api.ts`

- Introduce classe `ApiError extends Error` che preserva:
  - `status` (numero HTTP intero),
  - `data` (body parsato come JSON, fallback string, fallback null),
  - `detail` (stringa estratta da `data.detail`/`data.detail.message`/
    `data.detail.blocker`/`data.detail.code`),
  - `code` (estratto da `data.detail.code` o `data.detail.blocker` o
    `data.code` o `data.blocker`),
  - `headers` (mappa lowercased degli header di risposta),
  - `diagnostics` (oggetto tipizzato con `blocker`, `roster_count`,
    `psp_lookup_mode`, `server_scope`, `raw`).
- Estrazione case-insensitive degli header diagnostici:
  `x-blocker`, `x-roster-count`, `x-psp-lookup-mode`, `x-server-scope`.
- `apiCall` continua ad esportare la stessa firma; **su risposta non-ok lancia
  `ApiError`** invece di `Error` plain.
- Nuovo export `apiCallWithMeta<T>` ritorna
  `{ data, status, headers, diagnostics }` anche su 200 OK.
- Token/secret: nessun log, comportamento outbound (Authorization, Content-Type)
  invariato.

## 6) Modifica 2/3 — `frontend/app/(tabs)/heroes.tsx`

- Import aggiornato a `apiCallWithMeta, ApiError, ApiDiagnostics`.
- Nuovo state `rosterDiag = { status, diagnostics, error_code, error_detail }`.
- `load()` ora usa `apiCallWithMeta` per `/api/user/heroes?server_id=…` e
  popola `rosterDiag` su 200 OK con `meta.status` + `meta.diagnostics`.
- `catch` non più silenzioso: `e instanceof ApiError ⇒ rosterDiag = {status,
  diagnostics, code, detail}`; fallback `NETWORK_ERROR` per non-ApiError.
- Empty state UI ora mostra (quando presenti): `HTTP <status>`, `blocker/code`,
  testo `detail`, `X-Blocker`, `server_scope`, `psp_lookup_mode`, `roster_count`.

## 7) Modifica 3/3 — `frontend/app/(tabs)/battle.tsx`

- Import aggiornato a `apiCallWithMeta, ApiError, ApiDiagnostics`.
- Stesso pattern `rosterDiag` aggiunto.
- `loadData()` usa `apiCallWithMeta` per il roster reader principale
  (`/api/user/heroes?server_id=…`); `team` e `constellations` mantengono il
  fallback locale esistente (fuori scope).
- Branch "Nessun eroe disponibile" sostituito da wrapper con `diagBox` che
  mostra: HTTP status, blocker/code, detail, X-Blocker, server_scope,
  psp_lookup_mode, roster_count.
- L'handler già esistente di `saveTeam` (che leggeva `e?.status` /
  `e?.data?.detail`) ora riceve **per la prima volta** valori reali: l'oggetto
  `ApiError` lo soddisfa nativamente senza alcuna modifica al codice di save.

## 8) Validator 1/3 — `validate_hotfix_b_api_error_contract.py`

Statico, no runtime, no DB. Verifica in `frontend/utils/api.ts`:

- `export class ApiError`
- `class ApiError extends Error`
- preservazione di `status`, `data`, `detail`, `code`, `headers`, `diagnostics`
- `export async function apiCallWithMeta`
- `export async function apiCall` (backward-compat)
- `throw new ApiError` (apiCall non lancia plain `Error`)
- estrazione header `x-blocker`, `x-roster-count`, `x-psp-lookup-mode`, `x-server-scope`
- guardia di regressione: assenza di `throw new Error(`

Risultato: **PASS** (15 check superati).

## 9) Validator 2/3 — `validate_hotfix_b_blocker_visibility.py`

Verifica statica, per ognuno dei due tab (`heroes.tsx`, `battle.tsx`):

- import di `apiCallWithMeta`, `ApiError`, `ApiDiagnostics`;
- uso di `apiCallWithMeta` nel loader;
- presenza di state `rosterDiag` + writer `setRosterDiag`;
- catch tipato `instanceof ApiError`;
- UI menziona `blocker`, `server_scope`, `psp_lookup_mode`, `roster_count`, `HTTP `;
- guardia anti-`catch(e){}` silenzioso.

Risultato: **PASS** per entrambi i file.

## 10) Validator 3/3 — `validate_hotfix_b_no_scope_drift.py`

Confronta `git diff --name-only HEAD` + `git ls-files --others
--exclude-standard` con la lista esatta di scope. File auto-generati
(`backend/scripts/reports/*.json`) esclusi esplicitamente perché vengono
riemessi dai validator Pack al loro run e non rappresentano source change.

Risultato: **PASS** — 6 file in scope, zero file fuori scope.

## 11) Suite Python `py_compile`

Eseguito su tutti e tre i validator nuovi:

```text
python -m py_compile backend/scripts/validate_hotfix_b_api_error_contract.py \
                    backend/scripts/validate_hotfix_b_blocker_visibility.py \
                    backend/scripts/validate_hotfix_b_no_scope_drift.py
# PYCOMPILE_OK (exit 0)
```

## 12) Lint TypeScript

- `frontend/utils/api.ts`: 0 errori, 3 warning su `_e` (underscore-prefixed
  intentional, pre-esistenti come convenzione del repo).
- `frontend/app/(tabs)/heroes.tsx`: 0 errori, 3 warning pre-esistenti
  (`useServerScope` default, `width` non usato, `useCallback` deps).
- `frontend/app/(tabs)/battle.tsx`: 0 errori, 12 warning **tutti
  pre-esistenti** (Dimensions/ROW_YS/refreshUser/V2Effect/_logE/_se non usati,
  hooks deps, array type). Nessun nuovo warning introdotto.

## 13) Backward compatibility

- Firma di `apiCall(endpoint, options)` invariata.
- Return shape su 2xx invariato (la `data` parsata, identica a prima).
- Consumer esistenti che facevano `try/catch` ricevono ora un `ApiError` che
  estende `Error` (instanceof Error == true ⇒ nessuna rottura).
- I consumer che leggevano `error.message` continuano a riceverlo (`detail` o
  `HTTP <status>` come fallback).

## 14) Constraint di sicurezza rispettati

- Zero DB writes; zero endpoint mutativi chiamati o modificati.
- Nessuna chiamata a `POST /api/psp/ensure`, `POST /api/psp/starter/claim`,
  `POST /api/team/save-formation`.
- Hotfix A (battle simulate fail-closed + JWT preflight): **non toccato**.
- `backend/battle_engine.py`: **non toccato**.
- JWT preflight: **non toccato**.
- Team formation contract: **non toccato**.
- Starter claim, gacha, shop, VIP, Battle Pass, mail: **non toccati**.
- Reward/economy formulas, Character Bible, heroes_master, assets,
  final_numbers: **non toccati**.

## 15) Bug fuori scope esplicitamente lasciato

`heroes.tsx` linea ~230 — pattern `filtered.map(...)` segnalato in handoff
come possibile null/undefined. **Non corretto** in questa patch per rispetto
dello scope. Da affrontare in patch dedicata previo OK utente.

## 16) Effetti collaterali positivi non richiesti

L'handler di `saveTeam` in `battle.tsx` (linee ~370-410) leggeva già
`e?.status`, `e?.data?.detail`, `detail?.blocker`. Prima di HOTFIX B questi
campi erano sempre `undefined` perché `apiCall` lanciava plain `Error`. Ora
l'oggetto `ApiError` soddisfa nativamente quel contratto: gli Alert specifici
per `QA_TEAM_SAVE_DISABLED`, `QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED`,
`PLAYER_SERVER_PROFILE_REQUIRED`, `OWNERSHIP_VALIDATION_FAILED` diventano
finalmente raggiungibili. Nessun codice modificato in quel branch.

## 17) Suite Pack 127–133

Eseguita per memoria storica: 64/73 PASS, 9/73 FAIL. **Le 9 FAIL sono tutte
riconducibili a HOTFIX A** (battle_engine.py, jwt_secret_preflight.py,
server.py, v96_auth.py, v130_lobby_launch_context.py,
v131_combat_preview.py). **Nessuna FAIL riferisce file di HOTFIX B**. Drift
atteso dallo snapshot Pack 132/133 vs Hotfix A; in attesa di re-audit Game
Master/Codex Web.

## 18) Classificazione finale

**`PASS`** — non `RELEASE_READY`, non `DEVICE_QA_PASS`, non `SECURE`.
La patch è observability-only, statica, frontend-only (più 3 validator). Il
re-audit Game Master/Codex Web resta dovuto per Hotfix A + Hotfix B
congiuntamente.

## 19) Truth-sync

- Baseline (Hotfix A): `d0461f806b7cd55d375ecbc95a703bc4c66a7b48`
- Commit HOTFIX B (contenuto patch): `99d9cd38d6e8748d3103e964a044db15779381e7`
- Truth-sync commit (sostituzione placeholder in questo report):
  vedi `git log` posteriore (SHA emesso dal commit di chiusura).
- Indice `docs/divine/` aggiornabile al prossimo passaggio di documentazione
  (fuori scope di questa patch).

## 20) Comandi di replay esatti

```bash
# 1) Validator 1/3 — API Error Contract
python /app/backend/scripts/validate_hotfix_b_api_error_contract.py

# 2) Validator 2/3 — Blocker Visibility
python /app/backend/scripts/validate_hotfix_b_blocker_visibility.py

# 3) Validator 3/3 — No Scope Drift
python /app/backend/scripts/validate_hotfix_b_no_scope_drift.py

# 4) py_compile guard
python -m py_compile \
    /app/backend/scripts/validate_hotfix_b_api_error_contract.py \
    /app/backend/scripts/validate_hotfix_b_blocker_visibility.py \
    /app/backend/scripts/validate_hotfix_b_no_scope_drift.py
```

Tutti e quattro devono terminare con exit code `0`.
