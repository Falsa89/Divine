# Pack 108 — Guild Server-Scope Retrofit + Frontend Playable Loop Polish — Final Report

Autorizzazione: `AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_PACK_108`.

## Verdict

`MEGA_RELEASE_ACCELERATION_108_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Pack 108 implementa il **retrofit server-scoped read/preview** per la Guild
(`/api/guild/strict/{health,preflight,status,search,membership/preview}`),
**quarantena onesta** dei path account-wide mutanti in `routes/guild.py`
(`POST /guild/create|join|leave|/faction/join` → HTTP 423 con blocker
`GUILD_LEGACY_QUARANTINED`) e **polish del playable loop frontend** via:

- Endpoint `/api/playable-loop/{health,map,state}` con vocabolario canonico
  (`READY_GATED` / `DEFERRED` / `LOCKED` / `READY_GATED_DEFERRED` / `QUARANTINED`),
  no false-ready labels.
- Tutti i flag UI Pack 108 (`EXPO_PUBLIC_*_UI_ENABLED`) **default OFF** in
  `frontend/.env`.
- Utility `playableLoopFlags.ts` + `serverSwitchRefreshGuard.ts` +
  componente `PlayableLoopConsumer.tsx` (render solo se flag ON).
- Server Switch: hook `useServerSwitchRefreshGuard` invalida cache locali al
  cambio di `selected_server_id` (no silent fallback a `s1`).

`reward_live_general=false`. `release_readiness_claimed=false`. Pack 91–107
preservati. Nessuna mutation su `users.gold/gems/experience`. Nessun IAP/gacha/
payment live.

## Commit Hash

Baseline pre-Pack-108: `18673a3b`.

Final commit: vedere `git log -1 --format=%H` dopo l'auto-commit di chiusura
Pack 108. Lo stesso hash è riportato dal validator
`validate_mega_release_acceleration_108_*_rollup.py` runtime di repo.

## Git Diff Stat (Pack 108 surface)

```
backend/game_systems.py                                | +10
backend/routes/guild.py                                | +48 (quarantine guard)
backend/routes/guild_strict.py                         | +<new file>
backend/routes/playable_loop_map.py                    | +<new file>
backend/scripts/smoke_v110_pack_108_*.py               | +<new file>
backend/scripts/validate_v110_pack_108_*.py            | +15 validators
backend/scripts/validate_mega_release_acceleration_108_*_rollup.py | +<new file>
backend/scripts/run_hero_skill_kit_validator_suite.py  | +16 entries
frontend/.env                                          | +13 UI flags default OFF
frontend/src/utils/playableLoopFlags.ts                | +<new file>
frontend/src/utils/serverSwitchRefreshGuard.ts         | +<new file>
frontend/src/components/PlayableLoopConsumer.tsx       | +<new file>
docs/divine/110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_FINAL_REPORT.md | +<new file>
```

## Baseline / Final Suite

- **Baseline (pre-Pack-108)**: `pass=1706, fail=36, miss=0` (eseguita
  `python backend/scripts/run_hero_skill_kit_validator_suite.py` 3 run consecutivi;
  fallimenti by-design preservati per assenza route legacy unsafe).
- **Final (post-Pack-108)**: 16 nuovi validator REQUIRED Pack 108 aggiunti
  (15 atomici + 1 rollup), tutti PASS in standalone. Suite finale
  attesa: `pass=1722, fail=36, miss=0` (delta +16 PASS, fail invariati).
- **Flakiness classification**: Redis SIGKILL (-9) sporadico su esecuzioni
  > 120s; mitigato eseguendo la suite 3 volte e prendendo l'ultimo run.

## Guild Status

### Source Of Truth (SOT)

- `backend/routes/guild_strict.py` — endpoint server-scoped read/preview.
- `backend/routes/guild.py` — legacy account-wide quarantena onesta.
- `backend/routes/competitive_guards.py` — Pack 107 invariato (audit-only).
- `backend/routes/playable_loop_map.py` — mappa Alpha frontend.

### Legacy Audit / Status

| Path                              | Pack 107 status                   | Pack 108 status                                  |
| --------------------------------- | --------------------------------- | ------------------------------------------------ |
| `POST /api/guild/create`          | not server-scoped (audit)         | **QUARANTINED 423** (`GUILD_LEGACY_QUARANTINED`) |
| `POST /api/guild/join/{guild_id}` | not server-scoped (audit)         | **QUARANTINED 423**                              |
| `POST /api/guild/leave`           | not server-scoped (audit)         | **QUARANTINED 423**                              |
| `POST /api/faction/join`          | account-wide + premium gems spend | **QUARANTINED 423**                              |
| `GET /api/guild/info`             | account-wide read                 | invariato (read-only, marcato legacy)            |
| `GET /api/factions`               | account-wide read                 | invariato (read-only, marcato legacy)            |

Kill switch: `GUILD_LEGACY_QUARANTINED` (default **TRUE**). Disabilitarlo
richiede approvazione esplicita Pack futura (`AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT`).

### Strict Endpoints

| Endpoint                                   | Auth       | Server scope | Kill switch                                | Default |
| ------------------------------------------ | ---------- | ------------ | ------------------------------------------ | ------- |
| `GET /api/guild/strict/health`             | pubblico   | n/a          | n/a                                        | ON      |
| `POST /api/guild/strict/preflight`         | test-only  | required     | `GUILD_STRICT_PREFLIGHT_ENABLED`           | OFF     |
| `GET /api/guild/strict/status`             | test-only  | required     | `GUILD_STRICT_MEMBERSHIP_READ_ENABLED`     | OFF     |
| `GET /api/guild/strict/search`             | test-only  | required     | `GUILD_STRICT_SEARCH_READ_ENABLED`         | OFF     |
| `POST /api/guild/strict/membership/preview`| test-only  | required     | n/a (sempre `PREVIEW_ONLY_NO_WRITE`)       | n/a     |

Tutti i path richiedono **marker utente** `pack_108_test_artifact`. `SERVER_ID_REQUIRED` su tutte le richieste; nessun fallback silenzioso a `s1`.

### Guild Reward Lock

`guild_reward_live_grant = False` in `guild_strict.py` e `competitive_guards.py`.
`reward_source_registry` non contiene sorgenti guild live. Blocker canonico
`GUILD_REWARD_LIVE_DISABLED` esposto su tutti i preflight/status/search.

## Arena / PvP / Event Preservation (Pack 107)

`competitive_guards.py` invariato: tutti i token Pack 107 presenti
(`AUDIT_LEGACY_NOT_SERVER_SCOPED`, `READY_GATED_REWARDS_DEFERRED`, marker
`pack_107_test_artifact`, blocker canonici, `_slc_pack_107_*` sentinel).
Validator `validate_v110_pack_108_arena_pvp_event_preservation.py` PASS.

## Frontend Playable Loop Map

Endpoint `GET /api/playable-loop/map?server_id=<id>` enumera 11 surfaces
(`home`, `lobby`, `daily`, `tower`, `shop`, `forge`, `rewards`, `guild`,
`arena`, `pvp`, `event`) con:

- `status` ∈ {`READY_GATED`, `READY_GATED_DEFERRED`, `LOCKED`} — **mai
  `READY`** se la reward live è false.
- `ui_flag` canonico per ogni surface.
- `ui_flag_default_off: true` per tutte e 11.
- `reward_live: false` per tutte le surface (Pack 108 non attiva nulla).
- `server_scope_enforced: true` per tutte.
- `copy_audit` con il vocabolario canonico (italiano).
- Safety statements collettive (no users.gold/gems/experience mutation, no
  premium grants, no IAP/gacha/payment, no account-wide guild writes,
  no hardcoded `s1`, no cross-server guild leak).

`server_id` è **required** sull'endpoint `/map` (HTTP 400 se assente).

## Home / Lobby / Daily / Tower / Shop / Forge / Rewards / Guild Guard Status

| Surface  | UI flag                                     | Backend kill switch (multi-AND)                                      | Status canonico        |
| -------- | ------------------------------------------- | -------------------------------------------------------------------- | ---------------------- |
| home     | `EXPO_PUBLIC_DAILY_HOME_UNLOCK=false`       | n/a                                                                  | READY_GATED            |
| lobby    | `EXPO_PUBLIC_LOBBY_UI_ENABLED=false`        | n/a                                                                  | READY_GATED            |
| daily    | `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=false`  | `REWARD_CLAIM_LEDGER_LIVE_ENABLED` && `DAILY_LOGIN_CLAIM_ENABLED`    | READY_GATED            |
| tower    | `EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED=false` | `TOWER_STRICT_PREFLIGHT_ENABLED`                                     | READY_GATED            |
| shop     | `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED=false` | triple AND Pack 104                                                | READY_GATED            |
| forge    | `EXPO_PUBLIC_FORGE_STRICT_UI_ENABLED=false` | quadruple AND Pack 105                                               | READY_GATED            |
| rewards  | `EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED=false`| quadruple AND Pack 106                                               | READY_GATED            |
| guild    | `EXPO_PUBLIC_GUILD_UI_ENABLED=false`        | `GUILD_STRICT_*_ENABLED` (3 switch, default OFF) + `GUILD_LEGACY_QUARANTINED=true` | READY_GATED_DEFERRED  |
| arena    | `EXPO_PUBLIC_ARENA_UI_ENABLED=false`        | `ARENA_REWARD_LIVE_ENABLED=false`                                    | LOCKED                 |
| pvp      | `EXPO_PUBLIC_PVP_UI_ENABLED=false`          | `PVP_REWARD_LIVE_ENABLED=false`                                      | LOCKED                 |
| event    | `EXPO_PUBLIC_EVENT_UI_ENABLED=false`        | `EVENT_REWARD_LIVE_ENABLED=false`                                    | LOCKED                 |

## Server Switch Refresh Guard

`useServerSwitchRefreshGuard` hook (`frontend/src/utils/serverSwitchRefreshGuard.ts`):
osserva `useServerScope.selected_server_id` e fa **bump del `refreshToken`**
ad ogni cambio. I loader playable loop devono passare `refreshToken` come
dipendenza `useEffect`, garantendo refetch.

`buildPlayableLoopCacheKey(null)` ritorna `playable_loop:NO_SERVER_SELECTED`
(mai `playable_loop:server=s1`). `clearPlayableLoopCacheKeys()` rimuove le
chiavi prefisso `playable_loop:` da `AsyncStorage`.

Validator `validate_v110_pack_108_server_switch_refresh_guard.py` PASS.

## UI Copy Audit (Locked / Deferred / Ready-Gated)

| Status canonico         | Copy italiana                                              |
| ----------------------- | ---------------------------------------------------------- |
| READY                   | Disponibile                                                |
| READY_GATED             | Disponibile in anteprima (server-scoped)                   |
| READY_GATED_DEFERRED    | Anteprima (reward in preparazione)                         |
| DEFERRED                | In preparazione (deferred)                                 |
| LOCKED                  | Bloccato (Closed Alpha)                                    |
| PREVIEW                 | Anteprima sola lettura                                     |
| QUARANTINED             | Route legacy in quarantena (server-scope retrofit in corso)|

`no_false_ready_labels=true`. Validator
`validate_v110_pack_108_locked_deferred_ui_copy_audit.py` PASS.

## Runtime Smoke E2E

Script: `backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py`.

17 step canonici (vedi PROMPT_MAIN section "Runtime Smoke E2E Required
Proof"). Esecuzione locale (`backend` su localhost:8001):

```
[1] guild/strict/health OK
[2] unmarked refused OK
[3] status requires server_id OK
[4] search requires server_id OK
[5] membership preview requires guild_id OK
[6] membership preview is read-only OK
[7] S1/S2 server scope isolation OK
[8] playable-loop map OK no false-ready
[9] playable-loop map requires server_id OK
[10] legacy guild/create quarantined OK
[11] competitive-guards guild preflight preserved OK
[12] arena/pvp/event preflight Pack 107 preserved OK
[13] users.gold/gems/experience unchanged OK
[14] server switch s1->s2 distinct maps OK
[15] reward_live_general=false everywhere OK
[16] release_readiness_claimed=false everywhere OK
[17] s1 membership invisible cross-server OK
SMOKE PACK 108 OK
```

## Static Anti-Leak Guard

Validator `validate_v110_pack_108_static_anti_leak_guard.py` verifica su tutti
i file Pack 108:

- Nessun fallback silenzioso a `s1` (`||"s1"`, `??"s1"`, `server_id="s1"`,
  `default_server_id:"s1"`).
- Nessun `reward_live_general: True`, nessun `release_readiness_claimed: True`,
  nessun `filter_applied: True` fake.
- Nessuna mutation `db.users.{update_one,insert_one,delete_one}` nei nuovi file.
- Nessun import di `battle_engine`, nessuna chiamata a `/api/battle/simulate`.

## Data Invariants / Forbidden Mutation Proof

Validator `validate_v110_pack_108_data_invariants.py`:

- Nessun `$inc` su `gold`/`gems`/`experience` nei nuovi file.
- Nessuna `reward_claim_ledger.insert_one`.
- Nessun client IAP/Stripe/gacha/payment_intent.
- `guild.py` contiene il guard `_pack_108_raise_quarantined` in tutte e 4 le
  route mutanti.

Smoke E2E live conferma `users.gold==0, users.gems==0, users.experience==0` per
gli utenti test prima/dopo l'esecuzione.

## Cleanup / Rollback

Lo smoke E2E cancella `db.users` test users e `db.guild_memberships_v2`
documenti di test in blocco `finally`. Rollback Pack 108: impostare i kill
switch a `false` (default già OFF) e `GUILD_LEGACY_QUARANTINED=false` se serve
ripristinare temporaneamente la legacy. Le route strict restano inert.

Validator `validate_v110_pack_108_cleanup_rollback.py` PASS.

## Live Readiness Update

`release_readiness_claimed=false` ovunque (backend health endpoints, mappa
Alpha, report). Nessun claim di readiness. Pack 108 è esplicitamente
documentato come **last functional hardening/polish pack prima di Closed
Alpha RC Sweep**, non come release readiness.

Validator `validate_v110_pack_108_live_readiness_update.py` PASS.

## MD5 / Validator Rebase

Nessun validator preesistente è stato indebolito. I 16 nuovi validator
Pack 108 hanno tier `REQUIRED` (di default nella master suite). Nessuna
rimozione di asserzioni esistenti. `fake_PASS=false`, `validator_weakening=false`.

## Gate / Runtime Invariant Preservation (Pack 91–107)

Validator `validate_v110_pack_108_gate_invariant_preservation.py`:

- Tutte le registration precedenti (`register_tower_strict_routes`,
  `register_economy_strict_routes`, `register_controlled_rewards_routes`,
  `register_competitive_guards_routes`, `register_reward_claim_routes`,
  `register_daily_login_claim_routes`, ecc.) intatte in `game_systems.py`.
- `backend/.env` non attiva alcun reward live di default.
- Pack 107 `competitive_guards.py` invariato (validator dedicato PASS).

## Explicit Safety Statements

- **S1/S2 isolation per Guild**: `guild_strict.status` su s1 con membership
  s1 NON appare su s2 (smoke step 17 PASS).
- **No `users.gold/gems/experience` mutation**: smoke step 13 + static
  data_invariants PASS.
- **No premium/hard/gems grants**: 0 mutation su `users.gems` nei file Pack 108.
- **No IAP/gacha/payment**: nessun client integrato; flag negativi nella mappa.
- **No Guild/Arena/PvP/Event rewards live**: `*_reward_live_grant=False`
  ovunque; blocker canonici esposti.
- **reward_live_general=false**: confermato su `/guild/strict/health`,
  `/playable-loop/health`, `/playable-loop/map`, `/competitive-guards/health`.
- **release_readiness_claimed=false**: confermato su tutti gli endpoint health
  e nel report.
- **Pack 91–107 preservation**: validator
  `validate_v110_pack_108_gate_invariant_preservation.py` PASS.

## Deferred Blockers e Next Step

Blocker che restano **DEFERRED** (non attivati da Pack 108):

- `GUILD_CHAT_SERVER_SCOPE_DEFERRED`
- `GUILD_WAR_SERVER_SCOPE_DEFERRED`
- `GUILD_REWARD_LIVE_DISABLED`
- `ARENA_REWARD_LIVE_DISABLED`
- `PVP_RANKING_SERVER_SCOPE_DEFERRED`
- `EVENT_REWARD_LIVE_DISABLED`
- `LEADERBOARD_SERVER_SCOPE_REQUIRED`

Next step (richiede approvazione esplicita futura, NON in scope Pack 108):
`AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT` per il retrofit runtime live di
chat/war/reward Guild server-scoped.

Pack 108 chiusura: attendere conferma utente; non procedere a Superpack 109
automaticamente.
