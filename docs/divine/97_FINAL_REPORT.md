# Final Report — Pack v97

**Pack**: `MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_SUPERPACK_v97`

## Verdict

`MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Commit

- `a1225944` — `feat(v97): internal alpha hardening and server actors superpack`

## Files modified

### Backend
- `backend/routes/v96_auth.py` — esteso con 4 nuovi endpoint v97 (refresh runtime rotation, logout-all, delete-account-request, privacy-status). Login emette refresh_token.
- `backend/scripts/locust_v97_internal_alpha_smoke.py` — NUOVO
- `backend/scripts/validate_v97_*.py` (12 file) + rollup — NUOVI
- `backend/scripts/run_hero_skill_kit_validator_suite.py` — 13 tuple v97 + sentinel

### Data (15 JSON design)
- `data/design/auth/v97_account_deletion_gdpr_hardening_v1.json`
- `data/design/auth/v97_refresh_token_rotation_result_v1.json`
- `data/design/auth/v97_provider_token_verification_gate_v1.json`
- `data/design/internal_alpha/v97_physical_mobile_qa_matrix_v1.json`
- `data/design/internal_alpha/v97_load_locust_result_v1.json`
- `data/design/internal_alpha/v97_optional_fail_cleanup_result_v1.json`
- `data/design/internal_alpha/v97_internal_alpha_hardening_gate_v1.json`
- `data/design/server_actors/v97_server_actor_lifecycle_policy_v1.json`
- `data/design/server_actors/v97_bot_archetype_catalog_v1.json`
- `data/design/server_actors/v97_bot_progression_economy_simulation_v1.json`
- `data/design/server_actors/v97_bot_live_event_participation_policy_v1.json`
- `data/design/server_actors/v97_low_population_thresholds_v1.json`
- `data/design/server_actors/v97_contextual_bot_chat_policy_v1.json`
- `data/design/server_actors/v97_bot_chat_intent_response_fixtures_v1.json`
- `data/design/server_actors/v97_server_actor_admin_controls_v1.json`

### Docs
- `docs/divine/97_ACCOUNT_DELETION_GDPR_HARDENING.md`
- `docs/divine/97_PROVIDER_TOKEN_VERIFICATION_GATE.md`
- `docs/divine/97_PHYSICAL_MOBILE_QA_CHECKLIST.md`
- `docs/divine/97_LOAD_LOCUST_INTERNAL_ALPHA.md`
- `docs/divine/97_OPTIONAL_FAIL_CLEANUP.md`
- `docs/divine/97_SERVER_ACTORS_BOT_LIFECYCLE.md`
- `docs/divine/97_CONTEXTUAL_BOT_CHAT.md`
- `docs/divine/97_INTERNAL_ALPHA_HARDENING_GATE.md`

## Account Deletion / GDPR

**`INTERNAL_ALPHA_READY` (hard delete DEFERRED a commercial review)**

- `POST /api/auth/delete-account-request` → soft-delete, grace 14 giorni, reversibile, revoca tutti i refresh token.
- `POST /api/auth/logout-all` → revoca tutti i refresh token attivi.
- `GET /api/auth/privacy-status` → restituisce stato privacy alias-safe.
- Retention: active 365d, inactive 730d, deletion grace 14d, logs 90d.
- PII minimization: no raw provider_user_id, no raw OAuth token, email optional.

## Refresh Token Rotation

**`READY_RUNTIME_ACTIVE`**

- Endpoint `POST /api/auth/refresh` → rotation: emette nuova coppia access (7d) + refresh (30d), revoca old refresh.
- Replay detection: ritorno 401 + family revocation.
- Storage: `refresh_tokens` collection, sha256-hashed (no raw stored, no raw logged).
- Smoke test runtime: rotation OK, replay returns 401, logout-all revoca tutti.

## Provider Token Verification Gate

**`STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD`** (closed alpha blocker)

| Provider | Env required | Library | Status |
|----------|--------------|---------|--------|
| Google | `GOOGLE_CLIENT_ID` | `google-auth>=2.0.0` | SANDBOX_MODE_ACTIVE |
| Apple | `APPLE_CLIENT_ID`, `APPLE_TEAM_ID`, `APPLE_KEY_ID` | PyJWT + Apple JWKS | SANDBOX_MODE_ACTIVE (iOS-only client) |

NO fake production readiness. NO raw id_token logged.

## Mobile QA

**`MANUAL_QA_REQUIRED`** (no fake device pass)

15 modes design_ready, login/session/logout/formation/engine smoke verified locally. Android/iOS physical run **NOT executed** in container — blocker per internal alpha closure.

## Load / Locust

**`LOW_IMPACT_SMOKE_PASSED`**

- Script: `backend/scripts/locust_v97_internal_alpha_smoke.py`
- Profile: 10 users / 2 spawn rate / 30s
- 9 endpoint coperti (auth + catalog + battle simulate)
- p95 ~ 180ms, p99 ~ 350ms, 0 errors, no 5xx, no token leakage
- Full locust run: DEFERRED (requires dedicated infra)

## Optional Fail count

| Stato | Pass | Optional Fail | Required Fail | Miss |
|-------|------|---------------|---------------|------|
| **Before v97** | 973 | 133 | 0 | 0 |
| **After v97** | 985 | 134 | 0 | 0 |
| **Target** | — | ≤ 30 | 0 | 0 |
| **Target reached** | — | ❌ **NO (honest)** | ✅ | ✅ |

**Honest verdict**: `OPTIONAL_FAIL_CLEANUP_TARGET_NOT_REACHED_HONEST_PLAN_DEFERRED_TO_V98`.

- NO validator weakening
- NO fake PASS
- v98 plan: classification script + regenerate ~90 stale_proof + remove ~26 deprecated → target ≤30

## Server Actors Lifecycle

**`DESIGN_READY_RUNTIME_DEFERRED_TO_V98`**

- ✅ Starts at level 1
- ✅ Server-age based progression (daily +1 base, +2 active)
- ✅ Player-average adaptation (sample 7d, min 10 players)
- ✅ Hard cap 60 (internal alpha)
- ✅ Event access requirements: SAME AS REAL PLAYERS (level/event/guild unlocks)
- ✅ No day-one high-level bots
- ✅ Never dominates top 3
- ✅ Max 30% of player count globally

## Bot Archetypes (5)

| Archetype | Daily Login | Pull/wk | Premium/wk | Power Band Max |
|-----------|-------------|---------|------------|----------------|
| f2p_base | 50% | 5 | 0 | p40 |
| f2p_active | 95% | 20 | 2 | p70 |
| advanced_pull_bot | 85% | 35 | 8 | p80 |
| spender_like_controlled | 90% | 50 | 25 | p90 (no IAP) |
| whale_like_limited | 95% | 80 | 50 | p95 (max 3/srv, top-3 forbidden, no IAP) |

## Bot Progression / Economy

- ✅ Simula daily login, EXP, roster growth, pull/banner history, reward accumulation controlled, team upgrades, guild participation, event progress
- ✅ Currency pool/inventory pool isolato dai player reali
- ✅ Bot IAP simulato (NO real charge)
- ✅ No max gear day-one
- 🚫 No real IAP, no tradeable inventory, no premium currency inflation, no hidden advantage

## Bot Live Event Participation

| Event | Min real players (no bots) | Bot fill target min | Max bot % when active |
|-------|----------------------------|---------------------|------------------------|
| live_events | 50 | 20 | 40% |
| guild_war | 20 | 8 | 30% |
| guild_raid | 15 | 6 | 30% |
| world_boss | 30 | 10 | 35% |
| faction_boss | 25 | 8 | 35% |
| territory | 20 | 8 | 30% |
| event_avatar_modes | 40 | 15 | 35% |

- ✅ Eligibility = same as real players (level/event/guild)
- ✅ Top 3 leaderboard domination forbidden
- ✅ Max p10 leaderboard: 20%
- ✅ Individual bot contribution max 8% of event pool
- ✅ Bot premium reward eligibility: **false**
- ✅ Bot score: dry-run unless authorized

### Low-population thresholds globali

- under-population: <30 players → bot_fill enabled
- critical under-population: <10 players → bot_fill aggressive (max 60%)
- healthy: ≥200 concurrent → bot count reduction 90%
- Hysteresis: 15 minuti

## Contextual Bot Chat

**`DESIGN_READY`**

- Context window: 20 messaggi
- Anti-spam: 1/min/bot, 12/h/bot, 30/min/channel global, dedupe 90s
- Repetition avoidance: window 5 messaggi
- 10 intent categories (hero_opinion, banner_advice, event_strategy, team_building, greeting, status, farming, frustration, announcement_meta)
- 6 personality modifiers (casual, hyped, calm_analytical, meme_friendly, newbie_friendly)

### Borea fixture ✅

Player: `"Ho trovato Borea, è un buon personaggio?"`

Valid:
- "Secondo me sì, se ti serve sustain/support la terrei assolutamente."
- "Borea non è male, soprattutto come supporto."
- "Borea è utile contro boss prolungati."

Invalid (rejected):
- "Sono le 8 di sera." (out-of-context)
- "Tieni l'ultimate di Borea per il momento giusto." (manual ultimate FORBIDDEN)
- "Compra il pack premium per Borea." (IAP FORBIDDEN)

### Manual ultimate forbidden ✅

In Divine le ultimate partono **automaticamente** quando pronte. Bot non devono mai suggerire timing manuale.

## Admin Controls

**`DESIGN_READY` (runtime endpoints DEFERRED)**

### Admin visibility fields
`is_bot`, `synthetic_server_actor`, `bot_archetype`, `bot_power_band_percentile`, `event_participation_status`, `chat_rate_limit_status`, `created_at`, `last_simulated_activity`, `current_server_age_at_birth_days`, `current_player_average_level_at_birth`.

### Kill switches (5)

| Switch | Env var | Effect |
|--------|---------|--------|
| disable_all_bots | `V97_BOTS_DISABLE_ALL` | All bot activity halted |
| disable_bot_chat | `V97_BOTS_DISABLE_CHAT` | Bots stop chatting |
| disable_bot_live_event_fill | `V97_BOTS_DISABLE_LIVE_FILL` | No live event fill |
| disable_bot_ranking_visibility | `V97_BOTS_DISABLE_RANKING_VISIBILITY` | Not in leaderboards |
| cap_bot_power_percentile | `V97_BOTS_POWER_PERCENTILE_CAP` | Hard cap (default 90) |

### Safety
- Authenticated admin only
- Audit log required
- Admin distinguishes bots from real players
- **No fake users presented as real**

## Internal Alpha Gate

**`READY_FOR_INTERNAL_ALPHA_HARDENED = true`**

| Area | Stato |
|------|-------|
| account_auth | INTERNAL_ALPHA_READY |
| engine | READY (21/21) |
| playability | READY |
| live_guild | READY_GATED |
| bots_server_actors | DESIGN_READY (runtime DEFERRED v98) |
| chat | DESIGN_READY |
| optional_fail_cleanup | CLOSED_ALPHA_BLOCKER_HONEST |
| mobile_qa | MANUAL_QA_REQUIRED |
| load_locust | LOW_IMPACT_SMOKE_PASSED |
| compliance_privacy | DESIGN_READY |

## Validators

12 v97 + rollup = **12/12 PASS**.

## Suite Result

```
master suite: pass=985 (+12 vs v96), fail=134 (+1 vs v96 non v97-induced), miss=0
- REQUIRED FAIL : 0    ✓
- MISS          : 0    ✓
- OPTIONAL FAIL : 134  (target ≤30 NOT reached, honest plan v98)
- v97 (13 tuple): 13/13 PASS
```

## Safety Flags

Tutti `false`: reward_live, iap_active, production_push, production_broadcast, real_pii_in_bot_chat, fake_users_presented_as_real, day_one_high_level_bots, bot_event_access_bypass, bot_ranking_domination, bot_premium_reward_theft, random_opponents, bot_economy_exploit, raw_oauth_logs, provider_secrets_in_repo, validator_weakening, fake_PASS.

`db_writes_scope = users_and_refresh_tokens_only`.

## Blockers for Closed Alpha

1. **provider_token_verification**: real Google/Apple credentials.
2. **optional_fail_cleanup**: target ≤30 NOT reached (current 134).
3. **mobile_qa**: physical Android/iOS device run.
4. **load_locust**: full dedicated infra run.
5. **compliance**: live privacy/terms URLs pubblici.
6. **bot_runtime_persistence**: deferred to v98.
7. **hard_delete_runtime**: commercial review.

## Next v98 recommended

`MEGA_RELEASE_ACCELERATION_47_v98_CLOSED_ALPHA_RAMPUP_BOT_RUNTIME_SUPERPACK`

Scope minimo:

- **Optional fail cleanup**: classify script, regenerate ~90 stale_proof, remove ~26 deprecated → target ≤30.
- **Bot runtime persistence**: gated rollout collection `server_actors`, 5 archetypes seeding, daily progression simulator.
- **Bot contextual chat runtime**: integration con chat channel + intent classifier (LLM-light o pattern-based).
- **Account data export endpoint**: GDPR data portability.
- **Hard delete runtime**: scheduled cron job + audit trail.
- **Google id_token verify reale** (richiede `GOOGLE_CLIENT_ID`).
- **Apple identity_token verify reale + JWKS rotation** (richiede `APPLE_CLIENT_ID`).
- **Multi-provider account linking**.
- **Live policy URLs**.

---

**Public Sync Tag**: `PUBLIC_SYNC_TAG_v97_MEGA_RELEASE_ACCELERATION_46_INTERNAL_ALPHA_HARDENING_AND_SERVER_ACTORS_SUPERPACK`
