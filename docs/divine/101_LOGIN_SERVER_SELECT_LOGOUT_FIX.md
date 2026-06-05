# 101 — LOGIN / SERVER SELECT / LOGOUT FIX — v101

> Lingua: Italiano. Politica: NO blind destructive, NO fake PASS.

## Bug originale (QA device iPhone 13 / Expo Go)

- L'app entra direttamente in Home dopo il login (gate server select bypassato)
- `/servers` era read-only/locked
- `Esci dal gioco` disconnetteva parzialmente ma non riportava al login

## Flow atteso post-v101

```
no session         → /login (index.tsx mostra form)
login valido       → /servers (gate v101)
server scelto      → /(tabs)/home
cambia server      → /servers
logout account     → clear v101_selected_server_id + clear token → /login
```

## Modifiche applicate

### 1. `frontend/app/index.tsx`
- `useEffect` post-load: se `user` esiste, controlla `AsyncStorage.getItem('v101_selected_server_id')`:
  - se assente → `router.replace('/servers')`
  - se presente → `router.replace('/(tabs)/home')`
- `onSubmit` post-login/register: stesso routing condizionale verso `/servers` o `/(tabs)/home`.

### 2. `frontend/context/AuthContext.tsx`
- `logout()` ora rimuove ANCHE `v101_selected_server_id` da AsyncStorage, oltre al `token`.
- Così al prossimo login l'utente viene riportato a `/servers`.

### 3. `frontend/app/(tabs)/menu.tsx`
- Tasto "ESCI DAL GIOCO": dopo `await logout()` esegue `router.replace('/')` per tornare immediatamente al login screen.

## Note di scope

- La logica di selezione attiva del server in `frontend/app/servers.tsx` (write `AsyncStorage v101_selected_server_id` al tap su un server) e' lasciata a un pack v102 di wiring per non ristrutturare la screen `servers.tsx` in modo invasivo. v101 fixa il **gate di routing** che era il blocker reale del QA device.
- v96 SecureStore clear gestito autonomamente dal proprio `AuthContext.logout()`. Per pulizia totale serve un pack di unificazione futuro.

## Safety

```
auth_session_deletion_outside_logout = false
raw_oauth_logs                       = false
fake_PASS                            = false
```
