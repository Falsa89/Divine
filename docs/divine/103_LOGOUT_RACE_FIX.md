# 103 — LOGOUT RACE FIX + AUTH UNIFICATION ROBUST — v103

> Lingua: Italiano.

## Bug pre-v103

LOGOUT ACCOUNT rimbalzava brevemente in `/servers` o `/(tabs)/home` prima di restare a `/login`. Su kill+restart restava a `/login` (= conferma che la state era effettivamente cancellata, ma il rimbalzo iniziale era un'esperienza utente brutta).

## Root cause

1. `index.tsx` useEffect ridirige basandosi su `user` truthy in closure stale prima che logout state propaghi.
2. v96 SecureStore non clearato esplicitamente dal menu logout (rimaneva sessione).
3. Ordine operazioni non garantito tra logout React state vs `router.replace` vs AsyncStorage clear.

## Fix v103

### Flag-based skip redirect
- Nuova chiave AsyncStorage: `v103_logout_in_progress`.
- **Set** dal pulsante LOGOUT ACCOUNT (prima operazione, sincrona logica).
- **Checked** dall'useEffect di `index.tsx` PRIMA di qualsiasi `router.replace`.
- **Auto-cleared** da `index.tsx` con `setTimeout(1500ms)` dopo la detezione.

### Sequenza completa LOGOUT ACCOUNT

```
1. user tap LOGOUT ACCOUNT
2. AsyncStorage.setItem('v103_logout_in_progress', 'true')
3. AsyncStorage.removeItem('v101_selected_server_id' + 'v102_*' + 'token' legacy)
4. SecureStore.deleteItemAsync('v96_auth_token' + 'v96_auth_account')
5. await logout() (legacy AuthContext azzera user state)
6. router.replace('/')
7. index.tsx remount: useEffect vede flag attivo → NO redirect
8. dopo 1500ms flag auto-clear; nel frattempo user e' diventato null
9. index.tsx mostra login form (no bounce)
```

## Auth Context Unification v103

Strategia: **`BRIDGE_LOGOUT_ROBUST`**.

- v102 aveva solo bridge marker passivo (import senza chiamata diretta).
- v103 chiama `SecureStore.deleteItemAsync` direttamente per `v96_auth_token` e `v96_auth_account`.
- Full unification (single provider) deferred a v104+.

## Atteso post-v103

```
logout_routes_to_login_immediately   = true
no_bounce_back_to_servers            = true
no_bounce_back_to_home               = true
kill_restart_stays_on_login          = true
```

## Safety

```
auth_session_deletion_outside_logout = false
token_raw_logs                       = false
unexpected_token_loss                = false
provider_secrets                     = false
fake_PASS                            = false
```
