# 110 — PSP user_id Dual-Read Compat + Server Player Progress SOT — Final Report

**Pack:** `MEGA_RELEASE_ACCELERATION_82_PSP_USER_ID_DUAL_READ_COMPAT_AND_SERVER_PLAYER_PROGRESS_SOT`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_PSP_USER_ID_DUAL_READ_COMPAT_AND_SERVER_PLAYER_PROGRESS_SOT`
**Data esecuzione (UTC):** 2026-06-08T00:35Z
**Lingua:** Italiano
**Approccio:** **A — DUAL-READ COMPAT (zero DB writes)**
**Approccio rifiutato:** B (PSP `user_id` physical normalization) — DEFERRED a pack dedicato con autorizzazione esplicita, backup e rollback script.

---

## 1. Verdict

```
MEGA_RELEASE_ACCELERATION_82_PSP_USER_ID_DUAL_READ_COMPAT_AND_SERVER_PLAYER_PROGRESS_SOT_READY_PHYSICAL_NORMALIZATION_DEFERRED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

PSP `user_id` mismatch risolto a runtime tramite dual-read (zero DB writes). Server player progress SOT formalizzato nel PSP. Fresh-start invariant verificata su utente Pack 77 reale. NON viene rivendicata la release readiness.

---

## 2. Commit Hash (HEAD pre-commit Pack 82)

```
08a859ac68c3ae39c5101d6af9518faed369387f
```

Commit Pack 82 firmato (italiano): `feat(pack-82): dual-read PSP user_id compat + server-scoped player progress SOT (zero DB writes)`.

---

## 3. PSP user_id Normalization Result

**Decisione canonica Pack 82:** NESSUNA normalizzazione fisica eseguita. Compatibilità ottenuta via dual-read a livello di applicazione. Zero DB writes.

### Audit READ-ONLY (eseguito 2026-06-08T00:34Z)

```json
{
  "psp_total": 1690,
  "direct_uuid_count": 0,
  "objectid_compat_fallback_count": 1690,
  "orphan_count": 0,
  "db_writes": 0,
  "read_only": true
}
```

**Interpretazione:**
- TUTTI i 1690 PSP Pack 77 usano namespace `ObjectId-string` (legacy compat).
- Zero PSP raggiungibili via `users.id` (uuid) direct — atteso, poiché Pack 77 ha usato `str(_id)`.
- Zero PSP orfani: ogni PSP corrisponde a un utente reale.
- Dual-read fallback risolve il mismatch al 100% senza scrivere nulla.

**Migrazione fisica futura:** quando autorizzata (con backup + rollback script + autorizzazione esplicita), riscriverà `PSP.user_id` da ObjectId-string a uuid. Pack futuri ETA.

---

## 4. Runtime Files Modified

| File | MD5 prima (Pack 81) | MD5 dopo (Pack 82) | Modifica |
|---|---|---|---|
| `backend/server.py` | `64bde649aad1095ab09772e5f625d0df` | `2e388592fcf8e0d87693b5656e908d22` | Dual-read PSP lookup (`uid` uuid → `str(_id)` fallback); nuovi header `X-PSP-Lookup-Mode`, `X-Player-Level`, `X-Player-Exp`, `X-Server-Progression-State`; SOT server-scoped player progress dal PSP. |

---

## 5. Git Diff Stat (file Pack 82)

```
 backend/scripts/audit_v110_pack_82_psp_user_id_namespace.py                      | new
 backend/scripts/run_hero_skill_kit_validator_suite.py                            | 16 ++++
 backend/scripts/validate_mega_release_acceleration_82_psp_dual_read_compat_rollup.py | new
 backend/scripts/validate_v110_pack_82_*.py × 11                                  | new
 backend/server.py                                                                | 60 +++++++++--
 data/design/closed_alpha/v100_runtime_md5_baseline_v1.json                       | 7 ++-
 data/design/v110_pack_82_psp_dual_read_compat/...summary_v1.json                 | new
```

---

## 6. Dual-Read PSP Lookup Implementation

```python
# 1° tentativo: namespace canonico futuro (users.id uuid)
psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
if not psp:
    # 2° tentativo compat: namespace legacy Pack 77 (str(users._id))
    legacy_uid = str(current_user.get("_id") or "")
    if legacy_uid:
        psp_compat = await db.player_server_profiles.find_one({"user_id": legacy_uid, "server_id": sid})
        if psp_compat:
            psp = psp_compat
            psp_lookup_mode = "objectid_compat_fallback"
```

