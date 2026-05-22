# SLC-BE — Server Profile Creation Contract + Server Selection Endpoint Contract

> **Status**: ✅ PASS · **Mode**: DESIGN-ONLY / CONTRACT-ONLY / READ-ONLY
> **Date (UTC)**: 2026-05-22 · **Suite Global**: pass=269, fail=0, miss=0

---

## 1. Scope & Mandate

Foundation contracts for the **server profile creation** and **server
selection endpoint** subsystems. Strictly:

- NO MongoDB writes · NO collection/index creation
- NO runtime route creation · NO auth changes · NO UI
- NO `battle_engine.py` / `battle_core.py` / `combat.tsx` / `affinity_gift_spend.py` changes
- NO AF2-N / Stage4 / gacha / roster / Character Bible / catalog / asset changes
- NO Borea exposure · NO second-server enablement · NO validator weakening

Builds on top of:

- **SLC-A** (server shard isolation audit) — present
- **SLC-C** (single-shard → multi-shard migration plan) — PASS, `execution_ready=false`, `second_server_opening_allowed=false`

---

## 2. Files Created (this task)

### JSON design contracts
```
/app/data/design/server_lifecycle/server_profile_default_values_v1.json
/app/data/design/server_lifecycle/server_selection_endpoint_contract_v1.json
/app/data/design/server_lifecycle/server_status_transition_policy_v1.json
/app/data/design/server_lifecycle/new_player_server_routing_policy_v1.json
/app/data/design/server_lifecycle/active_server_resolution_contract_v1.json
/app/data/design/server_lifecycle/server_profile_creation_dry_run_scenarios_v1.json
/app/data/design/server_lifecycle/server_selection_runtime_safety_audit_v1.json   (generated)
/app/data/design/server_lifecycle/slc_be_preflight_result_v1.json                 (generated)
/app/data/design/system_safety/server_lifecycle_profile_selection_readiness_rollup_v1.json
```

### Python scripts
```
/app/backend/scripts/validate_slc_be_preflight_v1.py
/app/backend/scripts/validate_server_profile_creation_contract_v1.py
/app/backend/scripts/validate_server_profile_default_values_v1.py
/app/backend/scripts/validate_server_selection_endpoint_contract_v1.py
/app/backend/scripts/validate_server_status_transition_policy_v1.py
/app/backend/scripts/validate_new_player_server_routing_policy_v1.py
/app/backend/scripts/validate_active_server_resolution_contract_v1.py
/app/backend/scripts/validate_server_profile_creation_dry_run_scenarios_v1.py
/app/backend/scripts/audit_server_selection_runtime_safety_v1.py
/app/backend/scripts/validate_server_lifecycle_profile_selection_readiness_rollup_v1.py
/app/backend/scripts/validate_slc_be_server_profile_selection_combo.py
```

## Files Modified

