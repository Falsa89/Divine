# MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK — FINAL REPORT

> Sentinel: `PUBLIC_SYNC_TAG_v110_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK`
> Approval ricevuta: `AUTORIZZO_V110_REWARD_LEDGER_STORY_WRITE_LEGACY_GUARDS_TEST_ONLY_PACK_95`

## Verdict

**`MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

## Commit Hash

`cc8049093284343dc1c2d5c291867dda3c27992c`

`local_commit_only=true` — nessun remote git esterno disponibile in questo container; sync pubblico gestito esternamente.

## Git Diff Stat

```
218 files changed, 1253 insertions(+), 211 deletions(-)
```

File runtime mutati: 2 (`backend/routes/combat.py`, `backend/routes/soul_forge.py`).
File suite mutati: 1 (`backend/scripts/run_hero_skill_kit_validator_suite.py` — solo aggiunta tuple Pack 95, nessun validator weakening).
File nuovi: 17 validator + 1 smoke + 1 cleanup + 1 rollup + 15 design JSON Pack 95.

## Baseline / Final Suite

| Run | Pass | Fail | Miss | Note |
|-----|-----:|-----:|-----:|------|
| Baseline pre #1 | 1522 | 34 | 0 | pre Pack 95 |
| Baseline pre #2 | 1522 | 34 | 0 | deterministic |
| Baseline pre #3 | 1522 | 34 | 0 | deterministic |
| Final post #1 | **1539** | **34** | **0** | post Pack 95 |
| Final post #2 | **1539** | **34** | **0** | deterministic |
| Final post #3 | **1539** | **34** | **0** | deterministic |

**Delta: +17 PASS, 0 nuovi FAIL, 0 MISS.** Nessun validator weakening.

> Nota: il baseline reale (1522/34/0) differiva leggermente dall'approssimazione dell'handoff (~1527/29/0). I 3 run consecutivi pre-Pack-95 hanno restituito `1522/34/0` invariato, confermando determinismo. Pack 95 ha aggiunto 17 validator nuovi tutti PASS senza toccare il resto.

## Reward / Legacy Write Path Audit

(file: `data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_write_path_audit_v1.json`)

| Endpoint | Stato pre Pack 95 | Stato post Pack 95 |
|----------|-------------------|--------------------|
| `POST /api/story/battle` | server_id-aware con blocker `STORY_PROGRESS_WRITE_SERVER_SCOPE_DEFERRED` | **STRICT server-scoped write** (PSP required, idempotency_token required, ledger replay-safe, NO grant) |
| `POST /api/currency/earn-mission` | account-wide, nessun guard | **server_id-aware → blocker `LEGACY_CURRENCY_QUARANTINE_DEFERRED`** |
| `POST /api/currency/earn-dimension` | account-wide, nessun guard | **server_id-aware → blocker `LEGACY_CURRENCY_QUARANTINE_DEFERRED`** |
| `POST /api/currency/earn-pvp` | quarantine Pack 94 | preservato (no regressione) |
| `POST /api/currency/earn-guild` | quarantine Pack 94 | preservato (no regressione) |
| `POST /api/shops/buy` | account-wide, nessun guard | **server_id-aware → blocker `SHOPS_BUY_SERVER_SCOPE_DEFERRED`** |
| `POST /api/soul-forge/retire` | cross-collection write, nessun guard | **server_id-aware → blocker `SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED`** |
| `POST /api/wallet/spend` | Pack 93 strict | preservato (no regressione) |

## Reward Claim Ledger Runtime Foundation

(file: `v110_pack_95_reward_claim_ledger_runtime_foundation_v1.json`)

- Collection: **`reward_claim_ledger`**
- Idempotency key: `(user_id, server_id, idempotency_token)`
- Audit fields: `id, user_id, server_id, claim_source, claim_key, idempotency_token, rewards, victory, applied_at, _slc_pack_95_reward_claim_ledger, _slc_pack_95_no_live_grant`
- **Replay-safe**: `find_one({user_id, server_id, idempotency_token})` prima di insert; nessun doppio grant possibile.
- **No reward live by default**: `rewards.server_scoped = {}`, `rewards.account_wide = {}`, `rewards.live_grant = false`.
- **Claim sources implementate**: `story`. Documentate per futuri pack: `mail, achievements, daily, battlepass, shop, battle, afk, event`.
- Index creation runtime: **OFF** (Pack 95 NON forza index creation per evitare schema drift in produzione; safety garantita dal check find_one).
- Approval per live grant: `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE` (NON ricevuta in Pack 95).

## Story Progress Write Strict Result

(file: `v110_pack_95_story_progress_write_strict_v1.json`)

- Endpoint: `POST /api/story/battle?server_id=<sid>&idempotency_token=<tok>`
- **server_id required + PSP check** (409 `PLAYER_SERVER_PROFILE_REQUIRED` se manca)
- **idempotency_token required** (>= 8 char, 400 `IDEMPOTENCY_TOKEN_REQUIRED` se manca)
- Replay check via `reward_claim_ledger`: stessa token → `idempotent_replay: true` senza secondo write.
- Write target: **SOLO** `player_server_profiles.story_progress.{completed, current_chapter, current_stage}`. NESSUN write a `users.story_progress` (legacy account-wide).
- **NESSUN grant**: nessun `$inc` su `users.gold/gems`, nessun item drop, nessun reward currency.
- Verificato static + runtime: smoke E2E conferma single-ledger-row-per-token e cross-server isolation (server B → 409).
- Legacy path (no server_id) invariato.

## Legacy Currency Earn Quarantine

(file: `v110_pack_95_legacy_currency_quarantine_v1.json`)

| Endpoint | Pack 95 |
|----------|---------|
| `/api/currency/earn-mission` | aggiunto `server_id` param → blocker `LEGACY_CURRENCY_QUARANTINE_DEFERRED` se server_id presente |
| `/api/currency/earn-dimension` | aggiunto `server_id` param → blocker `LEGACY_CURRENCY_QUARANTINE_DEFERRED` se server_id presente |
| `/api/currency/earn-pvp` | quarantine Pack 94 preservata |
| `/api/currency/earn-guild` | quarantine Pack 94 preservata |

Path legacy (no server_id) invariato in tutti e 4 gli endpoint. Nessun `users.gold/gems` grant per server-bound rewards. Nessun hardcoded `s1` in attive player-facing path quando `server_id` presente.

## Shops Buy Guard

(file: `v110_pack_95_shops_buy_guard_v1.json`)

- Endpoint: `/api/shops/buy?server_id=<sid>` → blocker `SHOPS_BUY_SERVER_SCOPE_DEFERRED`
- Reason: muta `users.gold/gems + db.wallets + db.user_materials + db.user_fragments` account-wide; promotion strict richiede `wallet_spend_ledger` + `reward_claim_ledger` live (non attivati in Pack 95).
- Legacy (no server_id) invariato.
- Approval proposto per promotion: `AUTORIZZO_V110_SHOPS_BUY_STRICT_SCOPE_EXECUTE`.

## Soul Forge Retire Guard

(file: `v110_pack_95_soul_forge_retire_guard_v1.json`)

- Endpoint: `/api/soul-forge/retire?server_id=<sid>` → blocker `SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED`
- Reason: muta `user_heroes/user_equipment/user_runes/wallets` cross-collection; server-scoped richiede hero selector strict server-bound + reward claim ledger live.
- Nessuna distruzione cross-server di hero.
- Legacy (no server_id) invariato.
- Approval proposto per promotion: `AUTORIZZO_V110_SOUL_FORGE_RETIRE_STRICT_SCOPE_EXECUTE`.

## Frontend Consumer Guard

(file: `v110_pack_95_frontend_consumer_guard_v1.json`)

- Strict consumer già passing server_id: `/api/user/equipment, /api/wallet, /api/inventory`.
- Endpoint con Pack 95 blocker (nessun silent s1): `/api/shops/buy, /api/soul-forge/retire, /api/currency/earn-mission, /api/currency/earn-dimension`.
- Story battle frontend consumer: **UI promotion strict NON eseguita in Pack 95** (deferita; approval futura `AUTORIZZO_V110_STORY_PROGRESS_FRONTEND_UNLOCK`).
- `no_false_success_on_blocker = true`, `no_silent_s1_for_server_bound_paths = true`.

## Runtime Smoke E2E

Script: `backend/scripts/smoke_v110_pack_95_reward_story_legacy_e2e.py`
Marker: `pack_95_test_artifact=true`. Utenti: `pack95_test_user_<ts>@test.com`.

Risultato (25/25 proof verde + cleanup):

```
register_ok ✓                                  story_write_strict_no_currency_grant ✓
ensure_psp_a_ok ✓                              story_write_strict_cross_server_isolation ✓
mark_pack_95_ok ✓                              story_write_strict_psp_story_progress_advanced ✓
story_battle_legacy_path_unchanged ✓           earn_mission_quarantine_when_server_id ✓
story_write_strict_requires_idempotency_token  earn_dimension_quarantine_when_server_id ✓
story_write_strict_unknown_server_psp_required earn_pvp_quarantine_pack_94_preserved ✓
story_write_strict_first_call_ok ✓             earn_guild_quarantine_pack_94_preserved ✓
story_write_strict_idempotent_replay_no_double earn_mission_legacy_path_unchanged_no_serverid
reward_claim_ledger_single_entry_per_token ✓   earn_dimension_legacy_path_unchanged_no_serverid
shops_buy_quarantine_when_server_id ✓          soul_forge_retire_quarantine_when_server_id ✓
pack_92_wallet_split_preserved ✓               pack_94_equipment_loader_strict_preserved ✓
pack_90_buy_strict_preserved ✓                 no_account_wide_leak_smoke_path ✓
cleanup_ok ✓
```

Verifiche chiave:
- Single ledger row per token (no double grant)
- `rewards.live_grant = false`, `rewards.server_scoped = {}`, `rewards.account_wide = {}`
- Cross-server (server B no PSP) → 409
- PSP.story_progress advanced (current_chapter ≥ 1)
- Cleanup verificato: utente + PSP + wallet + ledger rimossi correttamente.

## Static Anti Double-Grant Guard

(file: `v110_pack_95_static_anti_double_grant_guard_v1.json`)

Check statici eseguiti dal validator `validate_v110_pack_95_static_anti_double_grant_guard.py`:

- Strict path di `/api/story/battle` (branch `if server_id`):
  - ❌ `db.users.update_one` NON presente
  - ❌ `db.story_progress` NON presente (no legacy account-wide write)
  - ❌ `"s1"` / `'s1'` NON presente (no hardcoded server_id)
  - ✓ `reward_claim_ledger` insert presente
  - ✓ `IDEMPOTENCY_TOKEN_REQUIRED` enforcement presente
- `soul_forge.py`:
  - ✓ `LEGACY_CURRENCY_QUARANTINE_DEFERRED` presente
  - ✓ `SHOPS_BUY_SERVER_SCOPE_DEFERRED` presente
  - ✓ `SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED` presente
  - ✓ Tutti gli endpoint `earn-mission, earn-dimension, earn-pvp, earn-guild` server_id-aware

## Data Invariants

(file: `v110_pack_95_data_invariants_v1.json`)

- ✅ no_production_user_writes
- ✅ no_unmarked_test_writes
- ✅ no_premium_hard_currency_grants
- ✅ no_reward_live
- ✅ no_legacy_cleanup_general_execute
- ✅ no_destructive_migration
- ✅ no_broad_db_writes
- ✅ pack_84_through_94_preserved (incluso `pack_94_legacy_earn_pvp_guild_quarantine_preserved`)
- ✅ test_artifact_marker_required = `pack_95_test_artifact`

## Cleanup / Rollback

Script: `backend/scripts/cleanup_v110_pack_95_test_artifacts.py`

- **Refuse by default**: senza `--apply` esegue dry-run e stampa solo counts.
- Marker required: `pack_95_test_artifact=true`. Mai tocca dati produzione.
- Collezioni gestite: `users, player_server_profiles, user_heroes, user_equipment, inventory, wallets, reward_claim_ledger, story_progress, retirement_history, shop_purchases_special`.
- Dry-run eseguito post-smoke: 0 documenti residui (smoke fa cleanup in finally).

## Live Readiness Update

(file: `v110_pack_95_live_readiness_update_v1.json`)

| Flag | Valore |
|------|--------|
| `reward_ledger_foundation_ready` | **true** |
| `reward_ledger_live` | **false** |
| `story_progress_write_guard_ready` | **true** |
| `story_progress_write_strict_test_only_safe` | **true** |
| `story_progress_write_grants_live_currency` | **false** |
| `legacy_guards_ready` | **true** |
| `earn_mission_quarantine_active` | **true** |
| `earn_dimension_quarantine_active` | **true** |
| `earn_pvp_quarantine_active_pack_94_preserved` | **true** |
| `earn_guild_quarantine_active_pack_94_preserved` | **true** |
| `shops_buy_quarantine_active` | **true** |
| `soul_forge_retire_quarantine_active` | **true** |
| `wallet_spend_ledger_live_pack_93_preserved` | **true** |
| `equipment_loader_strict_real_pack_94_preserved` | **true** |
| `equipment_write_strict_real_pack_94_preserved` | **true** |
| `reward_live` | **false** |
| `progress_live` | **false** |
| `release_readiness_claimed` | **false** |

## MD5 Rebase

(file: `v110_pack_95_md5_rebase_v1.json`)

File runtime modificati:
- `backend/routes/combat.py` (story battle strict path già committed con marker `_slc_pack_95_*`)
- `backend/routes/soul_forge.py` (4 endpoint quarantine: earn-mission, earn-dimension, /shops/buy, /soul-forge/retire)

Nessun MD5 historical lock weakening. Nessun fake_PASS. Baseline signature preserved.

## Gate Preservation

(file: `v110_pack_95_gate_invariant_preservation_v1.json`)

Tutti i pack 84–94 preserved:
- ✅ Pack 84 PSP normalization
- ✅ Pack 85 PSP onboarding
- ✅ Pack 86 lobby PSP ensure
- ✅ Pack 87 server-scoped starter flow
- ✅ Pack 88 team formation strict
- ✅ Pack 89 inventory PSP-scoped
- ✅ Pack 90 inventory write strict
- ✅ Pack 91 inventory frontend
- ✅ Pack 92 core server scope
- ✅ Pack 93 economy progress + wallet spend ledger
- ✅ Pack 94 equipment strict + legacy earn-pvp/earn-guild quarantine
- ✅ POSTQA_D gates locked (no unlock in Pack 95)
- ✅ battle_engine unchanged
- ✅ battle_simulate NOT called from staging/live
- ✅ story.tsx / combat.tsx unchanged

## Explicit Statements

### No reward live activation generale

✅ **Confermato.** `reward_live = false` ovunque. Strict story battle path inserisce ledger row con `live_grant=false`. Nessun endpoint Pack 95 grants currency reale.

### No premium / hard currency grant

✅ **Confermato.** Nessun `$inc` su `users.gems`, nessuna scrittura a `users.gold` o premium store. Approval `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE` NON ricevuta.

### No double reward grant

✅ **Confermato.** Static check + smoke E2E provano che:
- Stessa `idempotency_token` → `idempotent_replay: true` senza secondo ledger insert
- Single ledger row per token verificato in DB

### No account-wide story progress write

✅ **Confermato.** Strict path scrive SOLO `player_server_profiles.story_progress`. Static guard verifica assenza di `db.users.update_one` e `db.story_progress` (legacy) nello strict block.

### Pack 91 / 93 / 94 preserved

✅ **Confermato.** Smoke E2E verifica:
- `pack_92_wallet_split_preserved` (`filter_applied=true, wallet_source=psp_server_scoped_split`)
- `pack_94_equipment_loader_strict_preserved` (`filter_applied=true`)
- `pack_90_buy_strict_preserved` (item-shop/buy 400/422)
- `earn-pvp/earn-guild` quarantine Pack 94 inviati con server_id → blocker preservato

## Deferred Blockers

1. **Reward claim ledger LIVE EXECUTE** — `AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE`
2. **Story progress write frontend UI unlock** — `AUTORIZZO_V110_STORY_PROGRESS_FRONTEND_UNLOCK`
3. **Legacy currency earn-\* strict promotion** (richiede reward ledger live)
4. **Shops buy strict server-scoped execute** — `AUTORIZZO_V110_SHOPS_BUY_STRICT_SCOPE_EXECUTE`
5. **Soul forge retire strict server-scoped execute** — `AUTORIZZO_V110_SOUL_FORGE_RETIRE_STRICT_SCOPE_EXECUTE`
6. **Forge upgrade/fuse endpoints** (non implementati)
7. **Frontend equipment UI POSTQA_D unlock** (NON eseguito)
8. **Legacy cleanup pre-Pack-86 user_heroes** (deferito)

## Next Step

Attendere autorizzazione esplicita per uno dei deferred blocker sopra. Suggerito ordine di priorità:

1. **P0** — Reward claim ledger LIVE EXECUTE (sblocca tutti i futuri claim path: mail, achievements, daily, battlepass, story+grant, battle, afk, event)
2. **P1** — Shops buy strict + Soul forge retire strict (richiede wallet_spend_ledger preliminare per shops)
3. **P2** — Frontend equipment UI POSTQA_D unlock
4. **P2** — Forge upgrade/fuse endpoints implementation
5. **P3** — Legacy cleanup pre-Pack-86 `user_heroes`

## Sync Status

```json
{
  "local_commit_only": true,
  "public_push_managed_externally": true,
  "no_remote_available": true,
  "commit_hash": "cc8049093284343dc1c2d5c291867dda3c27992c"
}
```