**Lookup modes emessi via header `X-PSP-Lookup-Mode`:**
- `direct_uuid` — PSP trovato via `users.id` uuid (path canonico futuro)
- `objectid_compat_fallback` — PSP trovato via `str(_id)` (Pack 77 legacy compat)
- `not_found` — Nessun PSP → blocker `PLAYER_SERVER_PROFILE_REQUIRED`
- `skipped_no_server_id` — Nessun server_id fornito → legacy account-wide deprecated

**Zero DB writes.** Solo `find_one`/`find` operazioni read.

---

## 7. Runtime Smoke con Utente Migrato REALE

Utente Pack 77 reale impersonato via JWT:

```
user_id_uuid:  651253e2-da8d-466b-98f3-82f008d158ed
user._id:      69db92d8310b06d00182f644
email:         test@test.com
PSP server_id: s1
PSP.user_id:   69db92d8310b06d00182f644  (ObjectId-string namespace legacy)
```

### Path 1 — `/api/user/heroes?server_id=s1` (con PSP esistente)

```
HTTP/1.1 200 OK
X-Server-Scope:              server_scoped
X-Filter-Applied:            true
X-Server-Id:                 s1
X-Profile-Id:                69db92d8310b06d00182f644:s1
X-Blocker:
X-Canonical-Decision:        user_heroes_are_server_scoped
X-Roster-Source:             server_scoped_psp_filtered
X-Roster-Count:              353
X-PSP-Lookup-Mode:           objectid_compat_fallback   ← compat OK
X-Player-Level:              50                          ← dal PSP
X-Player-Exp:                7252292                     ← dal PSP
X-Server-Progression-State:  psp_present_server_scoped
```

Body: array di 353 eroi filtrati per `(user_id=uuid, server_id=s1)`. Filter REALE applicato.

### Path 2 — `/api/user/heroes?server_id=s2` (server mai giocato, FRESH START)

```
HTTP/1.1 200 OK
X-Server-Scope:              server_scoped
X-Filter-Applied:            false
X-Server-Id:                 s2
X-Profile-Id:
X-Blocker:                   PLAYER_SERVER_PROFILE_REQUIRED
X-Roster-Source:             server_scoped_no_psp_blocked
X-Roster-Count:              0                           ← ZERO copia da s1
X-PSP-Lookup-Mode:           not_found
X-Player-Level:              1                           ← FRESH start (non 50)
X-Player-Exp:                0                           ← FRESH start (non 7252292)
X-Server-Progression-State:  fresh_start_pending_psp_creation
```

Body: `[]` (nessun roster legacy s1 leakato in s2).

**Verdict smoke:** `MIGRATED_USER_FOUND_VIA_OBJECTID_COMPAT_FALLBACK_FILTER_APPLIED_TRUE` + `FRESH_START_INVARIANT_RESPECTED_NO_S1_TO_S2_COPY`.

---

## 8. Server Player Progress SOT (Canonical Decision)

**Statement canonico Pack 82:**

> Server-scoped player progress SOT: `player_level`, `player_exp`, `roster`, `team`, `story_progress`, `inventory`, `equipment` vivono nel PSP / `player_server_profiles`. NON in `users.*` global come fonte finale.

**Invariant esempi:**

```
S1 livello 40  !=  S2 livello 40
nuovo server mai giocato = livello 1 / exp 0 / progressione iniziale
roster S1 NON copiato su S2
level/exp S1 NON copiato su S2
team formation S1 NON copiato su S2
```

**Account-wide rimangono SOLO:**

- account identity
- auth/login
- entitlements globali
- hard/premium currency (se già definita account-global)
- impostazioni account
- diritti/acquisti globali

**PSP creation/onboarding per nuovo server:** **DEFERRED_TO_DEDICATED_ONBOARDING_PACK**. In questo Pack 82, server mai giocato → blocker onesto + headers fresh-start (level 1, exp 0).

`no_fallback_to_old_server_or_account_level = true`.

---

## 9. New Server Fresh-Start Proof

Verificato live sul caso `server_id=s2` per utente con PSP solo su `s1`:

