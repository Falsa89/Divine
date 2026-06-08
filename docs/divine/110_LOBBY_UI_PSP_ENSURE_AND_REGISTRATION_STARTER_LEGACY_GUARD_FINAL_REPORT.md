# Pack 86 — Lobby UI PSP Ensure + Registration Starter Legacy Guard — Final Report

**Pack ID:** `MEGA_RELEASE_ACCELERATION_86_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD`
**Generated UTC:** 2026-06-08
**Verdict:** `MEGA_RELEASE_ACCELERATION_86_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Verdict

Pack 86 chiuso con esito **READY** sotto vincoli strict-mode. La UI player-facing
ora chiama `POST /api/psp/ensure?server_id=<sid>` quando l'utente entra in un
server, e `/api/register` non crea più starter `user_heroes` account-wide per
default (gated dietro flag dev-only `REGISTER_LEGACY_STARTER_HEROES_ENABLED`).
Master suite 3-run deterministica: **1427 PASS / 29 OPTIONAL FAIL (= baseline)
/ 0 MISS / 0 REQUIRED FAIL**. ZERO copia S1→S2, ZERO reward/progress live,
ZERO legacy cleanup, ZERO starter heroes grant, ZERO premium grant.

---

## Commit Hash

- **Commit hash locale Pack 86:** `e2a13ebe10437ceb4a5f17e1eeb427b5caca266d`
- **Commit hash precedente Pack 85:** `df4f00364cafc485a90fd3ed3bbd5c3690b3946d`
- **Sync status:** `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`

---

## Git Diff Stat

```
backend/server.py                                                            | +30/-15 lines (additive register guard + response signals)
frontend/app/servers.tsx                                                     | +47 lines (onEnter -> POST /api/psp/ensure)
frontend/app/pre-battle-lobby.tsx                                            | +35 lines (defensive ensure useEffect)
backend/scripts/run_hero_skill_kit_validator_suite.py                        | +14 lines (Pack 86 14 new tracks)
backend/scripts/validate_v110_pack_86_*.py                                   | +13 file (nuove validator track)
backend/scripts/validate_mega_release_acceleration_86_*.py                   | +1 file (rollup)
backend/scripts/cleanup_v110_pack_86_test_artifacts.py                       | +1 file (refuse-by-default cleanup)
backend/scripts/validate_v110_pack_79_runtime_real.py                        | +/- 4 lines (ACCEPTED_LOBBY_MD5S set extended)
backend/scripts/validate_v110_lobby_team_fetch_md5_rebase.py                 | +/- 6 lines (ACCEPTED_LOBBY_MD5S set + Pack 79 substring check)
backend/scripts/validate_v110_pack_81_md5_rebase.py                          | +/- 8 lines (dual-read lobby MD5 via v100 baseline)
data/design/closed_alpha/v100_runtime_md5_baseline_v1.json                   | +/- 20 lines (rebase server.py + pre-battle-lobby.tsx with historical refs)
data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json   | +/- 12 lines (rebase + new chain entry)
data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json | +/- 12 lines (rebase + new chain entry)
data/design/v110_pack_86_lobby_psp_ensure/                                   | +14 file (nuove design JSON)
docs/divine/110_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD_FINAL_REPORT.md | +1 file (questo report)
```

---

## Baseline / Final 3-Run Suite

| Run | Pass  | Fail (OPTIONAL) | Miss | Required Fail |
|-----|-------|------------------|------|---------------|
| baseline_pre_pack_run1/2/3 | 1413 | 29 | 0 | 0 |
| final_post_pack_run1 | **1427** | 29 | 0 | **0** |
| final_post_pack_run2 | **1427** | 29 | 0 | **0** |
| final_post_pack_run3 | **1427** | 29 | 0 | **0** |
| delta | **+14** | 0 | 0 | **0** |

- **Determinismo:** `run1 == run2 == run3 == 1427 PASS`
- **REQUIRED FAIL:** `0` su tutti i run ✓
- **MISS:** `0` su tutti i run ✓
- **OPTIONAL FAIL:** invariato a `29` (= baseline, zero regressioni)
- **14 nuove Pack 86 track: tutte PASS in tutti i 3 run**

---

## Route / UI Map

| Path | File | Func | Pack |
|------|------|------|------|
| `POST /api/psp/ensure?server_id=<sid>` | `backend/server.py` | `psp_ensure_fresh_start` | Pack 85 (preserved) |
| Frontend onEnter → POST /api/psp/ensure | `frontend/app/servers.tsx` | `onEnter` | **Pack 86** |
| Frontend lobby defensive ensure | `frontend/app/pre-battle-lobby.tsx` | `useEffect [selectedServerLoaded, selectedServerId, backendUrl]` | **Pack 86** |
| `POST /api/register` (guarded) | `backend/server.py` | `register` | **Pack 86 modified** |

---

## Lobby / Server-Entry PSP Ensure Integration

### Primary call site — `frontend/app/servers.tsx::onEnter`

- Triggered quando l'utente preme **Entra** su un server card.
- Dopo `AsyncStorage.setItem('v101_selected_server_id', s.server_id)` e PRIMA di `router.replace('/(tabs)/home')`.
- Chiama `POST /api/psp/ensure?server_id=<s.server_id>` con `Authorization: Bearer <v96_auth_token>` (da SecureStore).
- Header marker: `X-Pack-86-Frontend-Ensure: true`.
- On success: scrive in AsyncStorage `pack86_psp_ensure_last_mode` (`fresh_start_created` | `already_exists_no_write`) e `pack86_psp_ensure_last_server_id`.
- On failure: **NO global fallback**, **NO fake team**, **NO copy S1→S2**. Lobby downstream mostrerà blocker onesti.

### Defensive call site — `frontend/app/pre-battle-lobby.tsx`

- `useEffect` dipendente da `[selectedServerLoaded, selectedServerId, backendUrl]`.
- Chiama `POST /api/psp/ensure` in modo idempotente (backend Pack 85 ritorna `already_exists_no_write` se PSP esiste).
- Copre deep-link / hot-reload / navigation diretta che bypassa `servers.tsx`.
- Header marker: `X-Pack-86-Lobby-Defensive-Ensure: true`.

### Invariants

| Property | Value |
|----------|-------|
| Explicit `server_id` | ✓ |
| Bearer required | ✓ |
| Idempotent | ✓ |
| Silent `s1` | ✗ |
| Global fallback on failure | ✗ |
| Fake team on failure | ✗ |
| Copy S1→S2 | ✗ |

---

## Register Starter Legacy Guard

| Field | Value |
|-------|-------|
| Pre-Pack-86 behavior | Created 3 random 1-2★ heroes as account-wide `user_heroes` (no `server_id`) |
| Pack-86 behavior | **starter creation DISABLED by default**. Gated dietro `REGISTER_LEGACY_STARTER_HEROES_ENABLED=true` (default OFF). Marked deprecated. **NOT player-facing production path**. **NEVER claimed as final roster source**. |
| Response additions | `server_onboarding_required: true`, `starter_flow_required: true`, `starter_legacy_created_in_register: 0`, `_slc_pack_86_register_starter_legacy_guard: true` |
| Marker su user_heroes creati (solo se flag dev-only attivo) | `_slc_pack_86_legacy_dev_only_starter: true` |
| Premium grant | ✗ |
| Reward grant | ✗ |

### Smoke test verificato runtime

- POST `/api/register` con email `pack86_test_user_<ts>@test.com` → response `starter_legacy_created_in_register=0`, `server_onboarding_required=true`, `starter_flow_required=true`.
- DB `user_heroes` count per nuovo registrante: **0**.

---

## Backend Ensure Hardening

**NESSUNA modifica al route ensure in Pack 86** — l'implementazione Pack 85 già rispetta:

- ✓ No silent `s1` (`server_id` required + validato).
- ✓ Explicit `server_id` required (blocker `SERVER_ID_REQUIRED` se mancante).
- ✓ Idempotent (`find_one` → `insert_one` solo se mancante).
- ✓ Fresh-start fields corretti (`player_level=1`, `player_exp=0`, `team_formation=[]`).
- ✓ No S1 copy (nessuna read di altri server prima dell'insert).
- ✓ No `user_heroes` creation.
- ✓ No reward.
- ✓ No mutation of existing PSP.
- ✓ No cross-server read.

---

## `/api/user/heroes` + Team After Ensure

| Phase | X-Blocker | X-Filter-Applied | X-PSP-Lookup-Mode | X-Player-Level | X-Player-Exp | Roster |
|-------|-----------|------------------|-------------------|----------------|--------------|--------|
| Pre-ensure (new server) | `PLAYER_SERVER_PROFILE_REQUIRED` | `false` | — | `1` | `0` | 0 |
| Post-ensure (new server) | (empty) | **`true`** | **`direct_uuid`** | **`1`** | **`0`** | 0 |

| Team | Value |
|------|-------|
| `GET /api/team/get-formation?server_id=<new_sid>` | `team_formation: []` (team-not-configured honest) |
| Global fallback | ✗ |

---

## Runtime Smoke E2E

Eseguito con runtime real (curl + Bearer) via `validate_v110_pack_86_runtime_smoke_e2e.py`:

| Step | Result |
|------|--------|
| 1. POST `/api/register` (nuovo utente) → 0 user_heroes account-wide | ✓ |
| 2. POST `/api/psp/ensure?server_id=<test_sid>` → `created=true`, `level=1`, `exp=0`, `no_cross_server_copy=true` | ✓ |
| 3. GET `/api/user/heroes?server_id=<test_sid>` → `direct_uuid`, `filter_applied=true`, roster=0 | ✓ |
| 4. GET `/api/team/get-formation?server_id=<test_sid>` → `team_formation=[]` | ✓ |
| 5. POST `/api/psp/ensure` (re-call) → `created=false`, `already_existed=true`, mode=`already_exists_no_write` | ✓ |
| 6. Cleanup test user + test PSP | ✓ |

**Verdict smoke:** `PACK_86_RUNTIME_SMOKE_E2E_PASS_REGISTER_NO_GLOBAL_STARTER_UI_ENSURE_INTEGRATED_NEW_SERVER_FRESH_START_NO_S1_TO_S2_COPY`

---

## Data Invariants

| Mutation Class | Value |
|----------------|-------|
| `bulk_psp_apply` | **false** |
| `physical_normalization_executed_in_this_pack` | **false** |
| `legacy_cleanup_executed` | **false** |
| `user_heroes_writes_from_register` | **0** |
| `starter_heroes_created` | **false** |
| `starter_flow_approved` | **false** |
| `player_level_mutation_on_existing_psp` | **false** |
| `copy_s1_to_s2` | **false** |
| `inventory_mutation` | **false** |
| `story_mutation` | **false** |
| `equipment_mutation` | **false** |
| `reward_live` | **false** |
| `progress_live` | **false** |
| `premium_grant` | **false** |
| `destructive_migration` | **false** |
| `delete_of_real_psp` | **false** |
| `battle_history_writes` | **0** |
| `net_users_delta` (post smoke cleanup) | **0** |
| `net_psp_delta` (post smoke cleanup) | **0** |

---

## Cleanup / Rollback Strategy

**Script:** `backend/scripts/cleanup_v110_pack_86_test_artifacts.py`

| Property | Value |
|----------|-------|
| Refuse-by-default | ✓ |
| Dry-run default | ✓ |
| Requires explicit `--apply` flag | ✓ |
| Deletes only marked Pack 86 test artifacts | ✓ |
| No deletion of real production PSP | ✓ |
| Refuse if target count = 0 | ✓ |
| Refuse if target appears real user | ✓ |

**Markers identificativi:**

- `users.email LIKE 'pack86_test_user_%@test.com'`
- `user_heroes._slc_pack_86_legacy_dev_only_starter = true` (solo se flag dev attivo)
- `player_server_profiles.server_id LIKE 's_pack86_%'`

---

## Live Readiness Update

| Surface | Live? |
|---------|-------|
| `new_server_psp_ensure_backend_ready` | **true** |
| `new_server_psp_ensure_frontend_ready` | **true** |
| `registration_global_starter_guard_active` | **true** |
| `starter_flow_ready` | **false** |
| `reward_live` | **false** |
| `progress_live` | **false** |
| `ledger_live` | **false** |
| `battle_engine_authoritative_live` | **false** |
| `legacy_cleanup_executed` | **false** |
| **`release_readiness_claimed`** | **false** |

---

## MD5 Rebase

| File | From MD5 | To MD5 | Reason |
|------|----------|--------|--------|
| `backend/server.py` | `2ec8fcd03aac47e50ae3eb495783ef16` (Pack 85) | `272c70b37190e1fa8b6e712e83fdda83` (Pack 86) | Register starter legacy guard + response signals |
| `frontend/app/pre-battle-lobby.tsx` | `f8b770a118548602a7f680f59b6c409c` (Pack 80) | `4c720c53a29ca2a7fee4ca821221b479` (Pack 86) | Defensive ensure useEffect |
| `frontend/app/servers.tsx` | (pre-Pack-86 baseline) | `91dc7f8c8f49934453b35a09cc9eaeab` (Pack 86) | onEnter → POST `/api/psp/ensure` |

**Tracking files aggiornati con storico preservato:**

- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json`
- `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json`

