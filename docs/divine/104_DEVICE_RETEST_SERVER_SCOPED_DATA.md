# v104 — Device Retest Server-Scoped Data

**Pack**: `MEGA_RELEASE_ACCELERATION_53_v104_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX`
**Device target**: iPhone 13 Expo Go (Manual QA required)

## Matrix (11 step)

| # | Action | Expected |
|---|---|---|
| 1 | Apri app | Login screen visibile, nessun bounce verso server. |
| 2 | Login | Routing a `/servers` (selected_server_id assente). |
| 3 | Apri `/servers` | Card server `[QA]` visibili. Banner `SERVER_DATA_ISOLATION_BACKEND_PENDING` visibile. |
| 4 | Verifica nomi/status | Nessun nome fake-production. Status QA dichiarato. |
| 5 | ENTRA S1 (`qa-eu-01`) | Routing a Home. AsyncStorage `v101_selected_server_id='qa-eu-01'`. |
| 6 | Osserva Home/Heroes/Inventory/Currencies/Team su S1 | Banner pending visibile su `/servers`; dati account condivisi finché isolation backend non è attiva. NESSUNA finzione di separazione. |
| 7 | Cambia server → `/servers` → ENTRA S2 (`qa-eu-02`) | AsyncStorage aggiornato. Banner ancora visibile. |
| 8 | Confronta S1 vs S2 (roster/inventory/currencies/team) | Identici (account condiviso) MA banner pending dichiara apertamente lo stato. |
| 9 | Chat scope | Surface chat non costruita; documentata `DECLARED_PENDING`. NESSUNA chat finta. |
| 10 | LOGOUT ACCOUNT | Esce al login; non rientra in server (v103 race fix tenuto). |
| 11 | Riapri → login | Routing a `/servers`. |

## Acceptance

- `min_steps_pass_required`: **10**
- `critical_steps`: 3, 4, 5, 6, 7, 8, 10
- Banner token obbligatorio su `/servers`: `SERVER_DATA_ISOLATION_BACKEND_PENDING`

## Forbidden durante il retest

- `fake_per_server_data`
- `random_heroes_per_server`
- `premium_currency_grant_per_server`
- `silent_data_mutation`