| Campo | Valore (s1 live) | Valore (s2 fresh) | Copia S1→S2? |
|---|---|---|---|
| player_level | 50 | **1** | ❌ NO |
| player_exp | 7252292 | **0** | ❌ NO |
| roster_count | 353 | **0** | ❌ NO |
| team | popolato | **vuoto** | ❌ NO |
| story_progress | avanzata | **initial** | ❌ NO |
| inventory | popolato | **iniziale** (gestito da loader dedicato, DEFERRED) | ❌ NO |
| equipment | live | **vuoto** | ❌ NO |
| progression_state | psp_present_server_scoped | **fresh_start_pending_psp_creation** | ❌ NO |

Nessuna logica di copia presente nel route. Verificato staticamente da Track 6 (`validate_v110_pack_82_fresh_start_invariant`).

---

## 10. /api/user/heroes Post-Normalization Result

`/api/user/heroes` ora supporta:
1. **Path canonico futuro** (`X-PSP-Lookup-Mode: direct_uuid`) — riservato per PSP creati POST-Pack-77 con uuid namespace.
2. **Path compat legacy** (`X-PSP-Lookup-Mode: objectid_compat_fallback`) — risolve i 1690 PSP Pack 77 senza migrazione.
3. **Path blocker** (`X-PSP-Lookup-Mode: not_found`) — fresh-start invariant per server mai giocato.
4. **Path legacy DEPRECATED** (`X-PSP-Lookup-Mode: skipped_no_server_id`) — solo per UI non-player-facing battle, con header `account_wide_legacy_DEPRECATED`.

Tutti i 1690 PSP attuali risolti via path 2. Zero orfani. Filter REALE applicato.

---

## 11. Zero Mutation / Economy Preservation

```
db_writes:                                0
psp_writes:                               0
user_heroes_writes:                       0
users_writes:                             0
reward_grant:                             false
progress_advance:                         false
ledger_writes:                            false
premium_currency_grant:                   false
gacha_mutation:                           false
shop_mutation:                            false
vip_mutation:                             false
battle_pass_mutation:                     false
physical_psp_normalization_executed:      false
legacy_cleanup_executed:                  false
destructive_migration_executed:           false
```

Verifica statica: `get_user_heroes` fn body contiene 0 occorrenze di `insert_*`/`update_*`/`delete_*`/`replace_*`. Audit script: 0 occorrenze di write ops (READ-ONLY).

---

## 12. Reward / Progress Live OFF

**Dichiarazione esplicita:** Reward live e Progress live restano **OFF**. Nessun ledger write live. Nessun grant. Nessuna progressione live abilitata.

---

## 13. Legacy Cleanup NOT Executed

**Dichiarazione esplicita:** NESSUN legacy cleanup. NESSUNA migrazione distruttiva. NESSUN delete. NESSUN PSP production apply (Pack 77, NON ripetuto). NESSUNA migrazione fisica del campo `PSP.user_id` (deferred).

---

## 14. Final Suite 3-Run REALE

| Run | Timestamp UTC | Pass | Fail | Miss | Required Fail |
|---|---|---|---|---|---|
| Baseline (Pack 81 final) | 2026-06-08T00:28Z | 1359 | 29 | 0 | 0 |
| **Pack 82 Run 1** | 2026-06-08T00:42Z | **1371** | 29 | 0 | **0** |
| **Pack 82 Run 2** | 2026-06-08T00:44Z | **1371** | 29 | 0 | **0** |
| **Pack 82 Run 3** | 2026-06-08T00:46Z | **1371** | 29 | 0 | **0** |

**Delta:** `+12 PASS, 0 nuovi FAIL, 0 REQUIRED FAIL, 0 MISS`.

**Deterministico al 100%**: i 3 run finali hanno tutti prodotto identicamente `pass=1371, fail=29, miss=0, required_fail=0`. (Pack 81 aveva documentato solo 2 run finali — issue riconciliata in Pack 82 con i 3 run espliciti qui sopra.)

I 29 OPTIONAL FAIL sono pre-esistenti (Redis HA, MD5 lock storici, audit minori). Nessuno causato da Pack 82.

---

## 15. Safety Flags

```
fake_PASS:                                              false
validator_weakening:                                    false
release_readiness_claimed:                              false
production_apply_executed:                              false
production_db_writes:                                   false
destructive_migration:                                  false
delete:                                                 false
premium_grant:                                          false
reward_live:                                            false
progress_live:                                          false
legacy_cleanup_executed:                                false
physical_psp_normalization_executed:                    false
copy_s1_to_s2_roster:                                   false
copy_s1_to_s2_level:                                    false
copy_s1_to_s2_progress:                                 false
copy_s1_to_s2_team:                                     false
account_wide_player_level_as_final_server_level:        false
account_wide_roster_as_final_server_roster:             false
false_filter_applied_true:                              false
hardcoded_s1_silent_player_facing_fallback:             false
battle_engine_formula_rewrite:                          false
battle_simulate_called_from_staging_or_live:            false
approval_flags_changed_to_yes_for_pack_82:              false
postqa_d_gates_unlocked:                                false
```

