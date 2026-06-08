# Pack 85 — PSP Onboarding New Server Fresh-Start — Final Report

**Pack ID:** `MEGA_RELEASE_ACCELERATION_85_PSP_ONBOARDING_NEW_SERVER_FRESH_START`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_PSP_ONBOARDING_NEW_SERVER_FRESH_START`
**Generated UTC:** 2026-06-08
**Verdict:** `MEGA_RELEASE_ACCELERATION_85_PSP_ONBOARDING_NEW_SERVER_FRESH_START_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## 1. Verdict Riassuntivo

Pack 85 chiuso con esito **POSITIVO** sotto vincoli strict-mode. È stata implementata
la route backend idempotente `POST /api/psp/ensure?server_id=<sid>` che crea un
Player Server Profile (PSP) fresh-start quando un utente autenticato entra in un
nuovo server in cui non ha mai giocato. **ZERO copia cross-server**, **ZERO writes
su `user_heroes`/`users`/`inventory`/`equipment`/`battle_history`**, **ZERO reward
grant**, **ZERO progress live**, **ZERO legacy cleanup**, **ZERO bulk apply**, **ZERO
physical normalization** (Pack 84 già conclusa separatamente).

---

## 2. Commit Locale & Git Diff

- **Sync status:** `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`
- Il container di esecuzione non espone un remote git esterno: il commit è
  esclusivamente locale. La sincronizzazione pubblica sarà gestita dalla
  pipeline di piattaforma post-approvazione esplicita dell'utente.
- Commit hash locale: si veda `git log -1 --format=%H` post-commit (Pack 85 commit).

### git diff --stat (Pack 85 scope)

```
backend/server.py                                                            | +81 lines (additive)
backend/scripts/run_hero_skill_kit_validator_suite.py                        | +12 lines (registrazione 12 nuove track)
backend/scripts/validate_v110_pack_85_*.py                                   | +11 file (nuove validator track)
backend/scripts/validate_mega_release_acceleration_85_*.py                   | +1 file (rollup)
data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json | +1 file (design summary completo)
docs/divine/110_PSP_ONBOARDING_NEW_SERVER_FRESH_START_FINAL_REPORT.md         | +1 file (questo report)
```

---

## 3. Baseline e Determinismo Master Suite — 3-Run

| Run | Pass  | Fail (OPTIONAL) | Miss | Required Fail |
|-----|-------|------------------|------|---------------|
| baseline_pre_pack | 1401 | 29 | 0 | 0 |
| final_post_pack_run1 | **1413** | 29 | 0 | **0** |
| final_post_pack_run2 | **1413** | 29 | 0 | **0** |
| final_post_pack_run3 | **1413** | 29 | 0 | **0** |
| delta | **+12** | 0 | 0 | **0** |

- **Determinismo:** `run1 == run2 == run3 == 1413 PASS`
- **Required fail:** `0` su tutti i run
- **Miss:** `0` su tutti i run
- **Optional fail:** invariato a `29` (baseline preservato — nessuna regressione)
- **12 nuove validator track Pack 85: tutte PASS in tutti i 3 run**

---

## 4. Canonical Fresh-Start SOT (Source of Truth)

> **Quando un utente entra in un nuovo server dove non ha mai giocato,
> per quell'utente significa iniziare il gioco da ZERO su quel server.**

### Schema fresh-start (default applicato dalla route ensure)

```
player_level      = 1
player_exp        = 0
team_formation    = []
story_progress    = {}
soft_currencies   = {}
onboarding_state  = "pending"
roster            = empty (nessun starter hero creato in Pack 85)
```

### Forbidden S1→S2 copy (ZERO eccezioni)

`roster`, `user_heroes`, `hero_levels`, `player_level`, `player_exp`,
`team`, `story_progress`, `inventory`, `equipment`, `mode_progression`.

### Account-wide remaining (NON è server-scoped)

- account identity
- auth/login
- entitlements globali
- hard/premium currency global
- impostazioni account
- diritti/acquisti globali

---

## 5. Route Map

| New Route                  | File                  | Function                  |
|----------------------------|-----------------------|---------------------------|
| `POST /api/psp/ensure`     | `backend/server.py`   | `psp_ensure_fresh_start`  |

**Downstream consumers preservati (read-only, nessuna modifica in Pack 85):**

- `GET /api/user/heroes` (Pack 81 server-scope + Pack 82 dual-read preservati)
- `GET /api/team/get-formation` (Pack 80 lobby fetch preservato)

---

## 6. PSP Ensure Route — Implementation Detail

| Property | Value |
|----------|-------|
| Method | `POST` |
| Path | `/api/psp/ensure?server_id=<sid>` |
| Auth | Required (JWT) |
| Idempotent | Yes (`already_exists_no_write` mode) |
| DB write only if PSP missing | Yes |
| No cross-server read | Yes |
| No starter heroes created | Yes |
| No starter premium grant | Yes |
| No `user_heroes` writes | Yes |

