# MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_MEGAPACK — FINAL REPORT

> Sentinel: `PUBLIC_SYNC_TAG_v110_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK`
> Approval ricevuta: `AUTORIZZO_V110_DAILY_LOGIN_CLAIM_AND_FRONTEND_UNLOCK_PACK_97`

## Verdict

**`MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

## Commit Hash

- Code + design + validators + smoke: `8bc44e5ce0199185de4208f3a41bee9289706dbf`
- Validator hotfix (Pack 96 source registry relaxed): `90124520`
- Final report + multirun result update: see footer commit.

`local_commit_only=true` — nessun remote git esterno disponibile in questo container.

## Git Diff Stat

```
backend/utils/reward_source_registry.py     | MOD (+30 lines: daily source + grant_fn)
backend/routes/daily_login_claim.py         | NEW (250+ lines)
backend/routes/__init__.py                  | MOD (+2 lines)
backend/game_systems.py                     | MOD (+5 lines)
backend/scripts/smoke_v110_pack_97_*.py     | NEW
backend/scripts/cleanup_v110_pack_97_*.py   | NEW
backend/scripts/validate_v110_pack_97_*.py  | NEW × 16
backend/scripts/validate_mega_..._97_*.py   | NEW (rollup)
backend/scripts/run_hero_skill_..._suite.py | MOD (+17 suite tuples)
backend/scripts/validate_v110_pack_96_reward_source_registry.py | MOD (relax for Pack 97+ sources)
frontend/src/components/DailyLoginClaimButton.tsx | NEW (130 lines)
frontend/app/daily-login-preview.tsx              | NEW (preview-only route)
docs/divine/117_DAILY_LOGIN_CLAIM_SOT.md          | NEW (SOT doc)
data/design/v110_pack_97_daily_login_claim_frontend_unlock/*.json | NEW × 15
```

## Baseline / Final Suite

| Run | Pass | Fail | Miss |
|-----|-----:|-----:|-----:|
| Baseline pre #1 | 1557 | 34 | 0 |
| Baseline pre #2 | 1557 | 34 | 0 |
| Baseline pre #3 | 1557 | 34 | 0 |
| Final post #1 | **1574** | **34** | **0** |
| Final post #2 | **1574** | **34** | **0** |
| Final post #3 | **1574** | **34** | **0** |

**Delta: +17 PASS, 0 nuovi FAIL, 0 MISS.** Nessun validator weakening.

## Daily Login Claim SOT

(file: `docs/divine/117_DAILY_LOGIN_CLAIM_SOT.md`)

- **source_id**: `daily_login_claim`
- **claim_key**: `daily_login_<server_id>_<YYYY-MM-DD UTC>` (server-side)
- **idempotency_token**: `sha1(claim_key)` (deterministico; client value ignorato)
- **Unique index DB**: `(user_id, server_id, claim_key)` con `partialFilterExpression={"claim_source": "daily_login_claim"}` → garanzia anti-double-claim DB-level
- **Reward fisso**: `{mission_coins: 10, honor: 5}` (server-side, payload client ignorato)
- **No double claim** per user/server/day

## Reward Registry Daily Source

(file: `backend/utils/reward_source_registry.py` + `v110_pack_97_reward_registry_daily_source_v1.json`)

| Source | live | server_scoped | grant_fn | reward_types | kill_switch_env | default |
|--------|:---:|:---:|---|---|---|:---:|
| `qa_controlled_soft_currency_claim` | ✅ | ✅ | `grant_soft_currency_to_psp` | soft currencies | global | n/a |
| `story_progress_marker_claim` | ✅ | ✅ | `grant_noop` | — | global | n/a |
| **`daily_login_claim`** ← Pack 97 | ✅ | ✅ | `grant_daily_login_to_psp` | mission_coins, honor | `DAILY_LOGIN_CLAIM_ENABLED` | **false** |

Pack 96 sources preservate.

## Daily Claim Endpoint

(file: `backend/routes/daily_login_claim.py`)

`POST /api/daily-login/claim?server_id=<sid>` body `{client_token?}`

Flow strict:
1. `_global_kill_switch_on()` → 503 `REWARD_CLAIM_LEDGER_LIVE_DISABLED`
2. `_daily_kill_switch_on()` → 503 `DAILY_LOGIN_CLAIM_DISABLED`
3. `server_id` → 400 `SERVER_ID_REQUIRED`
4. PSP check → 409 `PLAYER_SERVER_PROFILE_REQUIRED`
5. `_test_day_override` accettato solo se `users.pack_97_test_artifact=true`; altrimenti 403 `DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER`
6. `compute_daily_claim_key(sid, day_override)` server-side
7. Replay check su ledger `(user_id, server_id, daily_login_claim, claim_key)`
8. Grant via `grant_daily_login_to_psp` → `$inc` SOLO su `player_server_profiles.soft_currencies`
9. Ledger insert con `_slc_pack_97_daily_login_claim=true`
10. Race protection via unique partial index + reverse `$inc`

## Reward Payload Guard

(file: `v110_pack_97_reward_payload_guard_v1.json`)

- **Fixed reward server-side**: `{mission_coins: 10, honor: 5}`
- **Client payload IGNORATO** (verificato via smoke: `payload={"gold": 999999}` → granted = `{mission_coins: 10, honor: 5}`)
- **Cap per chiave**: 100
- ❌ NO pulls, NO hero/equipment/inventory grants
- ❌ NO premium / hard currency (`gold, gems`)
- ✅ Solo soft currency server-bound

## Frontend Consumer Unlock

(file: `frontend/src/components/DailyLoginClaimButton.tsx` + `frontend/app/daily-login-preview.tsx`)

| Gate | Default |
|------|---------|
| `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` | `false` (hidden in production) |
| `useServerScope().serverId` truthy | required |
| `useAuth().token` truthy | required |
| Preview route `/daily-login-preview` | not linked from home |

**Stati gestiti**: idle, loading, claimed, already_claimed, kill_switch_off (global|daily), psp_missing, error.

❌ NO mail/achievements/battlepass/event/AFK consumer in Pack 97.

## Kill Switch / Flags

| Env Var | Default | Track |
|---------|:-------:|-------|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` (Pack 96) | `false` | global |
| `DAILY_LOGIN_CLAIM_ENABLED` (Pack 97) | `false` | per-source |
| `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` | `false` | frontend |

**AND logic**: per claim eseguibile, ENTRAMBI i kill switches backend devono essere `true`.

### Smoke lifecycle (verificato)
- **Initial**: entrambi OFF (default safety)
- **Override durante smoke**: scrittura in `/app/backend/.env` + restart backend
- **Final**: env vars rimosse → entrambi tornano a OFF di default
- **Verifica finale**: `health endpoint` ritorna `claim_executable: false`

## Runtime Smoke E2E

Script: `backend/scripts/smoke_v110_pack_97_daily_login_claim_e2e.py`
Marker: `pack_97_test_artifact=true`. Utenti: `pack97_test_user_<ts>@test.com`.

**Risultato: 27/27 proof verde + cleanup**

```
both_kill_switches_default_off ✓                  cross_server_b_no_psp_409 ✓
register_ok ✓                                     cross_server_isolation_independent_claim ✓
ensure_psp_a_ok ✓                                 day_override_forbidden_for_non_test_user ✓
mark_pack_97_ok ✓                                 pack_96_premium_block_preserved ✓
claim_blocked_when_global_off ✓                   pack_95_story_strict_preserved ✓
claim_blocked_when_only_global_on ✓               pack_94_equipment_loader_preserved ✓
both_kill_switches_enabled ✓                      pack_93_wallet_split_preserved ✓
daily_preflight_indices_ok ✓                      pack_95_shops_buy_quarantine_preserved ✓
first_daily_claim_success_with_fixed_reward ✓     daily_kill_switch_disable_re_blocks ✓
same_day_replay_no_double_grant ✓                 kill_switches_restored_to_original ✓
psp_balance_unchanged_after_replay ✓              cleanup_ok ✓
ledger_single_row_for_daily_key ✓
client_token_cannot_bypass_daily_idempotency ✓
next_day_simulation_grants_new_claim ✓
psp_balance_doubled_after_next_day_claim ✓
next_day_same_day_replay_idempotent ✓
```

Verifiche chiave:
- **First claim**: PSP.mission_coins=10, honor=5; ledger row con claim_key correto; `live_grant=true`; `account_wide={}`
- **Replay same day** (anche con diverso `client_token`): `idempotent_replay=true`, ledger count=1, PSP balance unchanged
- **Next-day override**: `_test_day_override=<tomorrow>` su utente marked → nuovo claim, PSP balance doppia (`mission_coins=20, honor=10`)
- **Same next-day replay**: idempotent
- **Cross-server isolation**: server B con PSP fresca → claim indipendente (sid_b granted, sid_a unchanged)
- **Day override forbidden** su utente NON marcato → 403 `DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER`
- **Premium block (Pack 96)**: payload `{gems: 100}` su qa source → 422 preserved
- **Kill switch lifecycle clean**: ripristinato OFF dopo smoke

## Static Daily Anti-Double-Claim Guard

(validator `validate_v110_pack_97_static_daily_anti_double_claim_guard.py`)

- ❌ `db.users.update_one` ASSENTE dal claim block
- ❌ hardcoded `"s1"` / `'s1'` ASSENTI
- ✅ `db.player_server_profiles.update_one` PRESENTE (PSP-only write)
- ✅ Entrambi kill switch checked AND (`_global_kill_switch_on` + `_daily_kill_switch_on`)
- ✅ `compute_daily_claim_key` + `derive_idempotency_token_from_claim_key` invocati server-side
- ✅ Replay check `find_one` precede `grant_fn()`
- ✅ `pack_97_test_artifact` marker check su `_test_day_override`
- ✅ Nessuna source live banned in registry (`mail/achievements/battlepass/event/afk_reward_claim` ASSENTI)

## Legacy Claim Non-Regression

(file: `v110_pack_97_legacy_claim_non_regression_v1.json` + runtime verify)

- **Only new real source**: `daily_login_claim`
- ❌ mail / achievements / battlepass / event / AFK / shop claim NOT LIVE
- ✅ Pack 95 story strict preserved (smoke proof)
- ✅ Pack 95 shops/buy + soul-forge/retire quarantine preserved (smoke proof)
- ✅ Pack 94 equipment strict + earn-pvp/earn-guild quarantine preserved
- ✅ Pack 93 wallet split preserved
- ✅ Pack 91 inventory preserved
- ✅ Live sources count = 3 (qa, story_marker, daily_login)

## Data Invariants

- ✅ no_production_broad_grants
- ✅ no_unmarked_test_writes
- ✅ no_premium_hard_currency_grants
- ✅ reward_live_general = **false**
- ✅ no_gacha_iap_changes
- ✅ no_legacy_cleanup_general_execute
- ✅ no_destructive_migration
- ✅ pack_84_through_96_preserved

## Cleanup / Rollback

Script: `backend/scripts/cleanup_v110_pack_97_test_artifacts.py`

- **Refuse-by-default** dry-run; `--apply` required
- Marker required: `pack_97_test_artifact=true`
- Flag `--reset-kill-switches` rimuove entrambe `REWARD_CLAIM_LEDGER_LIVE_ENABLED` e `DAILY_LOGIN_CLAIM_ENABLED` dal `.env`
- Mai tocca dati produzione (refuse senza marker)

## Live Readiness Update

| Flag | Valore |
|------|--------|
| `daily_login_claim_ready` | **true** |
| `daily_login_claim_live_enabled_default` | **false** ⚠️ |
| `global_reward_kill_switch_default` | **false** |
| `and_logic_required` | **true** |
| `first_real_player_facing_source_added` | **`daily_login_claim`** |
| `only_one_new_player_facing_source_in_pack_97` | **true** |
| `reward_live_general` | **false** |
| `premium_grants` | **false** |
| `mail_claim_live` | **false** |
| `achievements_claim_live` | **false** |
| `battlepass_claim_live` | **false** |
| `afk_claim_live` | **false** |
| `event_claim_live` | **false** |
| `shop_claim_live` | **false** |
| `release_readiness_claimed` | **false** |

## MD5 Rebase

Files added: 3 (1 backend route, 2 frontend files) + 1 SOT doc.
Files modified: 3 (registry, init, game_systems) + 1 validator relax + 1 suite registration.
No validator weakening. Baseline signature preserved (1557→1574 = +17 PASS only).

## Gate Preservation

Tutti i pack 84–96 preservati (Pack 95 story strict, Pack 95 legacy quarantine, Pack 96 reward_claim endpoint + qa/story_marker sources + premium block). POSTQA_D locked. Battle engine unchanged. `/api/battle/simulate` NOT called from staging/live. `story.tsx` / `combat.tsx` unchanged.

## Explicit Statements

### daily_login_claim live/ready status

✅ **READY**. Endpoint `/api/daily-login/claim` operativo. Live execution **gated by AND di 2 kill switches default OFF**. Quando entrambi su `true` (test/local override), claim funziona con server-side deterministic claim_key + unique index DB-level + ledger replay-safe.

### Reward live general remains false

✅ **Confermato.** `reward_live_general=false` in summary, in live_readiness, e nell'output di ogni claim response. Nessuna source player-facing diversa da `daily_login_claim` attivata.

### No premium / hard currency grants

✅ **Confermato.** `gems`, `premium_pull`, `standard_pull` in `FORBIDDEN_REWARD_TYPES`. Daily reward fisso a `mission_coins/honor` solo. Cap 100/chiave. Premium attempt sul reward_claim Pack 96 endpoint resta bloccato.

### No double daily reward

✅ **Confermato.** 
- Server-side claim_key deterministico (client non puo' influenzare)
- Replay check via `find_one` su `(user_id, server_id, claim_source, claim_key)`
- Unique partial index DB-level garantisce protezione race
- Smoke E2E proof: 4 chiamate stesso giorno → 1 ledger row, PSP balance invariata

### Only daily source added as real player-facing source

✅ **Confermato.** Live sources post Pack 97: `qa_controlled_soft_currency_claim` (test/QA), `story_progress_marker_claim` (marker, no reward), **`daily_login_claim`** (Pack 97 nuovo, real player-facing). Nessuna altra real source player-facing è stata abilitata.

### Pack 91/93/94/95/96 preserved

✅ **Confermato** via smoke E2E:
- `pack_91_inventory_preserved` (loader filter_applied)
- `pack_93_wallet_split_preserved` (`wallet_source=psp_server_scoped_split`)
- `pack_94_equipment_loader_preserved` (`filter_applied=true`)
- `pack_95_story_strict_preserved` (`pack_95_strict_story_progress_write=true`)
- `pack_95_shops_buy_quarantine_preserved` (`SHOPS_BUY_SERVER_SCOPE_DEFERRED`)
- `pack_96_premium_block_preserved` (`PREMIUM_GRANT_BLOCKED` su `{gems:100}`)

## Deferred Blockers

1. **Reward live activation generale** (richiede approval distinta)
2. **Mail / Achievements / Battlepass / AFK / Event / Shop reward claim sources** — ogni source richiede dedicated allowlisting + smoke E2E
3. **Frontend home unlock** — `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=true` + embed sulla home
4. **Shops buy strict server-scoped execute** — `AUTORIZZO_V110_SHOPS_BUY_STRICT_SCOPE_EXECUTE`
5. **Soul forge retire strict server-scoped execute** — `AUTORIZZO_V110_SOUL_FORGE_RETIRE_STRICT_SCOPE_EXECUTE`
6. **Forge upgrade/fuse endpoints** (non implementati)
7. **Frontend equipment UI POSTQA_D unlock**
8. **Legacy cleanup pre-Pack-86 user_heroes**

## Next Step

Attendo conferma utente. Pack 98 NON avviato come richiesto.

Suggerito ordine di priorità per il prossimo pack:

1. **P0** — Frontend home unlock daily login (`EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=true` + integrare componente sulla home dietro flag)
2. **P0** — Seconda real source low-risk (es. `daily_quest_completion_claim` con stesso pattern di Pack 97)
3. **P1** — Mail rewards live source (richiede design ledger per `mail_id` come instance)
4. **P1** — Shops buy / Soul forge retire strict execute
5. **P2** — Achievements / Battlepass reward sources

## Sync Status

```json
{
  "local_commit_only": true,
  "public_push_managed_externally": true,
  "no_remote_available": true,
  "commit_hash_primary": "8bc44e5ce0199185de4208f3a41bee9289706dbf"
}
```
