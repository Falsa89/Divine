# 154B — Legacy Current-Server Read Model

**Verdict:** `TRACK_B_LEGACY_CURRENT_SERVER_READ_MODEL_READY` · design-only

## Modello di lettura
- **Read source primario**: `users.server` (string)
- **Disponibile via**: `GET /api/user/profile` (già esistente) · (futuro) `GET /api/account/server-profiles/preview`
- **Semantica**: display-only, mai interpretato per consentire selezione
- **Active switching**: ❌
- **Write back**: ❌

## Fallback se utente senza server
- Display: "Anteprima dual-read in preparazione"
- Behavior: locked preview identico, nessun error toast, nessun retry

## Evitare divergenza con server_profiles
- mai derivare `users.server -> server_profile_id` lato client
- mai cache su derived profile_id
- mai write su `users.server` finché dual-write non abilitato

## Mapping futuro
- seed pack materializza `users.server` in `server_profiles` con `archive=False`
- mapping creato server-side, mai client-side
- dual-write window: entrambi i campi sincronizzati; reads preferiscono `profile_id` quando presente

## Implementazione corrente nella locked preview
Placeholder "Anteprima dual-read in preparazione" (Track E polish). Quando auth/contract hardening landerà, mostrerà `Server attuale: {users.server || none}`.