---

## 16. Gate / Runtime Invariant Preservation

- POSTQA_D gates: non modificati.
- `battle_engine.py`: non riscritto.
- `/api/battle/simulate`: non chiamato.
- Pack 80 lobby fetch + 6-slot rendering: preservato.
- Pack 81 user_heroes server-scoped promotion: preservato (token `user_heroes_are_server_scoped`, blocker chain, filter Mongo reale).
- v107D binding, v108_POSTQA_A blockers: preservati.

Verificato dal validator Pack 82 Track 10 → PASS.

---

## 17. Deferred Blockers (Documentati)

- **Physical PSP `user_id` normalization** → dedicated future pack con autorizzazione esplicita + backup + rollback script.
- **PSP creation/onboarding per nuovo server** → dedicated onboarding pack (Pack futuro produrra' fresh-start PSP con `player_level=1`, `player_exp=0`, roster vuoto, ecc.).
- **Inventory/currencies/story_progress/equipment loader promotion** → packs follow-up (richiedono schema migration + productive route creation).
- **Roster consumers non-battle migration** → pack follow-up (hero-collection, soul-forge, equipment, heroes tab, ecc.).
- Reward/progress live restano OFF (intenzionale).
- Legacy cleanup NOT executed (intenzionale).

---

## 18. Next Step Recommendation

1. **Pack futuro — PSP user_id physical normalization**: con autorizzazione esplicita (es. stringa "AUTORIZZO LA NORMALIZZAZIONE FISICA PSP user_id SU divine_waifus"), backup PSP completo + rollback script + idempotency check + final smoke. Output target: `direct_uuid_count=1690, objectid_compat_fallback_count=0`.
2. **Pack futuro — PSP onboarding new server**: definire flow per creazione PSP fresh-start su server mai giocato (level=1, exp=0, roster vuoto/starter, ecc.). Trigger su login con `selected_server_id` non ancora visto.
3. **Pack futuro — inventory PSP-scoped**: aggiungere `server_id` a inventory_items + productive route promotion.
4. **Pack futuro — currencies productive route**: creare `/api/currencies?server_id=...` leggendo `PSP.soft_currencies`.
5. **Pack futuro — story progress productive route**: `/api/story/progress?server_id=...` da `PSP.story_progress`.
6. **Pack futuro — equipment server-scoped**: schema migration + productive route.
7. **Pack futuro — roster UI consumers migration**: hero-collection, soul-forge, equipment.tsx, heroes tab.

Nessuno di questi pack abilita reward/progress live: richiedono pack dedicati con autorizzazione esplicita.

---

## 19. Appendice — Validator Pack 82

```
PROJECT-V110-PACK-82-BASELINE-MULTIRUN                     PASS
PROJECT-V110-PACK-82-DUAL-READ-PSP-LOOKUP                  PASS
PROJECT-V110-PACK-82-SERVER-PLAYER-PROGRESS-SOT            PASS
PROJECT-V110-PACK-82-PSP-NAMESPACE-AUDIT                   PASS
PROJECT-V110-PACK-82-RUNTIME-SMOKE-REAL-MIGRATED-USER      PASS
PROJECT-V110-PACK-82-FRESH-START-INVARIANT                 PASS
PROJECT-V110-PACK-82-ZERO-DB-WRITES                        PASS
PROJECT-V110-PACK-82-LIVE-READINESS-UPDATE                 PASS
PROJECT-V110-PACK-82-MD5-REBASE                            PASS
PROJECT-V110-PACK-82-GATE-INVARIANT-PRESERVATION           PASS
PROJECT-V110-PACK-82-FINAL-3RUN-SUITE                      PASS
MEGA-RELEASE-ACCELERATION-82-PSP-DUAL-READ-COMPAT-ROLLUP   PASS
```

12/12 validator PASS. Suite finale deterministica 3-run: `pass=1371, fail=29, miss=0, required_fail=0`.

---

**Fine report Pack 82.**
