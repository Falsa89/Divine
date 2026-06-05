# 102 — DEVICE RETEST SERVER FLOW — v102

> Lingua: Italiano. Target device: iPhone 13 / Expo Go.

## Matrix di test (12 step, ~5-10 min)

| # | Azione | Risultato atteso | OK? |
| --- | --- | --- | --- |
| 1 | App start senza session | redirect a `/login` (form email/password visibile) | ⏹️ |
| 2 | Login valido | redirect a `/servers` (gate v101 attivo) | ⏹️ |
| 3 | `/servers` caricato | 4-5 server cards visibili, banner `SERVER PROFILE FALLBACK` visibile se backend non disponibile, sezioni Server consigliato/Tutti i server | ⏹️ |
| 4 | Tap pulsante **ENTRA** su server online (Aurora EU-01) | label cambia in `Entrata...`, poi route a `/(tabs)/home` | ⏹️ |
| 5 | Verifica home raggiunta | tabs visibili: home/inventory/character/menu | ⏹️ |
| 6 | Vai a tab **Menu** | pulsanti `CAMBIA SERVER` (viola) + `LOGOUT ACCOUNT` (rosso) visibili in fondo | ⏹️ |
| 7 | Tap **CAMBIA SERVER** | route a `/servers`; session NON cancellata; lista server visibile di nuovo | ⏹️ |
| 8 | Tap **ENTRA** su altro server (Crepuscolo EU-02) | sovrascrive `v101_selected_server_id`; route a `/(tabs)/home` | ⏹️ |
| 9 | Menu → Tap **LOGOUT ACCOUNT** | clear AsyncStorage `v101_selected_server_id` + `v102_*` + token legacy; route a `/` (login form mostrato) | ⏹️ |
| 10 | Kill + restart app | App parte direttamente a `/login` (no auto-home, no auto-server) | ⏹️ |
| 11 | Tap **ENTRA** su server in MANUTENZIONE | pulsante grigio disabled, label `Non disponibile`, tap no-op | ⏹️ |
| 12 | Test safe area su notch iPhone 13 | SafeAreaView rispettato; nessun contenuto coperto | ⏹️ |

## Acceptance

- Step critici: **2, 3, 4, 7, 9, 10** → devono passare
- Min step PASS richiesti: **10/12**

## Note

- Backup credentials dell'utente test sono in `/app/memory/test_credentials.md` se già configurate.
- Se il banner `SERVER PROFILE FALLBACK` non appare, vuol dire che il backend ha risposto con dati live: in quel caso documentare lo status e procedere.
- Se tap **ENTRA** su server online non porta in home, controllare i log Expo Metro per errori di routing.