- `/app/data/design/server_lifecycle/server_profile_creation_contract_v1.json`
  — extended with `db_write`, `migration_required_before_runtime`,
  `second_server_opening_allowed`, `future_feature_flag`,
  `default_server_id_for_legacy`, `future_flow`, `scope_rules`,
  and additional invariants. SLC-C validator still PASS (retro-compatible).
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py`
  — 11 SLC-BE entries added as OPTIONAL.

---

## 3. Preflight

`slc_be_preflight_result_v1.json`:

| Check | Observed |
|---|---|
| SLC-A audit present | ✅ true |
| SLC-C combo present and PASS | ✅ true |
| SLC-C preflight present | ✅ true |
| SLC-C `execution_ready` | ✅ false |
| `second_server_opening_allowed` | ✅ false |
| `/api/heroes` count | ✅ 100 |
| `/api/heroes/primordial_gaia` | ✅ 404 |
| AF2-N cap S2 (50000) marker | ✅ present in `affinity_gift_spend.py` |
| Multishard collections present in runtime DB | ✅ none (40 collections scanned) |
| Errors | 0 |

---

## 4. Server Profile Creation Contract

`server_profile_creation_contract_v1.json` (extended):

- `design_only=true`, `runtime_attached=false`, `db_write=false`
- `migration_required_before_runtime=true`
- `second_server_opening_allowed=false`
- `future_feature_flag=SERVER_PROFILES_RUNTIME_ENABLED`
- `default_server_id_for_legacy="s1"`
- `implementation_status=NOT_IMPLEMENTED_IN_RUNTIME`

**Future flow** (NOT implemented):
1. login_global_account → 2. choose_or_select_server →
3. if_profile_exists_load → 4. if_missing_and_server_open_or_crowded_create_profile_on_first_entry →
5. new_profile_starts_from_zero_server_bound_progression

**Scope rules**:
| Field | Scope |
|---|---|
| starter heroes & rewards | server_bound |
| free currency (gold, diamonds_free, event) | server_bound |
| paid currency (Divine Crystals) | **account_wide** (never cloned per server) |
| VIP level | account_wide |
| VIP claims & rewards | server_bound |
| paid cosmetics ownership | account_wide |
| paid cosmetics equip & use | server_bound |
| active title / equipped cosmetics | server_bound |

**Invariants**: `no_cross_server_data_transfer`, `borea_never_exposed`,
`paid_currency_balance_not_cloned_to_server_profile`,
`no_inherited_roster_from_other_servers`,
`no_inherited_free_currency_from_other_servers`.

### Defaults — `server_profile_default_values_v1.json`

- `level_on_server=1`, `tutorial.completed=false`, `story_chapter=1`
- `server_bound_free_currencies = {gold:0, diamonds_free:0, event_currency:{}}`
- `team_slots.max_active_teams=3`
- Forbidden inheritance: roster, inventory, free currency, progression,
  guild, arena rank (all `true`)
- `account_wide_views_visible_per_server` for paid balance, VIP level,
  paid cosmetics ownership (read-only views)
- Borea safety: `borea_never_exposed_as_starter_hero=true`,
  `borea_never_appears_in_starter_roster_results=true`

---

## 5. Server Selection Endpoint Contract

`server_selection_endpoint_contract_v1.json` —
`endpoint_contract_only=true`, `no_route_created=true`, `no_auth_change=true`,
`implementation_status=NOT_IMPLEMENTED_IN_RUNTIME`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/servers` | list visible servers + recommendation hint |
| GET | `/api/account/server-profiles` | list this account's per-server profiles |
| POST | `/api/account/server-profiles/select` | pick active server (creates profile only on first valid entry) |
| GET | `/api/account/active-server` | return currently active `server_id` |

**`POST select` rejection rules**:
- unknown server_id → 404
- planned → 409 `not_selectable_planned`
- archived → 409 `not_selectable_archived`
- merge_pending no profile → 409 `merge_pending_no_new_profile`
- merged → 308 redirect to merge target
- closed_to_new no profile → 409 `closed_to_new`
- second-server disabled & target ≠ current → 423 `second_server_locked`

Forbidden: `never_clone_server_bound_progress`,
`never_copy_free_currency_across_servers`,
`never_create_profile_for_archived_or_planned`.

---

## 6. Server Status Transition Policy

`server_status_transition_policy_v1.json` — 7 statuses, all rules
explicitly encoded:

| Status | Selectable | New profile | Existing |
|---|---|---|---|
| planned | ❌ | ❌ | ❌ |
| open | ✅ | ✅ | ✅ |
| crowded | ✅ | only_below_hard_cap | ✅ |
| closed_to_new | existing_only | ❌ | ✅ |
| merge_pending | existing_only | ❌ | ✅ |
| merged | ❌ | ❌ | redirect_to_target |
| archived | ❌ | ❌ | ❌ |

Approval-required transitions explicitly listed.

---

## 7. New-Player Routing / Default Policy

`new_player_server_routing_policy_v1.json`:

- Default for new account: newest **open** server
- If newest is crowded: fall back to newest open **not crowded**
- Manual selection allowed if status permits
- Existing player default: return to last active server
- **No auto-migration** old → new; **no cross-server resource copy**
- Legacy player default in future migration: **s1**

Forbidden: copy inventory/roster/free currency across servers; auto-route
existing players to new server; expose Borea in starter routing.

`compatibility_window.single_shard_runtime=true`,
`compatibility_window.second_server_opening_allowed=false`.

---

## 8. Active Server Resolution Contract

`active_server_resolution_contract_v1.json`:

- `get_current_user` → account identity only, **NOT** server-aware
- `get_current_server_profile` → resolves `(account_id, active_server_id)`;
  raises **HTTP 423 `no_active_server`** when unresolvable
- Server-bound endpoints require resolved profile
- Account-wide endpoints must explicitly opt out

**Active server resolution priority**:
1. `X-Server-ID` header (must match owned profile, else 403)
2. Stored `active_server_id` on session
3. `server_id` query param (only when explicitly enabled)
4. `default_legacy_server_id=s1` (ONLY during compat window)

**Failure modes** (future runtime):
- no_active_server → HTTP 423
- header mismatch → HTTP 403
- archived → HTTP 410
- merged → HTTP 308 redirect

