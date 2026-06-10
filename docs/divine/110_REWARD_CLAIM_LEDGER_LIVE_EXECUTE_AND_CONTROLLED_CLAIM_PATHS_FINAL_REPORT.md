# MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS — FINAL REPORT

> Sentinel: `PUBLIC_SYNC_TAG_v110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS`
> Approval ricevuta: `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_PACK_96`

## Verdict

**`MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

## Commit Hash

- Code + design + validators + smoke: `5c22033c8ca52de13dd1e95366a401687e252fee`
- Final report + multirun result update: see footer commit.

`local_commit_only=true` — nessun remote git esterno disponibile in questo container.

## Git Diff Stat

Files added/modified (cumulato sul commit Pack 96):

```
backend/utils/reward_source_registry.py        | NEW (180+ lines)
backend/routes/reward_claim.py                 | NEW (220+ lines)
backend/routes/__init__.py                     | MOD (+2 lines)
backend/game_systems.py                        | MOD (+5 lines)
backend/scripts/smoke_v110_pack_96_*.py        | NEW
backend/scripts/cleanup_v110_pack_96_*.py      | NEW
backend/scripts/validate_v110_pack_96_*.py     | NEW × 17
backend/scripts/validate_mega_release_accel_96_*.py | NEW (rollup)
backend/scripts/run_hero_skill_kit_validator_suite.py | MOD (+18 suite tuples)
data/design/v110_pack_96_reward_claim_ledger_live_execute/*.json | NEW × 16
```

## Baseline / Final Suite

| Run | Pass | Fail | Miss | Note |
|-----|-----:|-----:|-----:|------|
| Baseline pre #1 | 1539 | 34 | 0 | pre Pack 96 |
| Baseline pre #2 | 1539 | 34 | 0 | deterministic |
| Baseline pre #3 | 1539 | 34 | 0 | deterministic |
| Final post #1 | **1557** | **34** | **0** | post Pack 96 |
| Final post #2 | **1557** | **34** | **0** | deterministic |
| Final post #3 | **1557** | **34** | **0** | deterministic |

**Delta: +18 PASS, 0 nuovi FAIL, 0 MISS.** Nessun validator weakening.

> Nota di onestà: durante l'iter di sviluppo è stata osservata una flake di un validator pre-esistente (`PROJECT-N-TRACK-D-CANARY-LIGHT-LOAD-STABILITY`) che dipende da timing p99 e può fallire quando il container ha background load (verificato 1 fallimento su 5 run intermedi). NON è regressione Pack 96 (passa pulito nei 3 final post runs). Nessun fake_PASS, nessun validator weakening.

## Reward Ledger Live Preflight

(file: `v110_pack_96_reward_ledger_live_preflight_v1.json`)

- Collection: **`reward_claim_ledger`**
- Unique index: **`ux_user_server_idem_token_pack96`** su `(user_id, server_id, idempotency_token)` — `unique=True, background=True`
- Secondary index: **`ix_applied_at_pack96`** su `(applied_at)`
- Creation **idempotente** (MongoDB no-op se esiste). **Nessun drop distruttivo.** In caso di duplicati pre-esistenti → `stopped=true` con error propagato.
- Kill switch env: **`REWARD_CLAIM_LEDGER_LIVE_ENABLED`**, **default OFF** (per richiesta utente safety).
- Endpoint preflight: `POST /api/rewards/claim/preflight` (auth richiesta). Esegue index ensure + ritorna `live_enabled`, `registry_size`, `allowlisted_sources`, `forbidden_reward_types`. NESSUN grant durante preflight.
- Endpoint health: `GET /api/rewards/claim/health` (pubblico, read-only).

## Reward Source Registry

(file: `backend/utils/reward_source_registry.py` + `v110_pack_96_reward_source_registry_v1.json`)

| Source | live | server_scoped | grant_fn | reward_types | pack_origin |
|--------|:---:|:---:|---|---|:---:|
| `qa_controlled_soft_currency_claim` | true | true | `grant_soft_currency_to_psp` (PSP.soft_currencies $inc) | gold, honor, guild_points, mission_coins, dimension_frags, prana, soul_seals, star_dust | pack_96 |
| `story_progress_marker_claim` | true | true | `grant_noop` | — (nessun reward) | pack_96 |

**Forbidden reward types** (ban categorico, controllo pre-grant):
- `gems` (premium currency)
- `premium_pull`, `standard_pull` (gacha)
- `stamina`, `experience` (account-wide)

**Per-call amount cap**: 10000 per chiave (sanity bound test). Importi ≤0 o >10000 → `REWARD_TYPE_NOT_ALLOWED`.

## Controlled Claim Endpoint

(file: `backend/routes/reward_claim.py` + `v110_pack_96_controlled_claim_endpoint_v1.json`)

`POST /api/rewards/claim?server_id=<sid>` body `{source, reward_instance_id, idempotency_token, payload?}`

Flow strict (ordine guard pre-grant):
1. **Kill switch check** → 503 `REWARD_CLAIM_LEDGER_LIVE_DISABLED` se OFF (default)
2. **server_id check** → 400 `SERVER_ID_REQUIRED`
3. **PSP check** → 409 `PLAYER_SERVER_PROFILE_REQUIRED`
4. **idempotency_token check** → 400 `IDEMPOTENCY_TOKEN_REQUIRED` (min 8 char)
5. **Source registry lookup** → 422 `REWARD_SOURCE_NOT_ALLOWLISTED` / `REWARD_SOURCE_NOT_LIVE`
6. **Replay check** (find_one su `reward_claim_ledger`) → ritorna receipt esistente senza secondo grant
7. **Premium pre-grant block** → 422 `PREMIUM_GRANT_BLOCKED` (per chiavi in `FORBIDDEN_REWARD_TYPES`)
8. **Grant fn invocation** → su `player_server_profiles.soft_currencies.*` (SOLO), atomic `$inc`
9. **Ledger insert** (con audit fields `_slc_pack_96_*` + `_slc_pack_95_reward_claim_ledger`)

Race protection: se unique index hits in insert dopo grant → compensating reverse `$inc` + return replay receipt.

## First Controlled Claim Sources

(file: `v110_pack_96_first_controlled_claim_sources_v1.json`)

- **2** source live in Pack 96: `qa_controlled_soft_currency_claim`, `story_progress_marker_claim`.
- Tutte server-scoped + idempotency mandatory.
- **Nessuna source reale player-facing live in Pack 96** (mail/achievements/daily/battlepass/afk/event differiti a pack futuri).

## Grant Engine Guard

(file: `v110_pack_96_grant_engine_guard_v1.json`)

- **Targets ammessi**: `player_server_profiles.soft_currencies.*`
- **Targets vietati**: `users.gold`, `users.gems`, `users.experience`, `users.stamina`, hero/equipment/inventory diretti
- **Premium pre-grant block**: ✅ (test statico + smoke E2E provano `PREMIUM_GRANT_BLOCKED` per `{gems: 100}`)
- **Per-amount cap**: 10000; lower bound: 1
- **Unknown reward types**: blocked con `REWARD_TYPE_NOT_ALLOWED`

## Legacy Claim Bridge Guards

(file: `v110_pack_96_legacy_claim_bridge_guards_v1.json`)

| Endpoint legacy | Stato post Pack 96 |
|---|---|
| `/api/currency/earn-mission` | Pack 95 quarantine preserved |
| `/api/currency/earn-dimension` | Pack 95 quarantine preserved |
| `/api/currency/earn-pvp` | Pack 94 quarantine preserved |
| `/api/currency/earn-guild` | Pack 94 quarantine preserved |
| `/api/shops/buy` | Pack 95 quarantine preserved |
| `/api/soul-forge/retire` | Pack 95 quarantine preserved |
| `/api/story/battle` | Pack 95 strict server-scope preserved |

**No legacy bypass without ledger.** Tutte le future grant active devono routare via `/api/rewards/claim`.

## Frontend Consumer Guard

(file: `v110_pack_96_frontend_consumer_guard_v1.json`)

- Frontend NON cablato su `/api/rewards/claim` in Pack 96.
- Endpoint live-gated; UI consumer attivazione richiede `AUTORIZZO_V110_REWARD_CLAIM_FRONTEND_UNLOCK` (futuro pack).
- ❌ no false_success_on_blocker  ❌ no silent s1 for claim paths

## Runtime Smoke E2E

Script: `backend/scripts/smoke_v110_pack_96_reward_ledger_live_e2e.py`
Marker: `pack_96_test_artifact=true`. Utenti: `pack96_test_user_<ts>@test.com`.

**Risultato: 25/25 proof verde + cleanup confermato**

```
kill_switch_default_off ✓                        first_controlled_claim_success ✓
register_ok ✓                                    replay_returns_idempotent_no_double_grant ✓
ensure_psp_a_ok ✓                                ledger_single_row_after_replay ✓
mark_pack_96_ok ✓                                psp_balance_unchanged_after_replay ✓
kill_switch_blocks_when_off ✓                    same_source_different_token_grants_again ✓
kill_switch_enable_for_test_ok ✓                 unknown_source_blocked ✓
preflight_index_creation_safe_idempotent_1 ✓     premium_grant_blocked ✓
preflight_index_creation_idempotent_2 ✓          no_ledger_row_for_premium_attempt ✓
story_marker_claim_noop_success ✓                cross_server_no_leak_psp_required ✓
pack_95_story_strict_preserved ✓                 pack_95_shops_buy_quarantine_preserved ✓
pack_94_equipment_loader_preserved ✓             pack_93_wallet_split_preserved ✓
kill_switch_disable_re_blocks_correctly ✓        kill_switch_restored_to_original ✓
cleanup_ok ✓
```

Verifiche chiave:
- **First claim live**: `qa_controlled_soft_currency_claim` con payload `{gold: 50, honor: 5}` → success, ledger row con `live_grant=true`, PSP.soft_currencies popolato esattamente coi valori.
- **Replay**: stesso `idempotency_token` → `idempotent_replay: true`, ledger count = 1, PSP balance unchanged.
- **Different token, same source**: ledger count = 2, PSP.gold = 75 (50 + 25), conferma multi-claim funziona.
- **Unknown source**: 422 `REWARD_SOURCE_NOT_ALLOWLISTED`.
- **Premium attempt** (`{gems: 100}`): 422 `PREMIUM_GRANT_BLOCKED`, **0 ledger row creato**, `users.gems` mai mutato.
- **Cross-server** (server B no PSP): 409.
- **Kill switch lifecycle**: OFF default → 503 → smoke enable → claims work → smoke disable → 503 again → finally restored to OFF (env var rimossa).

## Static Anti-Bypass Guard

(file: `v110_pack_96_static_anti_bypass_guard_v1.json`)

Check statici eseguiti dal validator `validate_v110_pack_96_static_anti_bypass_guard.py`:

- ✅ Kill switch default = `"false"` in source
- ✅ `PLAYER_SERVER_PROFILE_REQUIRED` enforcement pre-grant
- ✅ `IDEMPOTENCY_TOKEN_REQUIRED` enforcement pre-grant
- ✅ `lookup_source` + `REWARD_SOURCE_NOT_ALLOWLISTED` pre-grant
- ✅ Replay check `find_one` precede `grant_fn` call (verificato per `claim_block.index()`)
- ✅ `PREMIUM_GRANT_BLOCKED` precede `grant_fn` call
- ❌ `db.users.update_one` ASSENTE dal claim block
- ❌ hardcoded `"s1"` / `'s1'` ASSENTI dal claim block
- ✅ `db.player_server_profiles.update_one` PRESENTE (PSP-only target)

## Index / Ledger Migration Safety

(file: `v110_pack_96_index_ledger_migration_safety_v1.json`)

- 2 index gestiti (unique + secondary), entrambi con `background=True` e `idempotent_creation=true`.
- ❌ NO `drop_index` / `dropIndex` nel codice.
- DuplicateKey hits in insert → compensating reverse `$inc` + return replay receipt (no double grant, no inconsistency).

## Data Invariants

(file: `v110_pack_96_data_invariants_v1.json`)

- ✅ no_production_user_writes
- ✅ no_unmarked_test_writes
- ✅ no_premium_hard_currency_grants
- ✅ no_reward_live_general
- ✅ no_legacy_cleanup_general_execute
- ✅ no_destructive_migration
- ✅ no_broad_db_writes
- ✅ pack_84_through_95_preserved (verificato via smoke)
- ✅ test_artifact_marker_required = `pack_96_test_artifact`

## Cleanup / Rollback / Kill Switch

Script: `backend/scripts/cleanup_v110_pack_96_test_artifacts.py`

- **Refuse by default**: dry-run senza `--apply`.
- Marker required: `pack_96_test_artifact=true`.
- Flag aggiuntivo `--reset-kill-switch` rimuove `REWARD_CLAIM_LEDGER_LIVE_ENABLED` da `/app/backend/.env`.
- Kill switch disable procedure: rimuovere/settare `false` la env var + restart backend → endpoint 503 `REWARD_CLAIM_LEDGER_LIVE_DISABLED`.
- Per disabilitare singola source (rollback granulare): settare `.live = False` in `REWARD_SOURCE_REGISTRY` — ledger entries esistenti restano.

## Live Readiness Update

(file: `v110_pack_96_live_readiness_update_v1.json`)

| Flag | Valore |
|------|--------|
| `reward_ledger_live_ready` | **true** |
| `reward_ledger_live_enabled_default` | **false** ⚠️ (kill switch default OFF su mandato utente) |
| `controlled_claim_paths_ready` | **true** |
| `controlled_claim_paths_live_sources` | `["qa_controlled_soft_currency_claim", "story_progress_marker_claim"]` |
| `reward_live_general` | **false** |
| `premium_grants` | **false** |
| `mail_claim_live` | **false** |
| `achievements_claim_live` | **false** |
| `daily_claim_live` | **false** |
| `battlepass_claim_live` | **false** |
| `afk_claim_live` | **false** |
| `event_claim_live` | **false** |
| `wallet_spend_ledger_live_pack_93_preserved` | **true** |
| `equipment_strict_pack_94_preserved` | **true** |
| `story_strict_pack_95_preserved` | **true** |
| `legacy_quarantine_pack_94_95_preserved` | **true** |
| `release_readiness_claimed` | **false** |

## MD5 Rebase

(file: `v110_pack_96_md5_rebase_v1.json`)

File nuovi (added): `backend/utils/reward_source_registry.py`, `backend/routes/reward_claim.py`
File modificati (minimal wiring): `backend/routes/__init__.py`, `backend/game_systems.py`
Suite touched: solo aggiunta tuple Pack 96 (18 nuove entry), nessun validator weakening.

## Gate Preservation

(file: `v110_pack_96_gate_invariant_preservation_v1.json`)

Tutti i pack 84–95 preservati:
- ✅ Pack 84–93 (PSP normalization, onboarding, lobby ensure, server-scoped starter, team formation, inventory PSP-scoped/strict/frontend, core server scope, economy progress)
- ✅ Pack 94 equipment strict + legacy earn-pvp/earn-guild quarantine
- ✅ Pack 95 story strict + reward claim ledger foundation + legacy quarantine
- ✅ POSTQA_D gates locked, battle_engine unchanged, `/api/battle/simulate` NOT called from staging/live, story.tsx/combat.tsx unchanged

## Explicit Statements

### Reward ledger live status

✅ **Live infrastructure READY**. Endpoint `/api/rewards/claim` operativo, unique index idempotente, replay-safe. **Kill switch default OFF** per safety user-mandated; endpoint risponde 503 finché env var non viene attivata esplicitamente per contesti test/guarded.

### Controlled claim paths live status

✅ **2 source allowlisted live** in Pack 96 (`qa_controlled_soft_currency_claim`, `story_progress_marker_claim`). Tutte server-scoped + idempotency mandatory. Nessuna source reale player-facing in questo pack.

### Reward live generale remains false

✅ **Confermato.** Nessuna source player-facing reale attivata. Mail/Achievements/Daily/Battlepass/AFK/Event/Shop/Battle claim path NON LIVE. `reward_live_general=false` in registry e in live_readiness.

### No premium / hard currency grants

✅ **Confermato.** `gems`, `premium_pull`, `standard_pull` in `FORBIDDEN_REWARD_TYPES`. Pre-grant check + grant_fn raise + smoke E2E (proof `premium_grant_blocked` + `no_ledger_row_for_premium_attempt`).

### No double reward grant

✅ **Confermato.** Replay via unique index `(user_id, server_id, idempotency_token)` + find_one pre-grant + smoke proof `ledger_single_row_after_replay` + `psp_balance_unchanged_after_replay`. Race compensation con reverse `$inc` se unique key hit in insert.

### Pack 91 / 93 / 94 / 95 preserved

✅ **Confermato** via smoke E2E proofs:
- `pack_95_story_strict_preserved` (chapter battle con server_id + idempotency_token funziona, `pack_95_strict_story_progress_write: true`)
- `pack_95_shops_buy_quarantine_preserved` (blocker `SHOPS_BUY_SERVER_SCOPE_DEFERRED`)
- `pack_94_equipment_loader_preserved` (`filter_applied: true`)
- `pack_93_wallet_split_preserved` (`wallet_source: psp_server_scoped_split`)

## Deferred Blockers

1. **Reward live activation generale** (richiede approval futura distinta da Pack 96)
2. **Real player-facing claim sources** (mail/achievements/daily/battlepass/afk/event) — richiedono allowlisting + smoke E2E aggiuntivi per ogni source
3. **Frontend reward claim consumer UI unlock** — `AUTORIZZO_V110_REWARD_CLAIM_FRONTEND_UNLOCK`
4. **Shops buy strict server-scoped execute** — `AUTORIZZO_V110_SHOPS_BUY_STRICT_SCOPE_EXECUTE`
5. **Soul forge retire strict server-scoped execute** — `AUTORIZZO_V110_SOUL_FORGE_RETIRE_STRICT_SCOPE_EXECUTE`
6. **Forge upgrade/fuse endpoints** (non implementati)
7. **Frontend equipment UI POSTQA_D unlock** (NON eseguito)
8. **Legacy cleanup pre-Pack-86 user_heroes** (deferito)

## Next Step

Attendo conferma utente. Pack 97 NON avviato come richiesto.

Quando vorrai procedere, indica quale dei deferred blockers autorizzare. Suggerito ordine di priorità:

1. **P0** — Prima real player-facing claim source allowlisting (es. `mail_reward_claim` o `daily_login_claim`) con smoke E2E dedicato
2. **P1** — Shops buy / Soul forge retire strict execute (per chiudere il loop economy)
3. **P2** — Frontend reward claim consumer UI (`AUTORIZZO_V110_REWARD_CLAIM_FRONTEND_UNLOCK`)
4. **P2** — Frontend equipment UI POSTQA_D unlock
5. **P3** — Forge upgrade/fuse endpoints + legacy cleanup pre-Pack-86

## Sync Status

```json
{
  "local_commit_only": true,
  "public_push_managed_externally": true,
  "no_remote_available": true,
  "commit_hash_primary": "5c22033c8ca52de13dd1e95366a401687e252fee"
}
```
