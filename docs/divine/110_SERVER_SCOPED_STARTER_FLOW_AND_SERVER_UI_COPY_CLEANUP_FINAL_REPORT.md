# Pack 87 — Server-Scoped Starter Flow + Server UI Copy Cleanup — Final Report

**Pack ID:** `MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_SERVER_SCOPED_STARTER_FLOW_AND_UI_COPY_CLEANUP`
**Authorization:** `AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87`
**Generated UTC:** 2026-06-08
**Verdict:** `MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Verdict

Pack 87 chiuso con esito **READY** sotto vincoli strict-mode con autorizzazione esplicita
`AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87`. Il primo starter flow **server-scoped**
è ora implementato end-to-end: backend endpoint idempotente `POST /api/psp/starter/claim`,
team initialization sicura (solo se vuoto), integrazione UI (servers.tsx::onEnter dopo
ensure), cleanup della stale UI copy. Master suite 3-run deterministica:
**1443 PASS / 29 OPTIONAL FAIL (= baseline) / 0 MISS / 0 REQUIRED FAIL**.

---

## Commit Hash

- **Commit hash locale Pack 87:** `fe6ef69d001859f56a444de7f63076563a992b00`
- **Commit hash precedente Pack 86:** `e2a13ebe10437ceb4a5f17e1eeb427b5caca266d`
- **Sync status:** `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`

---

## Git Diff Stat

```
backend/server.py                                                            | +175 lines (psp_starter_claim endpoint)
backend/routes/v96_team_formation.py                                         | +20/-5 lines (PSP team_formation read, dual-read fix)
frontend/app/servers.tsx                                                     | +45/-6 lines (starter/claim call + UI copy cleanup)
backend/scripts/run_hero_skill_kit_validator_suite.py                        | +16 lines (Pack 87 16 new tracks)
backend/scripts/validate_v110_pack_87_*.py                                   | +15 file (nuove validator track)
backend/scripts/validate_mega_release_acceleration_87_*.py                   | +1 file (rollup)
backend/scripts/cleanup_v110_pack_87_test_artifacts.py                       | +1 file (refuse-by-default cleanup)
backend/scripts/validate_v103_server_naming_status.py                        | +/- 12 lines (Pack 87 UI cleanup token set extended)
backend/scripts/validate_v104_server_scoped_data_flow_audit.py               | +/- 20 lines (banner token set extended)
backend/scripts/validate_v104_server_naming_canonicalization.py              | +/- 12 lines (banner token set extended)
data/design/closed_alpha/v100_runtime_md5_baseline_v1.json                   | +/- 7 lines (server.py md5 rebase + Pack 86 historical ref)
data/design/v110_pack_87_server_scoped_starter_flow/                         | +17 file (design JSON + SOT)
docs/divine/113_CANON_SERVER_SCOPED_STARTER_FLOW.md                          | +1 file (canon SOT MD)
docs/divine/110_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP_FINAL_REPORT.md | +1 file (questo report)
```

---

## Baseline / Final 3-Run Suite

| Run | Pass  | Fail (OPTIONAL) | Miss | Required Fail |
|-----|-------|------------------|------|---------------|
| baseline_pre_pack_run1/2/3 | 1427 | 29 | 0 | 0 |
| final_post_pack_run1 | **1443** | 29 | 0 | **0** |
| final_post_pack_run2 | **1443** | 29 | 0 | **0** |
| final_post_pack_run3 | **1443** | 29 | 0 | **0** |
| delta | **+16** | 0 | 0 | **0** |

- **Determinismo:** `run1 == run2 == run3 == 1443 PASS`
- **REQUIRED FAIL:** `0` su tutti i run ✓
- **MISS:** `0` su tutti i run ✓
- **OPTIONAL FAIL:** invariato a `29` (= baseline, zero regressioni)
- **16 nuove Pack 87 track: tutte PASS in tutti i 3 run**

---

## Starter Flow SOT (Canon)

**File canon:** `docs/divine/113_CANON_SERVER_SCOPED_STARTER_FLOW.md`
**JSON canon:** `data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_canon_starter_flow_sot_v1.json`

Decisione canonica:

> Gli starter heroes del player sono **SERVER-SCOPED**. La registrazione account NON
> assegna roster globale operativo (preservato da Pack 86). Lo starter roster viene
> assegnato **SOLO** nel contesto `(authenticated_user_id, selected_server_id)`,
> idempotentemente, **una sola volta per server**.

---

## Route + Legacy Starter Audit

| Surface | File | Pack | Stato |
|---------|------|------|-------|
| `POST /api/register` (legacy starter) | `backend/server.py` | Pack 86 (guarded) | Starter creation DISABLED by default. Pack 87 starter flow è il replacement. |
| Hero catalog audit (rarity ≤ 2, official, obtainable, catalog, non-deactivated, non-premium) | `db.heroes` | Pack 87 | 20 heroes eligible, 3 starter selezionati con marker low-rarity ufficiali. |
| `POST /api/psp/ensure` | `backend/server.py::psp_ensure_fresh_start` | Pack 85 (preserved) | Idempotent PSP fresh-start. |
| `POST /api/psp/starter/claim` | `backend/server.py::psp_starter_claim` | **Pack 87** | Idempotent server-scoped starter claim. |
| `GET /api/user/heroes?server_id=<sid>` | `backend/server.py` | Pack 81 (preserved) | Server-scoped roster read. |
| `GET /api/team/get-formation?server_id=<sid>` | `backend/routes/v96_team_formation.py` | Pack 87 (extended) | Ora legge PSP.team_formation se popolato (Pack 87 init). |
| `frontend/app/servers.tsx::onEnter` | frontend | Pack 86 + **Pack 87** | Chiama ensure → starter/claim → home. |

---

## Starter Roster Policy

| Slot | Hero ID | Nome | Rarity | Element | Ruolo |
|------|---------|------|--------|---------|-------|
| 1 | `greek_phalanx_recruit`    | Recluta di Falange     | 1★ | earth | **tank**    |
| 2 | `celtic_forest_archer`     | Arciera di Bosco       | 1★ | wind  | **dps**     |
| 3 | `angelic_sanctuary_acolyte`| Accolita del Santuario | 1★ | light | **support** |

**Eligibility (verificato runtime via audit catalog):**

- `rarity ≤ 2` ✓
- `is_official: true` ✓
- `show_in_catalog: true` ✓
- `obtainable: true` ✓
- `deactivated_at in {None, ""}` ✓
- `is_premium not true` ✓
- Nessun 5★/6★ ✓
- Nessuna Borea / hero premium ✓

**Refuse-by-default audit:** Se un hero ID non rispetta la policy, l'endpoint ritorna esplicitamente uno di:
`STARTER_ROSTER_NOT_CATALOGED`, `STARTER_ROSTER_HIGH_RARITY`, `STARTER_ROSTER_NOT_OFFICIAL`,
`STARTER_ROSTER_NOT_OBTAINABLE`, `STARTER_ROSTER_NOT_CATALOG_VISIBLE`, `STARTER_ROSTER_DEACTIVATED`,
`STARTER_ROSTER_PREMIUM_FORBIDDEN`. **NO silent invention.**

---

## Starter Config

`data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_starter_config_v1.json`

```
starter_set_id = "pack_87_default_starter_set"
server_scoped = true
claim_once_per_server = true
allow_duplicate_on_same_server = false
no_equipment = true
no_currency = true
no_inventory_reward = true
no_story_reward = true
no_player_level_mutation = true
no_s1_to_s2_copy = true
no_overwrite_existing_team = true
team_init_only_if_empty = true
premium = false
max_rarity_allowed = 2
```

---

## Backend Starter Claim Endpoint

**Path:** `POST /api/psp/starter/claim?server_id=<sid>`
**File:** `backend/server.py::psp_starter_claim`

| Property | Value |
|----------|-------|
| Auth (Bearer JWT) | Required |
| `server_id` required | ✓ (blocker `SERVER_ID_REQUIRED` se mancante) |
| Requires existing PSP | ✓ (blocker `PLAYER_SERVER_PROFILE_REQUIRED` se mancante) |
| Idempotent | ✓ (marker `_slc_pack_87_starter_claim_marker` su PSP) |
| `user_heroes` created with `server_id` | ✓ MANDATORY |
| `creation_source` | `server_scoped_starter_flow_pack_87` |
| `level=1`, `experience=0`, `stars` da catalogo | ✓ |
| Authorization marker per `user_hero` | `_slc_pack_87_authorization=AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87` |
| Audit hero ID via catalog | ✓ refuse-by-default |
| Account-wide user_heroes | ✗ |
| Premium currency / hard currency / inventory / equipment / story reward | ✗ |
| `player_level` mutation | ✗ |
| Copy S1→S2 | ✗ |
| Headers di risposta | `X-Starter-Claim-Mode`, `X-Server-Id` |

---

## Team Initialization

| Property | Value |
|----------|-------|
| Init solo se `PSP.team_formation` vuoto | ✓ |
| Init SOLO con `user_hero_id` appena creati | ✓ |
| Stesso `server_id` | ✓ |
| Mongo conditional update con `team_formation: {$in: [None, []]}` | ✓ |
| Mai overwrite team esistente | ✓ |
| Mai fake team | ✓ |
| Mai copia da altri server | ✓ |
| Marker per slot init | `_slc_pack_87_starter_team_init=true` |
| Marker PSP team init | `_slc_pack_87_team_initialized_from_starter=true` |

---

## Frontend / Onboarding Integration

**File:** `frontend/app/servers.tsx::onEnter`

```
Sequence:
1. AsyncStorage.setItem('v101_selected_server_id', s.server_id)
2. POST /api/psp/ensure?server_id=<sid>      (Pack 86)
3. POST /api/psp/starter/claim?server_id=<sid>  (Pack 87)
4. AsyncStorage.setItem('pack87_starter_claim_last_mode', ...)
5. AsyncStorage.setItem('pack87_starter_user_hero_ids', JSON.stringify(...))
6. router.replace('/(tabs)/home')
```

| Property | Value |
|----------|-------|
| Bearer required | ✓ (`v96_auth_token` da SecureStore) |
| Header marker | `X-Pack-87-Frontend-Starter-Claim: true` |
| Explicit `server_id` | ✓ |
| Global fallback su failure | ✗ |
| Idempotent (via backend marker) | ✓ |

---

## Server UI Copy Cleanup

**File:** `frontend/app/servers.tsx` (banner fallback section)

| Stato | Testo |
|-------|-------|
| **Pre-Pack-87 (stale)** | `SERVER_DATA_ISOLATION_BACKEND_PENDING · Server isolation backend (per_server_id account/inventory/team/chat) PENDING. Tutti i server caricheranno lo stesso account corrente finché il backend multi-shard non è attivo. Nessuna finzione di separazione.` |
| **Post-Pack-87 (honest)** | `Pack 85-87 attivi: account identity condivisa tra server; profilo giocatore, roster e progressione sono server-scoped. Entrare in un nuovo server crea un PSP fresh-start (livello 1, exp 0) senza copia da altri server. Inventario, valute, story e equipment restano ancora deferred. Nessuna finzione di separazione.` |

**Verifica statica:**
- `SERVER_DATA_ISOLATION_BACKEND_PENDING` count post-Pack-87 = **0** ✓
- `tutti i server caricheranno lo stesso account corrente` count post-Pack-87 = **0** ✓
- New honest banner key phrase `Pack 85-87 attivi` count = **1** ✓

---

## Runtime Smoke E2E

Eseguito con runtime real (curl + Bearer) via `validate_v110_pack_87_runtime_smoke_e2e.py`:

| Step | Result |
|------|--------|
| 1. POST `/api/register` (nuovo utente) → `starter_legacy_created_in_register=0`, DB user_heroes=0 | ✓ |
| 2. POST `/api/psp/ensure?server_id=<new_sid>` → `created=true`, level=1, exp=0 | ✓ |
| 3. POST `/api/psp/starter/claim?server_id=<new_sid>` → `created=true`, 3 starter user_heroes (server_id, creation_source=pack_87), team_initialized=true | ✓ |
| 4. Verifica DB: tutti `user_heroes` includono `server_id` corretto, `creation_source=server_scoped_starter_flow_pack_87`, `level=1`, `experience=0` | ✓ |
| 5. GET `/api/user/heroes?server_id=<new_sid>` → `X-Filter-Applied=true`, `X-PSP-Lookup-Mode=direct_uuid`, roster=3 | ✓ |
| 6. GET `/api/team/get-formation?server_id=<new_sid>` → `team_formation` con 3 starter | ✓ |
| 7. POST `/api/psp/starter/claim` (re-call) → `created=false`, `already_claimed=true`, mode=`already_claimed_no_write`, 0 nuovi writes | ✓ |
| 8. POST `/api/psp/starter/claim` su server DIVERSO (senza ensure) → blocker `PLAYER_SERVER_PROFILE_REQUIRED` | ✓ |
| 9. Cleanup test user + starter user_heroes + test PSP | ✓ |

**Verdict smoke:** `PACK_87_RUNTIME_SMOKE_E2E_PASS_SERVER_SCOPED_STARTER_FLOW_NO_ACCOUNT_WIDE_NO_S1_TO_S2_COPY_IDEMPOTENT`

---

## Data Invariants

| Mutation Class | Value |
|----------------|-------|
| `account_wide_starter_from_register` | **false** |
| `starter_user_heroes_only_on_selected_server` | **true** ✓ |
| `all_starter_user_heroes_include_server_id` | **true** ✓ |
| `all_starter_user_heroes_creation_source=server_scoped_starter_flow_pack_87` | **true** ✓ |
| `copy_s1_to_s2` | **false** |
| `player_level_mutation` | **false** |
| `premium_currency_grant` | **false** |
| `hard_currency_grant` | **false** |
| `inventory_grant` | **false** |
| `equipment_grant` | **false** |
| `story_reward_grant` | **false** |
| `legacy_cleanup_executed` | **false** |
| `destructive_migration` | **false** |
| `delete_of_real_psp` | **false** |
| `bulk_psp_apply` | **false** |
| `physical_normalization_executed_in_this_pack` | **false** |
| `team_overwrite_existing` | **false** |
| `team_init_only_if_empty` | **true** ✓ |
| `reward_live` | **false** |
| `progress_live` | **false** |
| `release_readiness_claimed` | **false** |

---

## Cleanup / Rollback Strategy

**Script:** `backend/scripts/cleanup_v110_pack_87_test_artifacts.py`

| Property | Value |
|----------|-------|
| Refuse-by-default | ✓ |
| Dry-run default | ✓ |
| Requires explicit `--apply` | ✓ |
| Deletes only marked Pack 87 test artifacts | ✓ |
| No deletion of real production PSP / user_heroes | ✓ |

**Markers:**

- `users.email LIKE 'pack87_test_user_%@test.com'`
- `user_heroes.creation_source='server_scoped_starter_flow_pack_87'` **AND** `user_id IN <test_users>` (safety guard: NO touch starter marker su real users)
- `player_server_profiles.server_id LIKE 's_pack87_%'`

---

## Live Readiness Update

| Surface | Live? |
|---------|-------|
| `server_scoped_starter_flow_backend_ready` | **true** |
| `server_scoped_starter_flow_frontend_ready` | **true** |
| `starter_team_initialization_ready` | **true** |
| `server_ui_stale_copy_cleaned` | **true** |
| `inventory_psp_scoped_loader_ready` | **false** (deferred) |
| `currencies_psp_scoped_loader_ready` | **false** (deferred) |
| `story_psp_scoped_loader_ready` | **false** (deferred) |
| `equipment_psp_scoped_loader_ready` | **false** (deferred) |
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
| `backend/server.py` | `272c70b37190e1fa8b6e712e83fdda83` (Pack 86) | `8e0595aaf398c3ba7dd92b9118d5a528` (Pack 87) | Aggiunto endpoint `psp_starter_claim` |
| `frontend/app/servers.tsx` | `91dc7f8c8f49934453b35a09cc9eaeab` (Pack 86) | `e7b0072ad2d54b5d7a52ec761f66d591` (Pack 87) | Aggiunta chiamata starter/claim + UI cleanup |
| `backend/routes/v96_team_formation.py` | (pre-Pack-87) | `b44b52c9da683ffdcaa7abfa0fbb484a` (Pack 87) | Read PSP.team_formation server-scoped + fix dual-read UUID lookup |
| `frontend/app/pre-battle-lobby.tsx` | `4c720c53a29ca2a7fee4ca821221b479` (Pack 86) | **UNCHANGED** | Non modificato in Pack 87 |

**Tracking files aggiornati con storico preservato:**

- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (server.py rebase + Pack 86 historical reference)

**Validatori v103/v104 (Pack 87 UI cleanup) — token set extended, NO weakening:**

- `validate_v103_server_naming_status.py` — accetta legacy stale token OR Pack 87 honest descriptor
- `validate_v104_server_scoped_data_flow_audit.py` — banner token set extended con `PACK_87_SERVER_SCOPED_UI_COPY_HONEST` + content check accepts both stale or Pack 87
- `validate_v104_server_naming_canonicalization.py` — set-based banner check

**No-weakening proof:** Tutti i check originali (`banner_visible=true`, `no_fake_per_server_data=true`, `fake_PASS=false`, `validator_weakening=false`) sono preservati. La sola estensione è il riconoscimento della legittima cleanup UI Pack 87 (Track H esplicitamente richiesto dal pack).

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
| Pack 86 register guard | **YES** |
| Pack 86 UI ensure | **YES** |
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
starter_heroes_account_wide_grant                    = false
copy_s1_to_s2                                        = false
account_wide_player_level_as_final_server_level      = false
account_wide_roster_as_final_server_roster           = false
postqa_d_gates_unlocked                              = false
battle_engine_formula_rewrite                        = false
battle_simulate_called_from_staging_or_live          = false
user_heroes_creation_from_register                   = false
premium_or_5star_or_6star_starter                    = false
borea_or_premium_hero_in_starter                     = false
inventory_grant_in_starter                           = false
equipment_grant_in_starter                           = false
currency_grant_in_starter                            = false
story_reward_grant_in_starter                        = false
team_overwrite_existing                              = false
player_level_mutation                                = false
```