`unsafe_fallback_removal.requires_explicit_user_approval=true`, gated on
**SLC-C phase 11**.

---

## 9. Dry-Run Scenarios

`server_profile_creation_dry_run_scenarios_v1.json` — **15 scenarios** (≥12 required), all read-only / no DB writes. Highlights:

1. Legacy s1 existing profile → load, no creation
2. New account routed to s2 open → create profile (level 1, free currency 0)
3. Closed_to_new + no profile → 409 reject
4. Closed_to_new + existing profile → load
5. Auto-route to newest open server
6. Newest crowded → fallback to newest open not crowded
7. Merged server → 308 redirect
8. Archived server → 409 reject
9. Paid currency visible **account-wide view** per server (not cloned)
10. Free currency starts at server default 0
11. Paid cosmetic owned but not equippable until hero exists on server
12. **Borea / greek_borea / primordial_gaia hidden from starter roster**
13. Second-server disabled blocks select to non-current → 423
14. Merge_pending + no profile → 409
15. Planned server → 409

---

## 10. Runtime Safety Audit

`server_selection_runtime_safety_audit_v1.json`:

| Check | Result |
|---|---|
| No new runtime routes for `/api/servers`, `/api/account/server-profiles`, `/api/account/server-profiles/select`, `/api/account/active-server`, `/api/server/enter` | ✅ all absent in `/app/backend/routes/**` |
| Protected files SHA-256 match (battle_engine, battle_core, combat.tsx, affinity_gift_spend.py) | ✅ all match SLC-C baseline |
| AF2-N cap S2 (50000) marker | ✅ present |
| Forbidden multishard collections in runtime DB (server_profiles, servers, server_wallets_free, accounts_wallet_paid, accounts_wallet_paid_ledger) | ✅ none (40 cols scanned) |
| Env `SECOND_SERVER_OPENING_ENABLED` | ✅ unset |
| Env `SERVER_PROFILES_RUNTIME_ENABLED` | ✅ unset |
| UI references to server-selection endpoints in `/app/frontend/app/**.tsx` | ✅ none |
| Borea safe | ✅ true |
| `second_server_opening_allowed` | ✅ false |

---

## 11. Rollup

`/app/data/design/system_safety/server_lifecycle_profile_selection_readiness_rollup_v1.json`:

```
server_profile_contract_ready              = true
server_selection_contract_ready            = true
active_server_resolution_contract_ready    = true
new_player_routing_policy_ready            = true
server_status_transition_policy_ready      = true
dry_run_scenarios_ready                    = true
runtime_safety_audit_ready                 = true

runtime_enabled                            = false
db_write                                   = false
migration_applied                          = false
second_server_opening_allowed              = false
route_patch_required                       = true
default_s1_migration_required              = true
borea_safe                                 = true
af2n_invariant_intact                      = true
```

**Blockers to runtime enable** (7 listed):
1. SLC-C migration not committed (phase 0 freeze+snapshot not approved)
2. `server_profiles` collection does not exist in runtime DB
3. `server_wallets_free` / `accounts_wallet_paid` collections do not exist
4. Server-aware route patch (SLC-F) is design-only; runtime routes still single-shard
5. Default S1 backfill (SLC-G) not committed
6. `get_current_server_profile` dependency does not exist in runtime
7. Unsafe fallback removal (phase 11) requires explicit user approval

**Future feature flags** (all currently `false`):
`SERVER_PROFILES_RUNTIME_ENABLED`, `SERVER_AWARE_READS_ENABLED`,
`SERVER_AWARE_WRITES_ENABLED`, `SECOND_SERVER_OPENING_ENABLED`.

---

## 12. Validators / Suite / Baseline

### SLC-BE Combo
```
[slc_be_combo_v1] PASS
  PASS  preflight
  PASS  server_profile_creation_contract
  PASS  server_profile_default_values
  PASS  server_selection_endpoint_contract
  PASS  server_status_transition_policy
  PASS  new_player_server_routing_policy
  PASS  active_server_resolution_contract
  PASS  dry_run_scenarios
  PASS  runtime_safety_audit
  PASS  readiness_rollup
```

### Global Suite (with SLC-BE optional entries)
```
Overall: PASS  (pass=269, fail=0, miss=0)
```

### Baseline diff
```
Invariants:               5★=20, 6★=13, DW=13
final_numbers / runtime flags: clean across 5★+6★ slots
Marchio Boreale leak:     0 in non-Borea
Forbidden hero IDs:       0 (borea / primordial_gaia / aliases)
```

