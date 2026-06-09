# Pack 89 — Inventory PSP-Scoped Loader Promotion Preflight — Final Report

**Pack ID:** `MEGA_RELEASE_ACCELERATION_89_INVENTORY_PSP_SCOPED_LOADER_PROMOTION_PREFLIGHT`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_INVENTORY_PSP_SCOPED_LOADER_PROMOTION`
**Generated UTC:** 2026-06-09
**Verdict:** `MEGA_RELEASE_ACCELERATION_89_INVENTORY_PSP_SCOPED_LOADER_PROMOTION_RUNTIME_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Verdict

Pack 89 chiuso con esito **RUNTIME_READY** (non solo preflight). L'audit data-only del catalogo
inventory ha rivelato che lo **schema è già server-scoped al DB level** (10/10 docs con `server_id`).
La feasibility gate ha autorizzato la promozione runtime read-path senza necessità di migration/backfill.
`GET /api/inventory` è ora STRICT server-scoped: con `server_id` filtra esclusivamente per
`(user_id, server_id)`, blockers espliciti su PSP mancante o `server_id` vuoto, ZERO fallback
account-wide nel path player-facing. Master suite 3-run deterministica:
**1474 PASS / 29 OPTIONAL FAIL (= baseline) / 0 MISS / 0 REQUIRED FAIL**.

---

## Commit Hash

- **Commit hash locale Pack 89:** (popolato post-commit nel finish summary)
- **Commit hash precedente Pack 88:** `d6db1f4cc1deaa1e539510f215ba02bfed31a0d7`
- **Sync status:** `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`

---

## Git Diff Stat

```
backend/routes/items.py                                                                    | +105/-12 (GET /api/inventory promoted strict server-scoped)
backend/scripts/run_hero_skill_kit_validator_suite.py                                     | +16 lines (Pack 89 16 new tracks)
backend/scripts/validate_v110_pack_89_*.py                                                | +15 file (nuove validator track)
backend/scripts/validate_mega_release_acceleration_89_*.py                                | +1 file (rollup)
backend/scripts/cleanup_v110_pack_89_test_artifacts.py                                    | +1 file (refuse-by-default)
data/design/v110_pack_89_inventory_psp_scoped/                                            | +16 file (design JSON)
docs/divine/110_INVENTORY_PSP_SCOPED_LOADER_PROMOTION_PREFLIGHT_FINAL_REPORT.md           | +1 file (questo report)
```

---

## Baseline / Final 3-Run Suite

| Run | Pass  | Fail (OPTIONAL) | Miss | Required Fail |
|-----|-------|------------------|------|---------------|
| baseline_pre_pack | 1458 | 29 | 0 | 0 |
| final_post_pack_run1/2/3 | **1474** | 29 | 0 | **0** |
| delta | **+16** | 0 | 0 | **0** |

- **Determinismo:** ✓ run1=run2=run3=1474 PASS
- **16/16 Pack 89 tracks PASS** deterministiche

---

## Inventory Route/Schema Audit

| Route | File | Pack 89 Status |
|-------|------|----------------|
| `GET /api/inventory` | `backend/routes/items.py::get_inventory` | **PROMOTED** runtime server-scoped |
| `POST /api/item-shop/buy` | `backend/routes/items.py::buy_item` | UNCHANGED (writes deferred a future pack) |
| `POST /api/inventory/use-exp` | `backend/routes/items.py::use_exp_item` | UNCHANGED (writes deferred) |

**Schema collection `inventory`:** `_id`, `user_id`, **`server_id`**, `item_id`, `quantity`, `account_id`, `_slc_g_commit_marker`. **Migration NOT needed** for read promotion.

---

## Inventory SOT

> Inventory/materiali/items operativi sono **SERVER-SCOPED**. Con `server_id` presente,
> `/api/inventory` legge SOLO inventory del `(user_id, server_id)` selezionato.
> **NESSUN fallback account-wide** come fonte player-facing finale.
> **NESSUNA copia inventory S1→S2**. Nuovo server parte inventory vuoto/default
> finché onboarding rewards non saranno approvati separatamente.

---

## Data Audit (Read-Only)

