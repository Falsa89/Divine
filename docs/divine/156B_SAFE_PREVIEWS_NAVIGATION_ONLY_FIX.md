# 156B — Safe Previews Navigation-Only Fix (Track B)

Pack: `PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT_PACK`
Verdetto: `TRACK_B_SAFE_PREVIEWS_NAVIGATION_ONLY_FIX_IMPLEMENTED_SAFE`

## Bug
Le 3 card di `/safe-previews` si scurivano al tap ma non navigavano su mobile.

## Causa
Il componente esponeva un wrapper `<TouchableOpacity>` attorno a una `SafeFeatureCard` che a sua volta restituisce `<TouchableOpacity>` (quando non locked). Il child consumava il press senza onPress proprio, impedendo al parent di invocare `router.push`.

## Fix
Rimosso il wrapper esterno; `onPress={() => router.push(route)}` ora viene passato direttamente alla `SafeFeatureCard`. Aggiunti testID stabili. Nessuna nuova API, nessuna live action, nessun bottone mutativo.

## File toccati
- `frontend/app/safe-previews.tsx` (md5: `2473947c7c692ddc61c70082f82bdb65` → `e40dd47e489561bfcfcbee3acfc90758`)
- `SafeFeatureCard.tsx`: invariato (`8f65c7783690ae240c8f63c1c2729812`).

## Destinazioni (tutte locked/read-only)
- Codex Status Effects → `/status-codex`
- Anteprima Artefatti → `/artifacts-preview`
- Dimora Divina → `/housing-preview`

## DB / API / Flags
- 0 DB writes
- 0 nuove chiamate API
- 0 flag flips