### SLC-C combo (regression check after server_profile_creation_contract extension)
```
[slc_c_combo_v1] PASS  (14/14 steps)
```

---

## 13. API Smoke (read-only)

| Endpoint | Status | Note |
|---|---|---|
| `/api/health` | 200 | reachable |
| `/api/heroes` | 200, count=100 | hard invariant ✅ |
| `/api/heroes/primordial_gaia` | 404 | hard invariant ✅ |
| `/api/heroes/borea` | 200 | **pre-existing catalog-only baseline** (unchanged) |
| `/api/heroes/greek_borea` | 200 | **pre-existing catalog-only baseline** (unchanged) |
| `/api/servers` | not implemented | ✅ (per contract `do_not_implement_routes_now=true`) |
| `/api/account/server-profiles` | not implemented | ✅ |
| `/api/account/server-profiles/select` | not implemented | ✅ |
| `/api/account/active-server` | not implemented | ✅ |

---

## 14. Borea Safety

- `/api/heroes` list still contains exactly 100 heroes, none of which are
  `borea` / `greek_borea` / `primordial_gaia`.
- `/api/heroes/primordial_gaia` returns 404 (hard invariant).
- `/api/heroes/borea` and `/api/heroes/greek_borea` return 200 as
  **pre-existing catalog-only inert data** — SLC-BE did not introduce or
  modify this behavior.
- All SLC-BE contracts explicitly forbid Borea exposure in starter rosters,
  starter routing, and server selection responses.

---

## 15. AF2-N / Stage4 Safety

- AF2-N gift-spend ledger cap (Cap S2): **50000** unchanged.
- Stage4 internal-beta allowlist: **2500** unchanged.
- `affinity_gift_spend.py` SHA-256 matches SLC-C baseline (no diff).
- Local Redis rate-limit backend: still operational (re-armed via
  `/app/ops/ensure_redis_rate_limit.sh`).
- Managed Redis / Alerting sink: still env-gated (no change).
- Broad rollout: still OFF.

---

## 16. Warnings

1. **Redis container drop is a recurring infrastructure issue** (already
   documented in handoff). Mitigated automatically via
   `/app/ops/ensure_redis_rate_limit.sh`. NOT introduced by SLC-BE.
2. **Pre-existing catalog-only behavior** on `/api/heroes/borea` and
   `/api/heroes/greek_borea` returning 200: documented as baseline in
   `_slc_c_api_smoke_readonly_v1_result.json`. NOT a regression.
3. **333 `user_id` references in `/app/backend/routes/**`** — the technical
   debt baseline that SLC-C phases 6–11 are designed to address. NO action
   taken in this task.

---

## 17. Risks

| Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|
| Future implementer skips phase-11 user approval before removing legacy fallback | Low | High | `unsafe_fallback_removal.requires_explicit_user_approval=true` enforced in 2 design docs (SLC-C phase plan + SLC-BE active server resolution) |
| Future runtime route accidentally implements `/api/account/server-profiles/select` before migration | Low | High | `audit_server_selection_runtime_safety_v1.py` re-scans routes; will fail-fast |
| Paid balance clone accidentally introduced per server | Low | High | `paid_currency_balance_not_cloned_to_server_profile=true` invariant + `paid_free_currency_split_plan_v1` |
| Borea leak into starter roster | Very Low | Critical | dry-run scenario 12 + 3 rollup invariants enforce hiding |
| Second-server enable env var accidentally set in production | Low | High | `audit_server_selection_runtime_safety_v1.py` checks env vars unset |

---

## 18. Recommendation

- ✅ **Accept** SLC-BE deliverables as the foundational contract set for
  the future multi-server runtime.
- ⏳ **Do NOT proceed** to SLC-F (server-aware route patch dry-run) or
  SLC-G (default S1 migration commit) without explicit user approval and
  full review of these contracts.
- ⏳ **Do NOT open** any second server until **all 7 blockers** in the
  rollup are resolved AND user has signed off on phases 0–12 of the
  SLC-C migration plan.

---

## 19. Next Tasks (NOT executed)

- **SLC-F** — server-aware route patch dry-run (design-only)
- **SLC-G** — default S1 migration commit (strictly gated)
- **SLC-D** — merge tooling simulation offline (design-only)
- **SLC-H** — server selection endpoint implementation (strictly gated)

---

**End of report.** SLC-BE closed as DESIGN-ONLY / CONTRACT-ONLY / PASS.
No DB writes, no runtime mutation, no UI, no Borea exposure, no AF2-N
drift, no critical file diff.
