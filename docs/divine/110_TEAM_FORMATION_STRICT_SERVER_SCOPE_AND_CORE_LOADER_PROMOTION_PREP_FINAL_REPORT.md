# Pack 88 — Team Formation Strict Server-Scope + Core Loader Promotion Prep — Final Report

**Pack ID:** `MEGA_RELEASE_ACCELERATION_88_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PROMOTION_PREP`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PREP`
**Generated UTC:** 2026-06-08
**Verdict:** `MEGA_RELEASE_ACCELERATION_88_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PROMOTION_PREP_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Verdict

Pack 88 chiuso con esito **READY** sotto vincoli strict-mode. Il caveat P0 del Pack 87 è stato corretto:
`backend/routes/v96_team_formation.py` ora è **STRICT SERVER-SCOPED** — quando `server_id` è presente,
la team formation è letta ESCLUSIVAMENTE da `player_server_profiles.team_formation`, con blockers
espliciti su PSP mancante o team vuoto. **ZERO fallback a `user.team_formation` account-wide**.
**Pack 87 starter team flow preservato**. Master suite 3-run deterministica:
**1458 PASS / 29 OPTIONAL FAIL (= baseline) / 0 MISS / 0 REQUIRED FAIL**.

---

## Commit Hash

- **Commit hash locale Pack 88:** (popolato post-commit nel `finish` summary)
- **Commit hash precedente Pack 87:** `fe6ef69d001859f56a444de7f63076563a992b00`
- **Sync status:** `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`

---

## Git Diff Stat

```
backend/routes/v96_team_formation.py                                                         | rewrite (~165 lines, strict server-scoped + legacy non-player-facing path)
backend/scripts/run_hero_skill_kit_validator_suite.py                                        | +15 lines (Pack 88 15 new tracks)
backend/scripts/validate_v110_pack_88_*.py                                                   | +14 file (nuove validator track)
backend/scripts/validate_mega_release_acceleration_88_*.py                                   | +1 file (rollup)
backend/scripts/validate_v110_team_formation_route_hardening.py                              | +/- 12 lines (Pack 88 token additive, NO weakening)
backend/scripts/cleanup_v110_pack_88_test_artifacts.py                                       | +1 file (refuse-by-default)
data/design/v110_pack_88_team_formation_strict_server_scope/                                 | +15 file (design JSON)
docs/divine/110_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PROMOTION_PREP_FINAL_REPORT.md | +1 file (questo report)
```

---

## Baseline / Final 3-Run Suite

| Run | Pass  | Fail (OPTIONAL) | Miss | Required Fail |
|-----|-------|------------------|------|---------------|
| baseline_pre_pack | 1443 | 29 | 0 | 0 |
| final_post_pack_run1 | **1458** | 29 | 0 | **0** |
| final_post_pack_run2 | **1458** | 29 | 0 | **0** |
| final_post_pack_run3 | **1458** | 29 | 0 | **0** |
| delta | **+15** | 0 | 0 | **0** |

- **Determinismo:** `run1 == run2 == run3 == 1458 PASS`
- **REQUIRED FAIL:** `0` ✓ **MISS:** `0` ✓
- **OPTIONAL FAIL:** `29` = baseline (zero regressioni)
- **15/15 Pack 88 track PASS deterministiche** su tutti i 3 run.

---

## Team Formation Source Audit

| Surface | Letture | Scritture | Stato Pack 88 |
|---------|---------|-----------|---------------|
| `GET /api/team/get-formation` | PSP.team_formation (strict con server_id) / users.team_formation (legacy non-player-facing senza server_id) | **NESSUNA** | ✓ STRICT |
| `users.team_formation` | legacy / documentazione / non-player-facing | **NESSUNA scrittura nel flow server-scoped** | ✓ |
| `player_server_profiles.team_formation` | Pack 87 starter team init + Pack 88 strict authoritative read | conditional `team_formation in {None, []}` (init only if empty) | ✓ AUTHORITATIVE |
| `POST /api/psp/starter/claim` | letture catalogo eroi | `player_server_profiles.team_formation` (init only if empty) + `user_heroes` con `server_id` | ✓ preservato |

---

## Strict Team Route Implementation