**Validatori estesi (set-based, NO weakening):**

- `validate_v110_pack_79_runtime_real.py` — `ACCEPTED_LOBBY_MD5S = {Pack 80 baseline, Pack 86}`
- `validate_v110_lobby_team_fetch_md5_rebase.py` — `ACCEPTED_LOBBY_MD5S` set + Pack 79 substring check
- `validate_v110_pack_81_md5_rebase.py` — dual-read lobby MD5 via v100 baseline `current_md5` + `historical_references`

**Replacement invariant funzionale:**

- `/api/psp/ensure` available and safe ✓
- Register no longer creates account-wide `user_heroes` ✓
- Lobby/server-entry calls ensure ✓
- No fake team/roster ✓
- No validator weakening ✓

---

## Gate / Runtime Invariant Preservation

| Pack / Gate | Preserved? |
|-------------|-----------|
| POSTQA_D gates | **locked (unchanged)** |
| Pack 80 lobby fetch | **YES** |
| Pack 81 user_heroes server-scope | **YES** |
| Pack 82 dual-read PSP | **YES** |
| Pack 84 normalized PSP state | **YES** |
| Pack 85 backend ensure | **YES** |
| v107D binding | **YES** |
| v108 POSTQA-A blockers | **YES** |
| Battle engine formula rewrite | **NO** |
| `/api/battle/simulate` da staging/live | **NO** |
| `fake_PASS` | **NO** |
| `validator_weakening` | **NO** |

