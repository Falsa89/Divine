# 162A — Soul Forge Emergency Restore: Root Cause

## Verdict
`TRACK_A_SOUL_FORGE_BLANK_SCREEN_ROOT_CAUSE_IDENTIFIED`

## Sintomo
Mobile QA dell'utente, dopo `PROJECT_SOUL_FORGE_ECONOMY_MERGE_AND_EXCLUSIVE_RETIREMENT_PACK`: aprendo `/soul-forge` non si vede più nulla — niente card eroi, niente pannelli, niente UI utile. Solo l'header risulta visibile.

## Root cause primaria (RC1)
Il pack precedente (SF_MERGE Track B — mobile reachability) ha convertito il layout del body da split orizzontale a stack verticale:

```ts
body: { flex: 1, flexDirection: 'column', padding: 6, gap: 6 }
```

Ma i due figli del body sono stati lasciati **senza `flex` né height esplicita**:

```ts
gridPanel: { gap: 4 },          // « no flex »
forgePanel: { width: '100%' },  // « no flex »
```

Conseguenze:

- **`gridPanel`** collassa all'altezza intrinseca del solo `gridHeader` (~14 px).
  All'interno, **`gridScroll: { flex: 1 }`** — una `ScrollView` con `flex: 1` dentro un parent non-bounded — viene renderizzata a **height 0**. Le card eroi non appaiono mai.
- **`forgePanel`** non ha flex, ha solo `width: '100%'`. Il suo `LinearGradient` interno (`forgePanelInner: { flex: 1 }`) richiede un parent bounded che non esiste → collassa.

## Root cause secondaria (RC2)
Riga 458 dell'ex `soul-forge.tsx`:

```jsx
<Text key={starKey} style={s.modalBreakLineV2}>
  \u2022 {selectionBreakdown[Number(starKey)]} eroi {starKey}\u2605
  ...
</Text>
```

In JSX il testo tra `>` e `<` è letterale: `\u2022` e `\u2605` venivano renderizzati come stringhe grezze di 6 caratteri invece che come bullet (•) e stella (★). Severità: cosmetica nel modal — non causa lo schermo vuoto, ma rovina la breakdown di conferma.

## Fix strategy (high level)
1. Sostituire il body broken con una **singola `ScrollView` esterna** che avvolge tutto il contenuto (mobile-first one-page-scroll).
2. Rimuovere l'inner `gridScroll` (la `ScrollView` esterna gestisce lo scroll).
3. Rimuovere `flex: 1` da `forgePanelInner` (size to content).
4. Aggiungere stati fail-safe: loading + error + empty (lo screen NON deve mai essere vuoto).
5. Aggiungere `KeyboardAvoidingView` + `ScrollView` interna al modal di conferma, e safe-area insets.
6. Sostituire `\u2022` e `\u2605` con `{'\u2022'}` e `{'\u2605'}` nel modal.

## File diff
- `frontend/app/soul-forge.tsx`: md5 `d2300bbe5171f62ac8f9fd54e8711d50` → `ba8f802d10cc774e65e8c552a1482099`
- `backend/battle_engine.py`: UNCHANGED (MD5 invariante rispettato)
- `backend/.env`: UNCHANGED (MD5 invariante rispettato)
- Backend routes: UNCHANGED
- DB writes: 0