- Total inventory docs: **10**
- Docs with `server_id`: **10** (100%)
- Docs with null/missing `server_id`: **0**
- Distinct `server_id` values: `["s1"]`
- **Migration needed for read promotion: NO** ✓

---

## Feasibility Gate

**Decision:** `PROMOTE_RUNTIME` (schema already server-scoped, no migration needed, smoke E2E verified strict + no leak).

---

## Route Guard / Promotion Result

**Action:** `PROMOTION_RUNTIME`

| Property | Value |
|----------|-------|
| `server_id` optional query param | ✓ |
| `server_id` presente filtra strict `(user_id, server_id)` | ✓ |
| PSP missing → blocker | `PLAYER_SERVER_PROFILE_REQUIRED` |
| `server_id` blank → blocker | `SERVER_ID_REQUIRED` |
| No fallback account-wide quando `server_id` presente | ✓ |
| Path no-`server_id` legacy non-player-facing (flagged) | ✓ |
| NO DB writes | ✓ |
| Dual-read UUID/ObjectId compat | ✓ |
| `filter_applied=true` solo in strict path | ✓ |
| `legacy_account_inventory_used=false` in strict path | ✓ |

**Response schema Pack 89:**
- `pack_89_inventory_strict_server_scope: true`
- `inventory_source: "player_server_scoped" | "legacy_account_wide_deprecated" | "none"`
- `legacy_account_inventory_used: bool`
- `filter_applied: true` strict / `false` legacy
- `blocker: "PLAYER_SERVER_PROFILE_REQUIRED" | "SERVER_ID_REQUIRED" | null`

---

## Future Migration / Backfill Plan

**Migration/backfill needed:** ❌ NO (schema già server-scoped).

**Future write paths promotion plan:**
- `POST /api/item-shop/buy` — richiederà `AUTORIZZO_V110_INVENTORY_WRITE_PATHS_SERVER_SCOPED_MIGRATION_EXECUTE`
- `POST /api/inventory/use-exp` — richiederà stessa authorization string

---

## Backup / Rollback Preflight

- Read-only route promotion — rollback git-revertibile senza impatto DB.
- Cleanup script: `backend/scripts/cleanup_v110_pack_89_test_artifacts.py` (refuse-by-default, `--apply` required).

---

## Frontend Inventory Consumer Check

- **Pack 89 è backend-only**. Nessun frontend file modificato.
- Consumer esistenti che chiamano `/api/inventory` senza `server_id` ricevono il path legacy non-player-facing (flagged). Frontend può opt-in al server-scoped passando `server_id` in futuri refactor.

---

## Runtime Smoke E2E

| Step | Result |
|------|--------|
| 1. `server_id` presente, PSP missing → blocker `PLAYER_SERVER_PROFILE_REQUIRED`, `filter_applied=true`, `legacy_account_inventory_used=false`, `items=[]` | ✓ |
| 2. Legacy path (no `server_id`) → `filter_applied=false`, `inventory_source=legacy_account_wide_deprecated`, `legacy_account_inventory_used=true` | ✓ |
| 3. `ensure` PSP, inventory empty per nuovo server → `filter_applied=true`, `inventory_source=player_server_scoped`, `items=[]` | ✓ |
| 4. **INJECT** `inventory` su `s1` con `item_id=leak_test_item` per test user | ✓ |
| 5. Inventory route su SID nuovo NON mostra leak (`items=[]`, `legacy_account_inventory_used=false`) | ✓ |
| 6. Cleanup eseguito | ✓ |

**Verdict smoke:** `PACK_89_RUNTIME_SMOKE_E2E_PASS_INVENTORY_STRICT_SERVER_SCOPED_NO_ACCOUNT_WIDE_LEAK_NO_DB_WRITES_IN_PROMOTION_PATH`

---

## Data Invariants

Tutti `false`: `inventory_schema_migration_executed`, `inventory_backfill_executed`, `inventory_db_writes_in_promotion_path`, `currencies_db_writes`, `story_db_writes`, `equipment_db_writes`, `false_filter_applied_true`, `account_wide_inventory_leak`, `copy_s1_to_s2`, `premium_grant`, `currency_grant`, `reward_live`, `progress_live`, `legacy_cleanup_executed`, `destructive_migration`, `delete_of_real_data`, `player_level_mutation`, `user_heroes_mutation`, `team_route_regression`, `release_readiness_claimed`.

