# 97 — SLC-F · Server-Aware Route Patch Dry-Run (Canonical)

> **Status**: ✅ PASS · **Mode**: DESIGN-ONLY / AUDIT-ONLY / READ-ONLY / DRY-RUN
> **Date (UTC)**: 2026-05-22 · **Suite globale**: 302 PASS / 0 FAIL / 0 MISS

---

## 1. Scopo

Eseguire SLC-F: produrre **inventario, risk matrix, patch contract, dry-run
simulation, validators e report** per preparare la futura migrazione
server-aware delle route, **senza toccare il runtime**.

Baseline obbligatoria: **Divine Benchmark Canonical Source-of-Truth**
(`/app/data/design/benchmark_canonical/benchmark_canonical_index_v1.json`).

---

## 2. File creati

### JSON design (`/app/data/design/server_lifecycle/` + `system_safety/`)
1. `slc_f_route_scope_inventory_v1.json` — 30 route families classificate
2. `slc_f_collection_scope_matrix_v1.json` — 19 collections con future key strategy
3. `slc_f_endpoint_patch_contract_v1.json` — 14 endpoint pseudo-diff + 2 dipendenze future
4. `slc_f_legacy_s1_compatibility_plan_v1.json` — 7 fasi, default `s1`
5. `slc_f_dry_run_simulation_plan_v1.json` — 10 scenari
6. `slc_f_route_patch_risk_matrix_v1.json` — 11 rischi (P0/P1/P2)
7. `slc_f_runtime_guardrail_policy_v1.json` — 25 hard guardrail
8. `slc_f_readiness_rollup_v1.json`
9. `system_safety/server_lifecycle_slc_f_route_patch_dryrun_readiness_rollup_v1.json`

### Script Python (`/app/backend/scripts/`)
- `_slc_f_common.py` (helper)
- `validate_slc_f_preflight_v1.py`
- `audit_slc_f_route_scope_inventory_v1.py`
- `validate_slc_f_collection_scope_matrix_v1.py`
- `validate_slc_f_endpoint_patch_contract_v1.py`
- `validate_slc_f_legacy_s1_compatibility_plan_v1.py`
- `simulate_slc_f_route_patch_dryrun_v1.py`
- `validate_slc_f_route_patch_risk_matrix_v1.py`
- `audit_slc_f_runtime_safety_v1.py`
- `validate_slc_f_readiness_rollup_v1.py`
- `validate_slc_f_route_patch_dryrun_combo_v1.py`

### Doc
- `/app/docs/divine/97_SLC_F_ROUTE_PATCH_DRYRUN_CANONICAL.md` (questo file)

## File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — 10 entry SLC-F aggiunti OPTIONAL. Nessun REQUIRED indebolito.

---

## 3. Preflight

`_slc_f_preflight_v1_result.json`:
- canonical index presente ✅
- SLC-C combo PASS ✅
- SLC-BE combo PASS ✅
- `/api/heroes`=100 ✅
- `/api/heroes/primordial_gaia`=404 ✅
- AF2-N cap 50000 marker presente ✅
- `SERVER_PROFILES_RUNTIME_ENABLED` / `SECOND_SERVER_OPENING_ENABLED` unset ✅

---

## 4. Route scope inventory (30 family)

Files scanned: **30** (tutti esistenti su disco). User_id refs totali nelle route classificate: **343**.

| Scope | Count | Esempi |
|---|---|---|
| `global_catalog_readonly` | 7 | heroes, hero_skill_kits_catalogs, skill_status_vfx_catalogs, divine_weapons, sprites, server_time, skill_kit_runtime_debug |
| `account_wide` | 3 | auth_user (server.py), economy_paid_wallet, push_notifications |
| `mixed_account_owned_server_equipped` | 2 | cosmetics, game_data |
| `server_bound` | 18 | hero_progression, items_inventory, equipment, forge, soul_forge, artifacts, combat, raids, gvg, guild, social, sanctuary, affinity_gifts, affinity_gift_spend, achievements, rankings, level_sharing, player_faction_v2 |
| `unsafe_unknown` | **0** ✅ |

**Top route con user_id refs** (per il futuro patch):
```
30 hero_progression.py
30 items.py
27 combat.py (protected — file battle/combat NON toccato qui)
26 server.py (auth)
26 affinity_gift_spend.py (protected — AF2-N invariato)
25 soul_forge.py
21 economy.py
21 artifacts.py
19 sanctuary.py
17 heroes.py (protected — catalog read-only)
```

