# Pack 97 — Daily Login Claim Source of Truth (SOT)

> Sentinel: `PUBLIC_SYNC_TAG_v110_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK`
> Pack: `MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_MEGAPACK`

## Identità della source

| Campo | Valore |
|---|---|
| `source_id` | `daily_login_claim` |
| `server_scoped` | **true** |
| `live` | **true** (gated da kill switches) |
| `idempotency` | **mandatory** |
| `pack_origin` | `pack_97` |
| `grant_fn` | `grant_daily_login_to_psp` (server-side fixed reward) |
| `per_source_kill_switch_env` | `DAILY_LOGIN_CLAIM_ENABLED` |
| `per_source_kill_switch_default` | **false** (OFF) |

## Daily Key Strategy

```
claim_key = "daily_login_<server_id>_<YYYY-MM-DD UTC>"
idempotency_token = sha1(claim_key)
```

- `claim_key` calcolato esclusivamente server-side. Il client NON puo' decidere la daily key.
- L'`idempotency_token` inviato dal client viene **ignorato** per daily_login_claim e sostituito col deterministic derivato.
- Garanzia DB-level: unique index `ux_user_server_claimkey_daily_login_pack97` con `partialFilterExpression={"claim_source": "daily_login_claim"}` su `(user_id, server_id, claim_key)`.

## Reward Payload Guard

```
fixed_reward = { "mission_coins": 10, "honor": 5 }
amount_cap_per_key = 100
```

- **Payload client viene IGNORATO**: il backend usa esclusivamente `fixed_reward` definito in `_grant_daily_login_to_psp`.
- Solo soft currency server-bound. **Vietati**: `gold`, `gems`, `pulls`, hero/equipment/inventory grants.
- Cap dailу per chiave: 100 (sanity bound).

## Endpoint

| Endpoint | Metodo | Auth | server_id | Note |
|---|---|---|---|---|
| `GET /api/daily-login/claim/health` | GET | no | n/a | Health info pubblico |
| `POST /api/daily-login/claim/preflight` | POST | sì | no | Ensure unique index |
| `POST /api/daily-login/claim` | POST | sì | **richiesto** | Claim live-gated |

### Flow strict (`POST /api/daily-login/claim`)

1. **Kill switch globale** (`REWARD_CLAIM_LEDGER_LIVE_ENABLED`) → 503 `REWARD_CLAIM_LEDGER_LIVE_DISABLED` se OFF
2. **Kill switch daily** (`DAILY_LOGIN_CLAIM_ENABLED`) → 503 `DAILY_LOGIN_CLAIM_DISABLED` se OFF
3. **server_id** required → 400 `SERVER_ID_REQUIRED`
4. **PSP** required → 409 `PLAYER_SERVER_PROFILE_REQUIRED`
5. **Test-only override** `_test_day_override=YYYY-MM-DD`: accettato SOLO se `users.pack_97_test_artifact=true`, altrimenti 403 `DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER`
6. **Compute** `claim_key` e `idempotency_token` server-side
7. **Replay check** su `reward_claim_ledger` per `(user_id, server_id, claim_source=daily_login_claim, claim_key)` → ritorna receipt esistente senza secondo grant
8. **Grant** via `_grant_daily_login_to_psp` (fixed reward) → atomic `$inc` SOLO su `player_server_profiles.soft_currencies.*`
9. **Ledger insert** con `claim_key`, `idempotency_token`, `_slc_pack_97_daily_login_claim=true`
10. **Race protection** via unique index (`partialFilterExpression`): se collision → reverse `$inc` + replay receipt

## Kill Switches (AND logic)

| Env Var | Default | Effect |
|---|---|---|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` | `false` | Globale Pack 96 |
| `DAILY_LOGIN_CLAIM_ENABLED` | `false` | Per-source Pack 97 |

Per claim eseguibile: **entrambi devono essere TRUE**. Logic AND.

## Frontend Consumer Gating

| Gate | Source | Default |
|---|---|---|
| UI feature flag | `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` | `false` (hidden in prod) |
| Server scope required | `useServerScope().serverId` truthy | n/a |
| Auth required | `useAuth().token` truthy | n/a |
| Preview page | `/daily-login-preview` route only | not linked from home |

## Non-Regression Statements

- ❌ NO mail/achievements/battlepass/AFK/event sources attivate.
- ❌ NO premium/hard currency grants possibili.
- ❌ NO double daily reward per user/server/day.
- ❌ NO release readiness claim.
- ✅ Pack 91/93/94/95/96 preserved (verificato via smoke E2E).