---

## Live Readiness Update

| Surface | Live? |
|---------|-------|
| `inventory_psp_scoped_loader_runtime_ready` | **true** |
| `inventory_legacy_path_marked_non_player_facing` | **true** |
| `team_formation_strict_server_scope_preserved` | **true** (Pack 88) |
| `pack_87_starter_team_preserved` | **true** |
| `currencies_psp_scoped_loader_ready` | **false** (deferred) |
| `story_psp_scoped_loader_ready` | **false** (deferred) |
| `equipment_psp_scoped_loader_ready` | **false** (deferred) |
| `inventory_write_paths_promoted` | **false** (deferred) |
| `reward_live` / `progress_live` / **`release_readiness_claimed`** | **false** |

---

## MD5 Rebase

| File | To MD5 | Reason |
|------|--------|--------|
| `backend/routes/items.py` | `86ed0118090306a92cb4f8b1cb2f8d74` | `GET /api/inventory` promoted strict server-scoped |

**Replacement invariant funzionale:** ✓ | **Validator weakening:** ✗ | **Fake PASS:** ✗

---

## Gate / Runtime Invariant Preservation

| Pack / Gate | Preserved? |
|-------------|-----------|
| POSTQA_D gates | **locked** |
| Pack 80-88 invariants | **YES** (tutti) |
| v107D / v108 POSTQA-A | **YES** |
| Battle engine formula rewrite | **NO** |

---

## Safety Flags (tutti `false`)

`fake_PASS`, `validator_weakening`, `release_readiness_claimed`, `inventory_schema_migration_executed`, `inventory_backfill_executed`, `inventory_db_writes`, `currencies_db_writes`, `story_db_writes`, `equipment_db_writes`, `false_filter_applied_true`, `account_wide_inventory_leak_in_server_scoped_path`, `copy_s1_to_s2_inventory`, `premium_grant`, `currency_grant`, `reward_live`, `progress_live`, `legacy_cleanup_executed`, `destructive_migration`, `delete_of_real_data`, `player_level_mutation`, `user_heroes_mutation`, `team_route_regression`, `postqa_d_gates_unlocked`, `battle_engine_formula_rewrite`, `battle_simulate_called_from_staging_or_live`.

---

## Explicit Statements

1. **Inventory runtime promoted or deferred** — **RUNTIME_PROMOTED** (schema già server-scoped, no migration needed).
2. **No inventory DB writes** — verificato static (no insert/update/delete in `get_inventory`) e runtime (smoke 6 steps).
3. **No false `filter_applied=true`** — `filter_applied=true` solo nel path strict con `server_id` presente; `filter_applied=false` esplicito nel legacy path.
4. **Reward/progress live OFF** — invariato.
5. **Legacy cleanup NOT executed** — `legacy_cleanup_executed=false`.

---

## Deferred Blockers / Next Step

**Deferred:**
- Currencies / story / equipment PSP-scoped loader promotion (future pack).
- Inventory write paths (`buy`, `use-exp`) — richiederanno `AUTORIZZO_V110_INVENTORY_WRITE_PATHS_SERVER_SCOPED_MIGRATION_EXECUTE`.
- Inventory onboarding/starter rewards — NOT granted; future starter rewards pack.
- Legacy cleanup `users.team_formation` e `user_heroes` pre-Pack-86 — out of scope.

**Future authorization string preparata (NON usata in Pack 89):**
`AUTORIZZO_V110_INVENTORY_SERVER_SCOPE_MIGRATION_EXECUTE`

**Next step recommendation:**

> **NON procedere a Pack 90 senza upload esplicito.**

Candidati: Currencies PSP-scoped promotion / Story progress PSP-scoped promotion / Equipment PSP-scoped promotion / Inventory write paths promotion / Legacy cleanup migration pack.

In attesa di verifica utente + sync pubblica della piattaforma.

---

**END OF REPORT — Pack 89**