Protected files dichiarati: `battle_engine.py`, `battle_core.py`, `combat.tsx`, `affinity_gift_spend.py`, `heroes.py`.

---

## 5. Collection scope matrix (19 collections)

| Collection | Future key strategy | Scope | Unique index |
|---|---|---|---|
| users | `account_id_only` | account_wide | `[account_id]` |
| accounts_wallet_paid | `account_id_only` | account_wide | `[account_id]` |
| accounts_wallet_paid_ledger | `account_id_plus_server_id_plus_entity_id` | account_wide | `[account_id, tx_id]` |
| server_profiles | `account_id_plus_server_id` | server_bound | `[account_id, server_id]` |
| servers | `global_static_catalog` | server_bound | `[server_id]` |
| server_wallets_free | `account_id_plus_server_id` | server_bound | `[account_id, server_id]` |
| user_heroes | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, hero_id]` |
| teams | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, team_id]` |
| inventory | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, item_id]` |
| gacha_history | `account_id_plus_server_id` | server_bound | `[account_id, server_id, pull_id]` |
| story_progress | `account_id_plus_server_id` | server_bound | `[account_id, server_id]` |
| guilds | `account_id_plus_server_id_plus_entity_id` | server_bound | `[server_id, guild_id]` |
| arena_rankings | `account_id_plus_server_id` | server_bound | `[account_id, server_id]` |
| user_affinity_state | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, hero_id]` |
| **gift_transaction_ledger** | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, idempotency_key]` | **AF2-N preservation_required=true** |
| **user_gift_inventory** | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, gift_id]` | **AF2-N preservation_required=true** |
| event_progress | `account_id_plus_server_id_plus_entity_id` | server_bound | `[account_id, server_id, event_id]` |
| account_cosmetics | `account_id_plus_server_id_plus_entity_id` | account_wide | `[account_id, cosmetic_id]` (ownership account-wide) |
| heroes_catalog | `global_static_catalog` | global_catalog_readonly | `[hero_id]` |

`accounts_wallet_paid` resta `account_id_only` (paid balance **mai clonato per server**).

---

## 6. Endpoint patch contract (14 endpoint, NOT IMPLEMENTED)

`do_not_implement_routes_now=true`. Pseudo-diff per:

- `GET /api/user/heroes` — filter by `(account_id, server_id)`; failure 423/403
- `POST /api/team` — upsert by `(account_id, server_id, team_id)`
- `GET /api/inventory` — `(account_id, server_id)`
- `POST /api/gacha/pull` — `(account_id, server_id, pull_id)` · pity scope futuro `(account_id, server_id, banner_id)`
- `GET /api/account/profile` — by `account_id` (account_wide)
- `GET /api/account/wallet/paid` — by `account_id` (account_wide, mai clonato)
- `GET /api/server/wallet/free` — by `(account_id, server_id)`
- **`POST /api/affinity/gift-spend`** — protected; cap **50000** + allowlist **2500** PRESERVATI
- **`GET /api/heroes (list)`** — protected; resta global_catalog_readonly, 100 heroes
- **`GET /api/heroes/{id}`** — protected; primordial_gaia=404, borea/greek_borea baseline immutato
- `GET /api/cosmetics/owned` — by `account_id`
- `POST /api/cosmetics/equip` — by `(account_id, server_id, cosmetic_id)`
- `GET /api/rankings` — by `server_id`
- `GET /api/guild` — by `(account_id, server_id) → guild_id`

Nuove dipendenze future dichiarate:
- `get_current_user` (account identity, NOT server-aware)
- `get_current_server_profile` (account_id + active_server_id; raises HTTP 423 `no_active_server`)

---

## 7. Legacy S1 compatibility plan

`default_legacy_server_id="s1"`. `backfill_executed=false`. 7 fasi (0–11):
- Phase 0: design & freeze
- Phase 1: seed `servers` collection con `{server_id:'s1',status:'open'}` (design only)
- Phase 2: legacy server_profiles plan (design only)
- Phase 3: dual-read window
- Phase 4: server_id tagging writes (NON in SLC-F)
- Phase 5: backfill existing docs (gated)
- **Phase 11**: rimozione fallback legacy `s1` → `reversible=false`, `requires_explicit_user_approval=true`

