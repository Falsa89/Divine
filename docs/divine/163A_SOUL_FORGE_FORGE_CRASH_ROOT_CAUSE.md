# 163A — Soul Forge Forge Crash: Root Cause

## Verdict
`TRACK_A_SOUL_FORGE_FORGE_CRASH_ROOT_CAUSE_IDENTIFIED`

## Sintomo riportato dall'utente
Dopo `PROJECT_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_FIX_COMPLETE`, mobile QA conferma:
- Soul Forge si apre, card visibili, filtri OK, pagina scorre, bottone `FORGE SOUL` raggiungibile.
- **Tuttavia premendo `FORGE SOUL` il gioco crasha.**

## Backend contract (audit)
Verificato manualmente:

- Endpoint: `POST /api/soul/forge` (auth-protected)
- File: `backend/routes/soul_forge.py:368-401`
- Request body: `{hero_ids: list[str]}`
- Response body: `{gained_essence: int, new_balance: int}`
- Safety guards: 400 se hero_ids vuoto, 404 se eroe non posseduto, 400 se eroe nel team attivo
- Reward formula: `int(SOUL_ESSENCE_VALUES[min(stars,5)] * (1 + level*0.02))` (immutata)
- Test curl: response confermata `{"gained_essence":10,"new_balance":10}` – 1:1 match al contract atteso dal frontend.

**Conclusione**: il backend è corretto. Il crash è frontend-only.

## Frontend crash candidates

### FC1 — setBalance(undefined) (PRIMARY)
Il pack EMERGENCY_RESTORE faceva:
```ts
setResult({ gained: r.gained_essence, newBalance: r.new_balance });
setBalance(r.new_balance);
```
Se per qualsiasi motivo `r.new_balance` è `undefined` (token scaduto → HTML response, 5xx, parse JSON fallisce silenziosamente, payload incompleto), `setBalance(undefined)` viene committato a state. Il render successivo dell'header fa `{balance.toLocaleString()}` → **TypeError: Cannot read properties of undefined (reading 'toLocaleString')**.

### FC2 — result.newBalance.toLocaleString() render
Nel resultBox:
```jsx
<Text style={s.resultBalance}>Bilancio: {result.newBalance.toLocaleString()}</Text>
```
Se `result.newBalance` è undefined → crash render.

### FC3 — deletion ottimistica heroes prima di validare risposta
```ts
setHeroes(prev => prev.filter(h => !selected.has(h.id)));
```
Se il backend ha restituito 200 ma con payload malformato, la UI rimuove gli eroi ma lo state non corrisponde alla realtà.

### FC4 — nessun errore visibile su API failure
Il catch attuale setta `setResult({gained: 0, newBalance: balance})` ma la conditional render `result.gained > 0` impedisce il display → utente non vede nulla, sembra crash silenzioso.

### FC5 — doppio submit
Nessun guard `if (forging) return;` in `confirmForge` — utente può tappare CONFERMA due volte.

## Fix strategy applicata (Track B, D)
1. `normalizeForgeResponse()` helper resiliente con alias multipli e mai-throw.
2. Snapshot `heroIdsSnapshot` PRIMA di qualsiasi setState.
3. Heroes rimossi SOLO dopo validazione `ok=true`.
4. Stati visibili: `forgeError` (rosso) e `postSuccessWarn` (ambra).
5. Guards double-submit in `requestForge` e `confirmForge`.
6. `refreshUser()` wrappato in try/catch (soft warning, no crash).
7. Render: `Number.isFinite(balance) ? balance : 0`, `Number(result.gained) || 0`.
8. Modal `FORGE` button disabilitato + dim mentre `forging===true`, label "… IN CORSO".

## Vincoli rispettati
- ❌ Zero modifiche reward formula
- ❌ Zero modifiche backend
- ❌ Zero DB writes
- ❌ Zero modifiche gacha/shop/IAP/battle_engine/.env
- ❌ Zero validator weakening
- ❌ Zero fake PASS

## File MD5
- `frontend/app/soul-forge.tsx`: `ba8f802d10cc774e65e8c552a1482099` → `88a39590454ecc1c5f16e34e09d90b63`
- `backend/battle_engine.py`: `151ca35ad3bc35f0a6209cb3744ed440` (invariant)
- `backend/.env`: `ff60bbb79efa329b71aa8ed351ea89b3` (invariant)