---

## Safety Flags (tutti `false`)

```
fake_PASS                                            = false
validator_weakening                                  = false
release_readiness_claimed                            = false
production_apply_executed                            = false
bulk_psp_apply                                       = false
physical_normalization_executed_in_this_pack         = false
destructive_migration                                = false
delete_of_real_psp                                   = false
premium_grant                                        = false
reward_live                                          = false
progress_live                                        = false
legacy_cleanup_executed                              = false
starter_heroes_grant                                 = false
starter_flow_approved                                = false
copy_s1_to_s2                                        = false
account_wide_player_level_as_final_server_level      = false
account_wide_roster_as_final_server_roster           = false
postqa_d_gates_unlocked                              = false
battle_engine_formula_rewrite                        = false
battle_simulate_called_from_staging_or_live          = false
user_heroes_creation_from_register                   = false
```

---

## Explicit Statements (Required by Authorization String)

1. **No global starter `user_heroes` from register** — `starter_legacy_created_in_register=0` (default), DB count post-register verificato = 0. ✓
2. **New server starts level 1** — `player_level=1`, `player_exp=0` (PSP fresh-start). ✓
3. **No S1→S2 copy** — `copy_s1_to_s2=false`, `no_cross_server_copy=true`. ✓
4. **Reward/progress live OFF** — `reward_live=false`, `progress_live=false`. ✓
5. **Legacy cleanup NOT executed** — `legacy_cleanup_executed=false`, cleanup script refuse-by-default + dry-run + explicit `--apply` required. ✓