Resolver fallback rules (priorità): `X-Server-ID header` > `stored_active_server_id` > `server_id query param` > `default_legacy_server_id=s1` (solo in compat window).

AF2-N preservation during compatibility: cap=**50000**, allowlist=**2500**, ledger rows preservati, inventory rows preservati.

---

## 8. Dry-run simulation (10 scenari, NO DB writes)

`_slc_f_route_patch_dryrun_simulation_v1_full_report.json`:

| ID | Scenario | Risultato simulato |
|---|---|---|
| 1 | legacy_user → s1 | resolved=`s1`, source=`default_legacy_server_id_s1`, creates_profile=false |
| 2 | header X-Server-ID priorità | resolved=`s1`, source=`x_server_id_header` |
| 3 | mismatch X-Server-ID → 403 | http_status=403, reason=`forbidden_server` |
| 4 | no active server post-phase11 → 423 | http_status=423, reason=`no_active_server` |
| 5 | merged server → 308 | redirect_to=`s_merge_dst` |
| 6 | archived server → 410 | reason=`server_archived` |
| 7 | `/api/heroes` invariant | http_status=200, heroes_count=100, borea_in_list=false ✅ |
| 8 | borea catalog-only baseline | http_status=200 (immutato) |
| 9 | primordial_gaia=404 | http_status=404 ✅ |
| 10 | AF2-N cap 50000 invariant | cap_preserved=true, allowlist_preserved=true ✅ |

`route_patch_applied=false`, `db_write=false`, `second_server_opening_allowed=false`.

---

## 9. Risk matrix (11 rischi)

**P0 (5)**: AF2-N gift_spend invariant · battle runtime untouched · borea exposure · second_server_opening locked · paid currency clone forbidden

**P1 (4)**: dual read window drift · mixed endpoints split (game_data, cosmetics) · unsafe fallback removal (phase 11 irreversible) · pity scope migration `(user_id, banner_id) → (account_id, server_id, banner_id)` senza leak

**P2 (2)**: telemetry naming · ranking visibility

Tutti con `mitigation` esplicita. Global invariants enforced: AF2-N cap=50000, allowlist=2500, /api/heroes=100, primordial_gaia=404, borea baseline unchanged, feature flags False.

---

## 10. Runtime safety audit

`_slc_f_runtime_safety_audit_v1_full_report.json`:

| Check | Stato |
|---|---|
| Protected files SHA-256 vs SLC-C baseline | ✅ tutti match (battle_engine, battle_core, combat.tsx, affinity_gift_spend, heroes) |
| Future SLC-BE routes leakage (`/api/servers`, `/api/account/server-profiles`, `/api/account/server-profiles/select`, `/api/account/active-server`, `/api/server/enter`) | ✅ 0 hit |
| AF2-N cap marker (50000) | ✅ presente |
| Forbidden multishard collections in DB | ✅ vuoto |
| `SERVER_PROFILES_RUNTIME_ENABLED` / `SECOND_SERVER_OPENING_ENABLED` | ✅ unset |
| `route_patch_applied` | ❌ false (design-only intentional) |
| `db_write` | ❌ false |

---

## 11. Readiness rollup

`slc_f_readiness_rollup_v1.json` (+ mirror in `system_safety/`):

```
route_scope_inventory_ready          = true
collection_scope_matrix_ready        = true
endpoint_patch_contract_ready        = true
legacy_s1_compatibility_plan_ready   = true
dry_run_simulation_plan_ready        = true
route_patch_risk_matrix_ready        = true
runtime_guardrail_policy_ready       = true

runtime_patch_applied                = false
db_write                             = false
migration_applied                    = false
second_server_opening_allowed        = false
server_profiles_runtime_enabled      = false
borea_safe                           = true
af2n_invariant_intact                = true
```

7 blockers documentati prima del runtime patch. 4 future feature flags tutti `false`.

---

## 12. Validator + suite + baseline + API smoke

### SLC-F combo
```
[slc_f_route_patch_dryrun_combo_v1] PASS  (9/9 steps)
  PASS  preflight
  PASS  route_scope_inventory
  PASS  collection_scope_matrix
  PASS  endpoint_patch_contract
  PASS  legacy_s1_compatibility
  PASS  dry_run_simulation
  PASS  route_patch_risk_matrix
  PASS  runtime_safety_audit
  PASS  readiness_rollup
```