**File modificato:** `backend/routes/v96_team_formation.py` (rewrite completo).

| Property | Value |
|----------|-------|
| `server_id` required for player-facing | ✓ |
| Missing PSP → blocker | `PLAYER_SERVER_PROFILE_REQUIRED` |
| PSP exists, team empty → blocker | `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` |
| Team source (server_id presente) | `player_server_profile` ESCLUSIVAMENTE |
| Fallback a `user.team_formation` | ✗ **MAI** quando server_id presente |
| `users.team_formation` writes | ✗ MAI nel server-scoped flow |
| Fake team / global fallback | ✗ |
| Dual-read UUID/ObjectId compat | ✓ (Pack 82 preservato) |
| Pack 87 starter team preserved | ✓ |
| Legacy path (no server_id) | flagged `team_source=legacy_account_wide_deprecated`, `legacy_account_team_used=true`, `_slc_pack_88_legacy_path_warning` |

**Response schema Pack 88:**
- `pack_88_strict_server_scope: true`
- `team_source: "player_server_profile" | "legacy_account_wide_deprecated" | "none"`
- `legacy_account_team_used: bool` (true SOLO nel path account-wide non-player-facing)
- `filter_applied: true` solo quando server_id presente E path strict
- `blocker: "PLAYER_SERVER_PROFILE_REQUIRED" | "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER" | null`

---

## Starter Team Compatibility (Pack 87 Preserved)

| Property | Value |
|----------|-------|
| `psp_starter_claim` scrive solo a PSP.team_formation | ✓ |
| `users.update_one/update_many` in `psp_starter_claim` | **assente** ✓ |
| Team init only if empty | ✓ |
| Re-claim no overwrite | ✓ |
| Pack 87 markers preserved | `_slc_pack_87_starter_team_init`, `_slc_pack_87_team_initialized_from_starter` |

---

## Frontend Team Consumer Check

| File | Include `server_id` | Honest empty/blocker |
|------|---------------------|----------------------|
| `frontend/app/pre-battle-lobby.tsx` | ✓ | ✓ |
| `frontend/app/servers.tsx` | ✓ (chiama ensure+claim) | N/A (non legge team) |

**Nessuna modifica al frontend richiesta in Pack 88**: il contract API esistente (`team_formation=[]` + blocker) era già gestito onestamente. Pack 88 è puramente un'irrigidimento backend semantico.

---

## Runtime Smoke E2E

Eseguito via `validate_v110_pack_88_runtime_smoke_e2e.py`:

| Step | Result |
|------|--------|
| 1. PSP missing → blocker `PLAYER_SERVER_PROFILE_REQUIRED`, `team_source=none`, `legacy_account_team_used=false` | ✓ |
| 2. POST `/api/psp/ensure` | ✓ |
| 3. PSP exists, team empty → blocker `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER`, `team_source=player_server_profile`, `team_formation=[]` | ✓ |
| 4. POST `/api/psp/starter/claim` | ✓ |
| 5. Team route returns `team_source=player_server_profile`, `team_formation` 3 slot starter | ✓ |
| 6. **INJECT** `user.team_formation` legacy account-wide con `user_hero_id=LEAK_TEST_HERO` | ✓ |
| 7. Team route su ALTRO server (PSP missing) → blocker (no leak): `team_source=none`, `legacy_account_team_used=false`, `team_formation=[]` | ✓ |
| 8. Team route su SID originale → continua a restituire starter team PSP (NO LEAK_TEST_HERO) | ✓ |
| 9. Cleanup eseguito | ✓ |

**Verdict smoke:** `PACK_88_RUNTIME_SMOKE_E2E_PASS_STRICT_SERVER_SCOPED_NO_ACCOUNT_WIDE_FALLBACK_NO_LEAK`

---

## Account-Wide Fallback Guard

### Static assertions

- ✓ Route file `v96_team_formation.py` contains token `pack_88_strict_server_scope`.
- ✓ Strict branch (`if server_id:`) does NOT read `user.get("team_formation")`.
- ✓ Strict branch does NOT assign `team_formation = user.get(...)`.
- ✓ Both blockers (`PLAYER_SERVER_PROFILE_REQUIRED`, `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER`) present in strict branch.
- ✓ `team_source` set to `player_server_profile` only in strict path.
- ✓ Field `legacy_account_team_used` present in response schema.