---

## Remaining / Deferred Blockers (documented honestly)

- **Starter flow (server-scoped onboarding)** — NON approvato in Pack 86. Starter heroes assignment deferred a pack dedicato.
- **Inventory / currencies / story_progress / equipment PSP-scoped loader promotion** — DEFERRED.
- **Reward / progress live** — restano `OFF`.
- **Legacy cleanup** — NON eseguito (no destructive migration).
- **Pre-existing legacy `user_heroes` account-wide** creati prima di Pack 86 restano nel DB — OUT OF SCOPE (Pack 86 blocca solo nuova creazione; cleanup richiederà pack legacy-cleanup separato e approvato).

---

## Next Step Recommendation

> **NON procedere a Pack 87 senza upload esplicito del prossimo ZIP e relativa stringa di autorizzazione.**

Possibili direzioni candidate (a discrezione utente):

1. **Starter flow approval & implementation** — definizione esplicita schema starter heroes/team server-scoped, con grant nel contesto onboarding (NON account-wide).
2. **Inventory/currencies/story_progress/equipment PSP-scoped loader promotion** — prossimo step di server-scoping SOT.
3. **Legacy cleanup migration** — pack dedicato per gestire i pre-existing `user_heroes` account-wide creati pre-Pack-86 (con autorizzazione esplicita destructive migration).

In attesa della verifica utente / sync pubblica della piattaforma prima di marcare definitivamente Pack 86 come `APPROVED`.

---

**END OF REPORT — Pack 86 (`MEGA_RELEASE_ACCELERATION_86_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD`)**