### Suite globale
```
Overall: PASS  (pass=302, fail=0, miss=0)
```
10 nuovi entry OPTIONAL aggiunti (SLC-F-PREFLIGHT, SLC-F-ROUTE-SCOPE-INVENTORY, SLC-F-COLLECTION-SCOPE-MATRIX, SLC-F-ENDPOINT-PATCH-CONTRACT, SLC-F-LEGACY-S1-COMPATIBILITY-PLAN, SLC-F-DRY-RUN-SIMULATION, SLC-F-ROUTE-PATCH-RISK-MATRIX, SLC-F-RUNTIME-SAFETY-AUDIT, SLC-F-READINESS-ROLLUP, SLC-F-COMBO). Nessun REQUIRED indebolito.

### Baseline diff
```
Invariants: 5★=20, 6★=13, DW=13
final_numbers / runtime flags: clean across 5★+6★ slots
Marchio Boreale leak: 0 in non-Borea
Forbidden hero IDs: 0 (borea / primordial_gaia / aliases)
```

### API smoke (read-only)
| Endpoint | Status |
|---|---|
| `/api/heroes` count | 100 ✅ |
| `/api/heroes/primordial_gaia` | 404 ✅ |
| `/api/heroes/borea` | 200 (baseline catalog-only, immutato) |
| `/api/heroes/greek_borea` | 200 (baseline catalog-only, immutato) |
| AF2-N cap marker (`min(v, 50000)`) | presente ✅ |

---

## 13. Safety statement

NO DB writes · NO migrations · NO collection/index creation · NO runtime route implementation · NO auth runtime change · NO server selection runtime · NO second server opening · NO UI · NO modifiche a `battle_engine.py` / `battle_core.py` / `combat.tsx` / `affinity_gift_spend.py` · NO modifiche a gacha / roster / Character Bible / catalog / final_numbers / assets · NO AF2-N / Stage4 / Redis runtime changes · `SERVER_PROFILES_RUNTIME_ENABLED` unset · `SECOND_SERVER_OPENING_ENABLED` unset · 0 multishard collections in MongoDB · 0 future-SLC-BE routes leak nel runtime · NO validator REQUIRED indebolito.

---

## 14. Warnings

1. **Redis container drop ricorrente**: noto issue infra (mitigato via `ensure_redis_rate_limit.sh`). NON causato da questo task.
2. **`/api/heroes/borea` e `/api/heroes/greek_borea` = 200**: baseline catalog-only pre-esistente immutato.
3. **343 `user_id` refs in route classificate** (top: hero_progression 30, items 30, combat 27, server.py 26, affinity_gift_spend 26): debito tecnico baseline da risolvere in **future runtime phases**. SLC-F le ha classificate ma NON modificate.

---

## 15. Recommendation

- ✅ Accettare SLC-F come **prerequisito design-only completo** per le successive runtime phases (SLC-G/D/H).
- ⏳ Prossimo design-only consigliato: **SLC-G** (default S1 migration commit) o **SLC-D** (merge tooling simulation offline), entrambi strictly gated.
- ⏳ NON procedere ad **alcuna implementazione runtime** senza:
  - Approvazione esplicita utente
  - 7 blockers SLC-F rollup risolti
  - Feature flags discussi e formalmente abilitati
- ⏳ **Phase 11** (rimozione fallback legacy s1) richiede approvazione utente esplicita (`reversible=false`).

---

## 16. Next tasks (NON eseguiti)

- 🟡 P1: **SLC-G** — default S1 migration commit (gated, strictly)
- 🟡 P1: **SLC-D** — merge tooling simulation offline (design-only)
- 🟡 P1: **SLC-H** — server selection endpoint implementation (gated)
- 🟢 P2: COSMETIC-B/C/D/E
- 🔵 P3: Managed Redis Live + Alerting Sink Live (in attesa env vars)
- 🔴 P4: Broad rollout / Public spend UI / STACK-G (strictly deferred/OFF)

---

**End of report.** SLC-F — Server-Aware Route Patch Dry-Run chiuso come DESIGN-ONLY / AUDIT-ONLY / DRY-RUN / PASS. Nessuna scrittura DB, nessuna mutazione runtime, nessuna UI, nessuna exposure Borea, nessun drift AF2-N, nessun diff su file critici.