### Runtime assertions

- ✓ `server_id` presente + `user.team_formation` legacy popolato + PSP missing → blocker (no leak).
- ✓ `server_id` presente + PSP esistente con team vuoto + `user.team_formation` legacy popolato → blocker `TEAM_NOT_CONFIGURED_FOR_SERVER` (no leak).
- ✓ `legacy_account_team_used: false` in strict path indipendentemente da `user.team_formation`.

---

## Core Loader Promotion Prep (Track H — Prep Only, NO Runtime Promotion)

| Loader | Stato attuale | Promosso runtime in Pack 88? | Blockers documentati |
|--------|---------------|------------------------------|---------------------|
| `/api/inventory` | account-wide legacy | ✗ | server_id query + collection scope + migration + ensure auto-call + frontend updates |
| `/api/currencies` | account-wide legacy | ✗ | currency class mapping + PSP.soft_currencies + frontend scope respect |
| `/api/story/progress` | account-wide legacy | ✗ | promote PSP.story_progress + strict read + frontend includes server_id |
| `/api/user/equipment` | account-wide legacy | ✗ | server_id su entries + strict reads + migration pack |

**Vincoli rispettati:**
- `explicit_no_false_readiness=true`
- `explicit_no_filter_applied_emitted_in_this_pack=true`
- `explicit_no_schema_migration_in_this_pack=true`
- `explicit_no_runtime_writes_in_this_pack=true`

---

## Data Invariants

| Mutation Class | Value |
|----------------|-------|
| `account_wide_team_fallback_when_server_id` | **false** |
| `writes_to_users_team_formation_in_server_scoped_flow` | **false** |
| `fake_team` | **false** |
| `fallback_global_roster_or_team` | **false** |
| `overwrite_existing_team` | **false** |
| `copy_s1_to_s2` | **false** |
| `user_heroes_mutation_outside_pack_87_starter_smoke` | **false** |
| `inventory_currency_story_equipment_mutation` | **false** |
| `bulk_psp_apply` | **false** |
| `physical_normalization` | **false** |
| `legacy_cleanup_executed` | **false** |
| `destructive_migration` | **false** |
| `delete_of_real_psp` | **false** |
| `delete_of_real_user_heroes` | **false** |
| `reward_live` | **false** |
| `progress_live` | **false** |
| `premium_grant` | **false** |
| `player_level_mutation` | **false** |
| `release_readiness_claimed` | **false** |

---

## Cleanup / Rollback Strategy

**Script:** `backend/scripts/cleanup_v110_pack_88_test_artifacts.py`

- Refuse-by-default, dry-run default, `--apply` required.
- Markers: `users.email LIKE 'pack88_test_user_%@test.com'`, `player_server_profiles.server_id LIKE 's_pack88_%'`.
- No deletion of real production data.

---

## Live Readiness Update

| Surface | Live? |
|---------|-------|
| `team_formation_strict_server_scope_backend_ready` | **true** |
| `team_formation_account_wide_fallback_removed_with_server_id` | **true** |
| `pack_87_starter_team_preserved` | **true** |
| `core_loader_promotion_prep_documented` | **true** |
| `inventory_psp_scoped_loader_ready` | **false** (prep only) |
| `currencies_psp_scoped_loader_ready` | **false** (prep only) |
| `story_psp_scoped_loader_ready` | **false** (prep only) |
| `equipment_psp_scoped_loader_ready` | **false** (prep only) |
| `reward_live` | **false** |
| `progress_live` | **false** |
| **`release_readiness_claimed`** | **false** |

---

## MD5 Rebase

| File | From MD5 | To MD5 | Reason |
|------|----------|--------|--------|
| `backend/routes/v96_team_formation.py` | `b44b52c9da683ffdcaa7abfa0fbb484a` (Pack 87) | `eecbaaf4797a43dc69ae9635125142b6` (Pack 88) | STRICT server-scoped rewrite |

