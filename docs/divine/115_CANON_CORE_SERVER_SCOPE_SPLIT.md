# Canon SOT — Core Server-Scope Split (Pack 92)

> Sentinella: `PUBLIC_SYNC_TAG_v110_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP`
> Pack di emissione: `MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK`

## Decisione canonica

Il seguente split è la **Source-of-Truth** per ogni nuovo pack runtime.

### Account-wide (resta globale)
- Account identity / email / username
- Auth tokens / JWT
- Global entitlements / purchase entitlements
- **Hard / premium currency**:
  - `gems` — definita globale, IAP-coupled
  - `gold` — legacy account-wide; promozione a server-scoped DEFERITA a pack futuro autorizzato

### Server-scoped (per (user_id, server_id) via PSP)
- `user_heroes` / roster posseduto / livelli / stelle / build operative (Pack 81)
- `team_formation` (Pack 88)
- `inventory` / use-exp / item-shop buy / skill upgrade (Pack 89/90/91)
- **Soft / server currencies** usate nel gameplay → `psp.soft_currencies`:
  `honor`, `guild_points`, `prana`, `soul_seals`, `mission_coins`, `dimension_frags`, `star_dust`
- `story_progress` → `psp.story_progress` (Pack 92 read guard)
- `user_equipment` → migration richiesta prima della promozione strict (Pack 92 honest deferred blocker)
- `player_level` / `player_exp` / progressione operativa → PSP

## Vincoli non-negoziabili
- Nessun nuovo server eredita roster, team, inventory, equipment, story, currencies server-bound da S1.
- Nessun fallback account-wide per dati server-bound nei path player-facing.
- Nessun silent `s1` literal nel frontend.
- I loader player-facing con `server_id` devono filtrare **realmente** o bloccare onestamente (no false `filter_applied=true`).
- Reward live OFF; progress live OFF; release readiness NON claimed.
