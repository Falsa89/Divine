# 155C — Pre-Home Server Selection UX Requirement

**Verdict:** `TRACK_C_PRE_HOME_SERVER_SELECTION_UX_REQUIREMENT_READY` · requirement-only

## Future flow
`AccountLogin → PreHomeServerSelection → Home`

Route futura: `/login-server-select` (o `/(auth)/server-select`).

## Sezioni richieste (4)
1. **Ultimo server usato** — `preview.last_used_profile_id`
2. **Server recenti** — `profiles` filtered by `last_played_at desc`
3. **Server disponibili** (required) — `preview.profiles[]`
4. **Nuovi server** — filter `server_state == 'new'`

## Per-card fields
`server_name` · `server_region` · `server_state badge` · `account_level` · `last_played_at` relative · capacity indicator

## Legend visuali
- 🟢 online (selezionabile)
- 🟡 full (badge PIENO, non selezionabile)
- 🟠 maintenance (badge MANUTENZIONE, account profile visibile)
- 🔵 new (badge NUOVO)
- ⚪ unknown (retry prompt)

## Fallback scenarios (4)
- one server only → auto-select (richiede `SERVER_SELECTION_AUTO_SKIP_APPROVAL`)
- no server profile yet → mostra solo "Server disponibili"
- all maintenance → lista locked + banner + retry
- 503 → fallback message + redirect a `/servers` internal preview

## Rapporto con `/servers` esistente
`/servers` (locked preview interno) resta visibile durante transizione; route futura `/login-server-select` non condivide stato. Deprecazione `/servers` interno deferred 1 release dopo GA.
