# 153B — Track B: Servers Screen Locked Preview Implementation

**Verdict:** `TRACK_B_SERVERS_SCREEN_LOCKED_PREVIEW_IMPLEMENTED_SAFE`

## File modificato
- `/app/frontend/app/servers.tsx`
- Pre-pack MD5: `26f5c796425aafa933f46979928165f4`
- Post-pack MD5: `bb5fbd29db70ab942dc9f79dcfa6694c`

## Cosa è stato fatto
- Riscrittura completa coerente con `housing-preview` / `artifacts-preview` pattern
- Importato `SafeFeatureCard`
- Banner "Selezione Server in aggiornamento" con copy lock italiano
- Probe `GET /api/server-profiles/select` per renderizzare card 503/live/unavailable
- `GET /api/servers` ancora chiamato ma SOLO read-only (rows non interattive con badge `🔒 In arrivo`)
- Footer informativo con disclaimer

## Cosa è stato rimosso
- Funzione `select()` (POST mutativa)
- `Alert.alert('Server Selezionato!', 'Benvenuto!')`
- TouchableOpacity onPress per selezione server
- Stato `selecting`
- `router.back()` su success

## Vincoli
- 0 backend changes
- 0 DB writes
- 0 flag flips
- 0 menu changes