**Validatori riallineati (NO weakening):**
- `validate_v110_team_formation_route_hardening.py` — Pack 88 tokens additive (`pack_88_strict_server_scope`, `PLAYER_SERVER_PROFILE_REQUIRED`, `player_server_profile`, `legacy_account_team_used`). Tutti i check originali (no db writes, blocker presenti, source PSP-aware) preservati. La check `filter_applied=bool(server_id)` (legacy) sostituita da check espliciti `filter_applied=True` (strict) E `filter_applied=False` (legacy non-player-facing) — entrambi i casi tracciati.

---

## Gate / Runtime Invariant Preservation

| Pack / Gate | Preserved? |
|-------------|-----------|
| POSTQA_D gates | **locked** |
| Pack 80 lobby fetch | **YES** |
| Pack 81 user_heroes server-scope | **YES** |
| Pack 82 dual-read PSP | **YES** |
| Pack 84 normalized PSP | **YES** |
| Pack 85 backend ensure | **YES** |
| Pack 86 register guard | **YES** |
| Pack 86 UI ensure | **YES** |
| Pack 87 starter flow | **YES** |
| v107D / v108 POSTQA-A | **YES** |
| Battle engine formula rewrite | **NO** |
| `/api/battle/simulate` da staging/live | **NO** |
| `fake_PASS` / `validator_weakening` | **NO** |

---

## Safety Flags (tutti `false`)

```
fake_PASS                                            = false
validator_weakening                                  = false
release_readiness_claimed                            = false
account_wide_team_fallback_with_server_id            = false
writes_to_users_team_formation_in_server_scoped_flow = false
fake_team                                            = false
fallback_global_roster_or_team                       = false
overwrite_existing_team                              = false
copy_s1_to_s2                                        = false
inventory_currency_story_equipment_mutation          = false
bulk_psp_apply                                       = false
physical_normalization_executed_in_this_pack         = false
destructive_migration                                = false
delete_of_real_data                                  = false
reward_live                                          = false
progress_live                                        = false
premium_grant                                        = false
player_level_mutation                                = false
postqa_d_gates_unlocked                              = false
battle_engine_formula_rewrite                        = false
battle_simulate_called_from_staging_or_live          = false
legacy_cleanup_executed                              = false
```

---

## Explicit Statements

1. **No account-wide team fallback with `server_id`** — verificato runtime con iniezione `user.team_formation` legacy; team route ritorna blocker su PSP missing/empty senza leak. ✓
2. **No `users.team_formation` writes in server-scoped flow** — verificato statico in `psp_starter_claim` e in `v96_team_formation.py`. ✓
3. **Pack 87 starter team preserved** — runtime smoke verifica che team_source resta `player_server_profile` con 3 starter dopo claim, re-claim no overwrite. ✓
4. **Reward/progress live OFF** — `reward_live=false`, `progress_live=false`. ✓
5. **Legacy cleanup NOT executed** — `legacy_cleanup_executed=false`, cleanup script refuse-by-default + dry-run. ✓

---

## Deferred Blockers / Next Step

**Deferred:**
- Core loaders `/api/inventory`, `/api/currencies`, `/api/story/progress`, `/api/user/equipment` — readiness prep documentato, runtime promotion deferred.
- Legacy cleanup pre-Pack-86 account-wide `user_heroes` — OUT OF SCOPE.
- Legacy cleanup `users.team_formation` campo — lasciato come legacy non-player-facing (no destructive migration).
- Reward/progress live — restano `OFF`.

**Next step recommendation:**

> **NON procedere a Pack 89 senza upload esplicito del prossimo ZIP e relativa stringa di autorizzazione.**

Possibili direzioni candidate:

1. **Inventory PSP-scoped loader promotion** (con autorizzazione esplicita).
2. **Currencies PSP-scoped loader promotion** (con currency class mapping).
3. **Story progress PSP-scoped loader promotion**.
4. **Equipment PSP-scoped loader promotion**.
5. **Legacy cleanup migration pack** per pre-Pack-86 account-wide `user_heroes` (destructive migration autorizzata).

In attesa della verifica utente / sync pubblica della piattaforma prima di marcare definitivamente Pack 88 come `APPROVED`.

---

**END OF REPORT — Pack 88 (`MEGA_RELEASE_ACCELERATION_88_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PROMOTION_PREP`)**