---

## Explicit Statements

1. **Starter heroes are server-scoped** — `user_heroes` includono MANDATORY `server_id`, `creation_source=server_scoped_starter_flow_pack_87`. ✓
2. **No account-wide starter `user_heroes`** — register guard (Pack 86) preservato + starter claim solo per `(user_id, server_id)`. ✓
3. **New server starts level 1** — PSP fresh-start (Pack 85) + starter `level=1, exp=0`. ✓
4. **No S1→S2 copy** — `_slc_psp_no_cross_server_copy=true`, `no_cross_server_copy=true`. ✓
5. **No premium / currency / equipment / story rewards** — `no_premium_grant=true`, nessuna scrittura su `inventory`, `equipment`, `story_progress`, `currencies`. ✓
6. **Reward/progress live OFF** — `reward_live=false`, `progress_live=false`. ✓
7. **Legacy cleanup NOT executed** — `legacy_cleanup_executed=false`, cleanup script refuse-by-default + dry-run + `--apply` esplicito richiesto. ✓

---

## Deferred Blockers / Next Step

**Deferred (documented):**

- Inventory / currencies / story_progress / equipment PSP-scoped loader promotion — restano DEFERRED.
- Reward / progress live — restano `OFF`.
- Legacy cleanup di `user_heroes` account-wide pre-Pack-86 — OUT OF SCOPE (richiede pack destructive migration separato).
- Lobby defensive starter claim — backend idempotency gestisce re-call safely; defensive UI call può essere aggiunta in pack futuro.
- Starter set composition currently fixed (1★ tank/dps/support); pack futuro può estendere/customizzare.

**Next step recommendation:**

> **NON procedere a Pack 88 senza upload esplicito del prossimo ZIP e relativa stringa di autorizzazione.**

Possibili direzioni candidate:

1. **Inventory / currencies / story_progress / equipment** PSP-scoped loader promotion — prossimo step di server-scoping SOT.
2. **Legacy cleanup migration** — pack dedicato per pre-Pack-86 account-wide `user_heroes` (richiede destructive migration autorizzata).
3. **Starter flow extensions** — set espandibile, scelta starter da UI, customizzazione per tipo server.
4. **Battle engine authoritative live** — verso `release_readiness`.

In attesa della verifica utente / sync pubblica della piattaforma prima di marcare definitivamente Pack 87 come `APPROVED`.

---

**END OF REPORT — Pack 87 (`MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP`)**