### Fresh-start fields written al primo ensure

```
user_id, server_id, profile_id, player_level=1, player_exp=0,
team_formation=[], story_progress={}, soft_currencies={},
onboarding_state="pending",
_slc_psp_user_id_namespace="uuid_canonical",
_slc_psp_created_by_pack="v110_pack_85_psp_onboarding_new_server_fresh_start",
_slc_psp_fresh_start=true,
_slc_psp_no_cross_server_copy=true,
created_at_utc
```

### Response headers

- `X-PSP-Ensure-Mode` ∈ {`fresh_start_created`, `already_exists_no_write`}
- `X-Server-Id`

---

## 7. `/api/user/heroes` After Ensure

| Phase | X-Blocker | X-Filter-Applied | X-PSP-Lookup-Mode | X-Player-Level | X-Player-Exp | Roster |
|-------|-----------|------------------|-------------------|----------------|--------------|--------|
| Pre-ensure (new server) | `PLAYER_SERVER_PROFILE_REQUIRED` | `false` | — | `1` | `0` | 0 |
| Post-ensure (new server) | (empty) | `true` | `direct_uuid` | `1` | `0` | 0 |

**Transition verified end-to-end** dal runtime smoke validator
(`validate_v110_pack_85_runtime_smoke_fresh_start.py`).

---

## 8. Lobby Integration

- Lobby già gestisce in modo onesto il blocker `PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER` (introdotto da Pack 79+ e preservato).
- Post-ensure su un nuovo server: lobby mostra **6 slot vuoti** + blocker team — nessuna leak di team S1.
- **Nessuna modifica al frontend in Pack 85**: la chiamata automatica `/api/psp/ensure` dal lobby è **DEFERRED** ad un pack successivo dedicato all'integrazione UI.

---

## 9. Runtime Smoke — Fresh-Start End-to-End

Eseguito con:

- `test_user_email`: `test@test.com`
- `test_server_id`: `s_pack85_val_<timestamp>` (ephemeral, cleaned-up post-test)

| Step | Result |
|------|--------|
| 1. Pre-ensure GET heroes su nuovo server | blocker `PLAYER_SERVER_PROFILE_REQUIRED` ✓ |
| 2. POST ensure → crea PSP fresh-start | `created=true`, `player_level=1`, `player_exp=0`, `no_cross_server_copy=true` ✓ |
| 3. Post-ensure GET heroes | `X-Filter-Applied=true`, `X-PSP-Lookup-Mode=direct_uuid`, level=1, exp=0, roster=0 ✓ |
| 4. Re-ensure (idempotenza) | `created=false`, `already_existed=true`, mode=`already_exists_no_write` ✓ |
| 5. S1 ancora intatto post-ensure | level≥1, filter_applied=true ✓ |
| 6. Cleanup PSP test ephemerale | ✓ |

**Verdict smoke:** `NEW_SERVER_FRESH_START_VERIFIED_END_TO_END_NO_S1_TO_S2_COPY`

---

## 10. Data Invariants & Zero Forbidden Mutation

| Mutation Class | Authorized in Pack 85 | Notes |
|----------------|----------------------|-------|
| `player_server_profiles` insert (1 record per first ensure call) | **YES (limited)** | Solo se PSP `(user_id, server_id)` non esiste |
| `user_heroes` writes | **NO (0)** | Zero |
| `users` writes | **NO (0)** | Zero |
| `inventory` writes | **NO (0)** | Zero |
| `equipment` writes | **NO (0)** | Zero |
| `battle_history` writes | **NO (0)** | Zero |
| Reward grant | **NO (false)** | Zero |
| Progress advance | **NO (false)** | Zero |
| Premium currency grant | **NO (false)** | Zero |
| Gacha/Shop/VIP/BattlePass mutations | **NO (false)** | Zero |
| Legacy cleanup | **NO (false)** | NOT executed in Pack 85 |
| Destructive migration | **NO (false)** | Zero |
| Physical normalization | **NO (false)** | (Pack 84 separato) |
| Bulk PSP apply | **NO (false)** | Zero |
| S1→S2 copy | **NO (false)** | Zero |
| Starter heroes created | **NO (false)** | Richiede starter flow approval pack separato |
| Player level mutation on existing PSP | **NO (false)** | Zero |

**Smoke test ephemeral:** 1 PSP creato + 1 PSP cancellato (cleanup). **Net DB delta = 0**.

---

## 11. Rollback / Cleanup Strategy

| Field | Value |
|-------|-------|
| Identifiable via | `_slc_psp_created_by_pack = "v110_pack_85_psp_onboarding_new_server_fresh_start"` |
| Cleanup query template | `{user_id, server_id, _slc_psp_created_by_pack: <tag>, _slc_psp_fresh_start: true}` |
| Future cleanup pack strategy | Pack futuro può rimuovere selettivamente PSP fresh-start con `onboarding_state=pending` E nessuna progression, OPPURE possono essere lasciati in produzione perché rappresentano stato di gioco valido |
| Safe to keep in production | **YES** |
| No data loss risk | **YES** |

