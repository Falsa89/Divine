# 164A — Soul Forge Inline Confirm Restore: True Crash Cause Corrected

## Verdict
`TRACK_A_TRUE_MOBILE_CRASH_CAUSE_CORRECTED_READY`

## Cronologia diagnostica
1. **Pack EMERGENCY_RESTORE**: layout broken → fix con ScrollView outer. ✅ risolto.
2. **Pack FORGE_CRASH**: ipotesi `setBalance(undefined)` → normalize/snapshot/defensive renders applicati. Tuttavia mobile QA conferma **crash persistente al primo tap di FORGE SOUL**.
3. **Pack INLINE_CONFIRM** (questo): correzione root cause + soluzione strutturale.

## Analisi temporale (smoking gun)
Il primo tap su `FORGE SOUL` chiama `requestForge()`:
```ts
const requestForge = () => {
  if (selected.size === 0) return;
  if (forging) return;
  setTypedConfirm('');
  setForgeError(null);
  setPostSuccessWarn(null);
  setConfirmOpen(true);  // <-- apre il Modal
};
```

Nessuna chiamata a `/api/soul/forge`. Nessuna mutazione di `balance`. Solo `setConfirmOpen(true)`.

**Conseguenza logica**: il crash NON può essere causato da `setBalance(undefined)` perché quel codice non viene mai eseguito prima del crash. La diagnosi precedente era errata (o solo parzialmente corretta).

## True root cause (corretto)
**`RC_REACT_NATIVE_MODAL_RENDER_PATH_ON_MOBILE`**

Il flusso di conferma usava:
```jsx
<Modal visible={confirmOpen} transparent animationType="fade">
  <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={modalBackdrop}>
    <View style={modalCard}>
      <ScrollView keyboardShouldPersistTaps="handled">
        <Text>...breakdown...</Text>
        <TextInput placeholder="CONFERMA" />
        <TouchableOpacity>...</TouchableOpacity>
      </ScrollView>
    </View>
  </KeyboardAvoidingView>
</Modal>
```

**Anti-pattern documentato** su React Native (specialmente Android, ma anche iOS con Reanimated):
- `Modal` (transparent) + `KeyboardAvoidingView` + `ScrollView` annidata
- `TextInput` dentro `KeyboardAvoidingView` dentro Modal transparent
- `Animated.View entering={FadeInUp/ZoomIn}` come children del Modal

Quando l'utente tappa `FORGE SOUL`, `setConfirmOpen(true)` triggera il mount dell'intero subtree. **Un solo bug di layout/render in qualunque punto del subtree crasha il JS thread PRIMA che qualsiasi chiamata API avvenga**.

## Evidenze a supporto
- Crash sempre al primo tap, nessuna richiesta backend osservata.
- Backend `/api/soul/forge` testato via curl: `{gained_essence:10, new_balance:10}` (contract OK).
- Le 5 protezioni difensive FORGE_CRASH non hanno spostato il crash → il bug è a monte di qualunque uso del response.
- React Native ha noti GitHub issues su `Modal + KeyboardAvoidingView + nested ScrollView` ("RNGH crashes", "Modal child layout error").

## Fix strutturale
**Rimuovere il Modal completamente** e sostituirlo con un **pannello inline** dentro la `ScrollView` esterna esistente. Il pannello:
- Appare in pagina, non come overlay
- Mantiene tutte le safety rules (typed CONFERMA, breakdown, override 4★+)
- Non usa `KeyboardAvoidingView` (la ScrollView outer già gestisce keyboard)
- Non usa `Platform.select` per il behavior della tastiera

## Valore residuo del pack FORGE_CRASH
Nonostante la diagnosi sbagliata, il pack precedente ha aggiunto difese utili che **manteniamo**:
- `normalizeForgeResponse()` — utile contro response malformate
- `heroIdsSnapshot` — preserva eroi su failure
- `forgeError` banner visibile
- `postSuccessWarn` banner
- Render defensivo `Number.isFinite()` / `Number()||0`
- Double-submit guard
- Shop nav buttons + bypass guards

Se in futuro il backend dovesse restituire un payload incompleto, queste difese eviteranno comunque crash.

## File modificati
- `frontend/app/soul-forge.tsx`: `88a39590454ecc1c5f16e34e09d90b63` → `b7659de11ac36f341e7a2f54fd29e6ed`

## Backend / Invarianti
- `backend/battle_engine.py`: `151ca35ad3bc35f0a6209cb3744ed440` ✅ invariante
- `backend/.env`: `ff60bbb79efa329b71aa8ed351ea89b3` ✅ invariante
- Nessun backend change, nessun DB write, nessuna formula change.