**Refuse-by-default per delete:** nessuna delete di PSP reale autorizzata. Solo cleanup ephemerale di PSP di smoke test (marcato esplicitamente).

---

## 12. Live Readiness Update

| Surface | Live? |
|---------|-------|
| New server onboarding path (ensure route) | **TRUE** |
| Reward live | **FALSE** (invariato) |
| Progress live | **FALSE** (invariato) |
| Ledger live | **FALSE** (invariato) |
| Battle engine authoritative live | **FALSE** (invariato) |
| **Release readiness claimed** | **FALSE** |

---

## 13. Gate Invariant Preservation

| Pack / Gate | Preserved? |
|-------------|-----------|
| Pack 80 lobby fetch | **YES** |
| Pack 81 `/api/user/heroes` server-scope promotion | **YES** |
| Pack 82 PSP dual-read compat (`uuid` + `objectid_compat_fallback`) | **YES** |
| Pack 83 preflight artifacts | **YES** |
| Pack 84 physical PSP normalization | **YES** |
| v107D binding | **YES** |
| v108 POSTQA-A blockers | **YES** |
| POSTQA-D gates changed | **NO** (unchanged) |
| Battle engine formula rewrite | **NO** |
| `/api/battle/simulate` chiamato da staging/live | **NO** |

**Token invariants verificati in `backend/server.py`:**

```
user_heroes_are_server_scoped, objectid_compat_fallback, direct_uuid,
X-PSP-Lookup-Mode, X-Player-Level, X-Server-Progression-State,
PLAYER_SERVER_PROFILE_REQUIRED, SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING
```

---

## 14. Safety Flags (tutti `false`, eccetto `new_server_onboarding_path_live=true`)

```
fake_PASS                                           = false
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
user_heroes_creation_not_authorized_in_this_pack     = false
player_level_mutation_on_existing_psp                = false
copy_s1_to_s2                                        = false
account_wide_player_level_as_final_server_level      = false
account_wide_roster_as_final_server_roster           = false
postqa_d_gates_unlocked                              = false
battle_engine_formula_rewrite                        = false
battle_simulate_called_from_staging_or_live          = false
```

---

## 15. MD5 Rebase Chain — `backend/server.py`

| From MD5 | To MD5 | Reason |
|----------|--------|--------|
| `2e388592fcf8e0d87693b5656e908d22` (post Pack 82) | `2ec8fcd03aac47e50ae3eb495783ef16` (post Pack 85) | Aggiunta additiva route `POST /api/psp/ensure` (`psp_ensure_fresh_start`). Nessuna riscrittura. Storico Pack 80/81/82/83/84 preservato. `fake_PASS=false`, `validator_weakening=false`. |

**Historical reference chain preserved:**
Pack 80 → Pack 81 → Pack 82 → Pack 83 (no runtime change) → Pack 84 (DB-only) → **Pack 85**.

---

## 16. Explicit Statements (Required by Authorization String)

1. **New server starts level 1** — `player_level=1`, `player_exp=0`. ✓
2. **No S1→S2 copy** — `copy_s1_to_s2=false`, `no_cross_server_copy=true`. ✓
3. **Reward/progress live OFF** — `reward_live=false`, `progress_live=false`. ✓
4. **Legacy cleanup NOT executed** — `legacy_cleanup_executed=false`. ✓
5. **Local/public sync status** — `local_commit_only=true`, `public_push_managed_externally=true`, `no_remote_available=true`. ✓

---

## 17. Deferred Blockers (documented honestly)

- **Starter heroes auto-grant** — richiede pack starter-flow approval separato.
- **Frontend lobby auto-call `/api/psp/ensure`** — UI integration deferred al prossimo pack dedicato.
- **PSP-scoped loader promotion** per `inventory`, `currencies`, `story_progress`, `equipment` — ancora deferred.
- **Reward/progress live** — restano `OFF`.
- **Legacy cleanup** — NON eseguito (richiede pack legacy-cleanup approvato separatamente).

---

## 18. Next Step Recommendation (in attesa di approvazione utente)

> **NON procedere a Pack 86 senza upload esplicito del prossimo ZIP e relativa stringa di autorizzazione.**

Possibili direzioni candidate per il prossimo pack (a discrezione utente):

1. **Lobby UI integration** — frontend chiama automaticamente `/api/psp/ensure` su server switch.
2. **Starter flow** — definizione e approval esplicita dello schema starter heroes/team per fresh-start.
3. **Inventory/currencies/story PSP-scoped loader promotion** (prossimo step di server-scoping SOT).

In attesa della verifica utente / sync pubblica della piattaforma prima di marcare definitivamente Pack 85 come `APPROVED`.

---

**END OF REPORT — Pack 85 (`MEGA_RELEASE_ACCELERATION_85_PSP_ONBOARDING_NEW_SERVER_FRESH_START`)**
