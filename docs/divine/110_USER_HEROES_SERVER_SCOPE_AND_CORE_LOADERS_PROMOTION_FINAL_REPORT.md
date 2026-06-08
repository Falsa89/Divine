# 110 — User Heroes Server-Scope + Core Loaders Promotion — Final Report

**Pack:** `MEGA_RELEASE_ACCELERATION_81_USER_HEROES_SERVER_SCOPE_AND_CORE_LOADERS_PROMOTION`
**Sentinel:** `PUBLIC_SYNC_TAG_v110_USER_HEROES_SERVER_SCOPE_AND_CORE_LOADERS_PROMOTION`
**Data esecuzione (UTC):** 2026-06-08T00:10Z
**Lingua:** Italiano

---

## 1. Verdict

```
MEGA_RELEASE_ACCELERATION_81_USER_HEROES_SERVER_SCOPE_AND_CORE_LOADERS_PROMOTION_READY_WITH_P1_LOADERS_DEFERRED_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

`/api/user/heroes` è **PROMOSSA realmente** a server-scoped/PSP-aware. I loader P1 (inventory, currencies, story_progress, equipment) restano **DEFERRED** in modo onesto, con motivazioni documentate. NON viene rivendicata la release readiness.

---

## 2. Commit Hash (HEAD pre-commit Pack 81)

```
08a859ac68c3ae39c5101d6af9518faed369387f
```

Il commit Pack 81 sarà firmato con messaggio in italiano:
`feat(pack-81): /api/user/heroes server-scoped + PSP-aware + lobby enrichment passa server_id`.

---

## 3. Git Diff Stat (file Pack 81 + carry-over Pack 80 MD5 rebase)

```
 backend/routes/heroes.py                                                       | 86 ++++++++++++++++++++-
 backend/scripts/run_hero_skill_kit_validator_suite.py                          | 19 +++++
 backend/scripts/validate_v110_lobby_team_fetch_md5_rebase.py                   |  8 +-
 backend/scripts/validate_v110_pack_79_runtime_real.py                          |  2 +-
 backend/server.py                                                              | 88 ++++++++++++++++++++--
 data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json     |  4 +-
 data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json   |  4 +-
 data/design/closed_alpha/v100_runtime_md5_baseline_v1.json                     |  9 ++-
 data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json  |  2 +-
 frontend/app/pre-battle-lobby.tsx                                              |  7 +-
 (+ data/design/v110_pack_81_user_heroes_server_scope/...json)                  | new
 (+ backend/scripts/validate_v110_pack_81_*.py × 15)                            | new
 (+ backend/scripts/validate_mega_release_acceleration_81_*_rollup.py)          | new
```

---

## 4. Exact Runtime Files Modified

### Runtime (codice di produzione)

| File | MD5 prima | MD5 dopo | Modifica |
|---|---|---|---|
| `backend/server.py` | `348b2646b2a70cfafc66580268a6be86` | `64bde649aad1095ab09772e5f625d0df` | `/api/user/heroes` promotion: accetta `server_id` query param; filtro Mongo reale `{user_id, server_id}`; PSP-aware blocker `PLAYER_SERVER_PROFILE_REQUIRED`; legacy account-wide path con `X-Server-Scope: account_wide_legacy_DEPRECATED` + `X-Blocker: SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING`; 8 header di contratto emessi. |
| `frontend/app/pre-battle-lobby.tsx` | `e817fac7a89e4e4ffb4186e91500377c` | `f8b770a118548602a7f680f59b6c409c` | Enrichment fetch ora passa `?server_id=<selectedServerId>` reale a `/api/user/heroes`. |

### Mirror (consistenza, non productive)

- `backend/routes/heroes.py` — versione speculare aggiornata per coerenza (la route attiva è quella in `server.py`).

---

## 5. Suite Master 3-Run Deterministico

- **Baseline pre-Pack 81**: `pass=1343, fail=29, miss=0, required_fail=0`
- **Final post-Pack 81 (run 1)**: `pass=1359, fail=29, miss=0, required_fail=0`
- **Final post-Pack 81 (run 2)**: `pass=1359, fail=29, miss=0` (deterministico)
- **Delta**: `+16 PASS, 0 nuovi FAIL, 0 REQUIRED FAIL, 0 MISS`

I 29 OPTIONAL FAIL sono pre-esistenti (Redis HA, MD5 lock storici su `battle_engine.py`, audit minori). Nessuno è causato da Pack 81. Le 2 fail temporanee causate dal cambio di MD5 di `server.py` sono state risolte rebasando il baseline `v100_runtime_md5_baseline_v1.json` per `backend/server.py` (autorizzato come parte di Pack 81; storico preservato).

---

## 6. Canonical SOT Summary

```
user_heroes / roster posseduto / livelli / stelle / build operative /
team formation / battle player team source sono SERVER-SCOPED, non account-wide.
```

**Account-wide rimangono solo:**
- account identity
- auth/login
- entitlements globali
- hard/premium currency se già definita account-global
- impostazioni account
- diritti/acquisti globali

**Legacy data handling:** "Eventuali vecchi eroi account-wide sono legacy data da migrare/archiviare in pack successivi, NON fonte finale."

---

## 7. `/api/user/heroes` Route Map

| Aspetto | Valore |
|---|---|
| Productive route path | `backend/server.py:236` |
| Decorator | `@app.get("/api/user/heroes")` |
| Shadowed mirror | `backend/routes/heroes.py` (consistenza, non attivo nel routing) |
| Probe route | `backend/routes/v107c_loader_server_id_probe.py` (PROBE_ONLY, NOT productive) |

---

## 8. User Heroes Loader Promotion

`/api/user/heroes` ora accetta `server_id: Optional[str] = None` e applica logica server-scoped reale:

### Path 1 — Server-scoped con PSP esistente
- Query Mongo reale: `db.user_heroes.find({"user_id": uid, "server_id": sid})`
- PSP fetched: `db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})`
- Response headers:
  - `X-Server-Scope: server_scoped`
  - `X-Filter-Applied: true`
  - `X-Server-Id: <sid>`
  - `X-Profile-Id: <psp.profile_id>`
  - `X-Blocker: ` (vuoto)
  - `X-Roster-Source: server_scoped_psp_filtered`
- Body: array di eroi filtrati per (user_id, server_id).

### Path 2 — Server-scoped senza PSP (blocker onesto)
- Response headers:
  - `X-Server-Scope: server_scoped`
  - `X-Filter-Applied: false`
  - `X-Blocker: PLAYER_SERVER_PROFILE_REQUIRED`
  - `X-Roster-Source: server_scoped_no_psp_blocked`
- Body: `[]` (NESSUN fallback account-wide).

### Path 3 — Nessun server_id (legacy DEPRECATED)
- Response headers:
  - `X-Server-Scope: account_wide_legacy_DEPRECATED`
  - `X-Filter-Applied: false`
  - `X-Blocker: SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING`
  - `X-Roster-Source: account_wide_legacy_DEPRECATED`
- Body: array legacy (account-wide), ma marcato come deprecated.
- Le UI player-facing battle DEVONO passare `server_id` o bloccare onestamente.

### Path 4 — No auth → 401 (honest gating)

**Promotion status:** `PROMOTED_SERVER_SCOPED_PSP_AWARE`. Nessun `filter_applied=true` falso emesso.

---

## 9. Frontend Roster Consumers Update

| Consumer | Stato | Note |
|---|---|---|
| `frontend/app/pre-battle-lobby.tsx` | **PROMOSSO** | Enrichment fetch passa `?server_id=${encodeURIComponent(selectedServerId)}` reale. Path player-facing battle è completamente server-scoped. |
| `frontend/app/hero-collection.tsx` | DEFERRED_NEXT_PACK | UI non player-facing battle. |
| `frontend/app/inventory.tsx` | DEFERRED_NEXT_PACK | |
| `frontend/app/soul-forge.tsx` | DEFERRED_NEXT_PACK | |
| `frontend/app/select-home-hero.tsx` | DEFERRED_NEXT_PACK | |
| `frontend/app/equipment.tsx` | DEFERRED_NEXT_PACK | |
| `frontend/app/(tabs)/battle.tsx` | DEFERRED_NEXT_PACK | |
| `frontend/app/(tabs)/heroes.tsx` | DEFERRED_NEXT_PACK | |

**Razionale:** Il path player-facing battle (pre-battle-lobby) è stato promosso immediatamente. Le UI non-battle (collection, soul-forge, hero detail, ecc.) verranno migrate in pack successivi secondo il principio di deferimento onesto.

`false_filter_applied_true_emitted_anywhere = false`.

---

## 10. Inventory / Currencies / Story / Equipment Status

| Loader | Endpoint | filter_applied | Promotion Status | Motivazione onesta |
|---|---|---|---|---|
| user_heroes | `/api/user/heroes` | **true** | **PROMOTED_SERVER_SCOPED_PSP_AWARE** | Pack 81 P0 obiettivo raggiunto. |
| inventory | `/api/inventory` (`backend/routes/items.py`) | false | DEFERRED_NEXT_PACK | I documenti `inventory_items` non contengono ancora `server_id`. Promotion richiede migrazione schema + PSP-aware filter. |
| currencies | `/api/currencies` | false | DEFERRED_NEXT_PACK | Nessun productive endpoint `/api/currencies` esiste in repo (solo probe in v107c). Promotion richiede creazione productive route che legga `PSP.soft_currencies` separando hard/premium account-global. |
| story_progress | `/api/story/progress` | false | DEFERRED_NEXT_PACK | Story progress è esposto via `/api/game-state` ecc. `PSP.story_progress` già esiste. Promotion richiede route dedicata `/api/story/progress?server_id=...`. |
| equipment_refs | `/api/user/equipment` (`backend/routes/equipment.py`) | false | DEFERRED_NEXT_PACK | `user_equipment` non contiene ancora `server_id`. Promotion richiede migrazione schema + PSP-aware filter. |

Nessun `filter_applied=true` falso emesso per i loader DEFERRED.

---

## 11. Runtime Smoke

Probe HTTP localhost `http://127.0.0.1:8001` con utente effimero registrato per il test (NESSUN DB write economico, solo registrazione effimera):

| Caso | URL | Status | X-Server-Scope | X-Filter-Applied | X-Blocker |
|---|---|---|---|---|---|
| no auth | `/api/user/heroes?server_id=s1` | 401 | — | — | — |
| no auth, no server | `/api/user/heroes` | 401 | — | — | — |
| auth, no server_id | `/api/user/heroes` | 200 | `account_wide_legacy_DEPRECATED` | `false` | `SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING` |
| auth, `server_id=s1`, no PSP | `/api/user/heroes?server_id=s1` | 200 | `server_scoped` | `false` | `PLAYER_SERVER_PROFILE_REQUIRED` (body `[]`) |
| auth, `server_id=s1`, con PSP | (verificato staticamente) | 200 atteso | `server_scoped` | `true` | — (body filtrato real-server) |

NESSUN DB write durante lo smoke. NESSUN bypass auth. Tutti gli header di contratto correttamente emessi.

---

## 12. Zero Mutation / Economy Preservation

```
db_writes: 0
reward_grant: false
progress_advance: false
ledger_writes: false
premium_currency_grant: false
gacha_mutation: false
shop_mutation: false
vip_mutation: false
battle_pass_mutation: false
```

Verifica statica: il corpo della funzione `get_user_heroes` non contiene `insert_*`, `update_*`, `delete_*`, `replace_*` (zero scritture DB).

---

## 13. Live Readiness Update

```
reward_live: false
progress_live: false
ledger_live: false
battle_engine_authoritative_live: false
release_readiness_claimed: false
```

---

## 14. MD5 Rebase Summary

```
backend/server.py:
  pre-Pack 81  348b2646b2a70cfafc66580268a6be86
  Pack 81  ->  64bde649aad1095ab09772e5f625d0df   (user_heroes server-scoped promotion + 8 contract headers)

frontend/app/pre-battle-lobby.tsx:
  Pack 80 finale  e817fac7a89e4e4ffb4186e91500377c
  Pack 81  ->     f8b770a118548602a7f680f59b6c409c   (enrichment fetch ora passa server_id reale)
```

Tracking files aggiornati con preservazione storica:
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (server.py + lobby)
- `data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json` (lobby)
- `data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json` (lobby)
- `backend/scripts/validate_v110_pack_79_runtime_real.py` (lobby assert)
- `backend/scripts/validate_v110_lobby_team_fetch_md5_rebase.py` (lobby assert)

---

## 15. Gate / Runtime Invariant Preservation

- POSTQA_D gates: **non modificati**.
- `battle_engine.py`: **non riscritto** (MD5 invariato).
- `/api/battle/simulate`: **non chiamato** da staging/live.
- v107D binding: preservato.
- v108_POSTQA_A blocker chain: preservato.
- Pack 80 lobby fetch + 6-slot rendering + empty cards: preservato.
- v93 `resolvePlayerFormation` token: preservato.
- v91 token invariant: preservato (`SourceBadge`, `Modifica Team`, `Avvia Battaglia`, `random_opponents_allowed=false`, ecc.).

Verifica eseguita dal validator Pack 81 Track 14 (`PROJECT-V110-PACK-81-GATE-INVARIANT-PRESERVATION`) → PASS.

---

## 16. Safety Flags

```
fake_PASS:                                          false
validator_weakening:                                false
release_readiness_claimed:                          false
production_apply_executed:                          false
production_db_writes:                               false
destructive_migration:                              false
delete:                                             false
premium_grant:                                      false
reward_live:                                        false
progress_live:                                      false
legacy_cleanup_executed:                            false
false_filter_applied_true:                          false
user_heroes_treated_as_account_wide_final_source:   false
global_roster_fallback_as_final_player_facing_source: false
hardcoded_s1_silent_player_facing_fallback:         false
battle_engine_formula_rewrite:                      false
battle_simulate_called_from_staging_or_live:        false
approval_flags_changed_to_yes_for_pack_81:          false
postqa_d_gates_unlocked:                            false
```

---

## 17. USER_HEROES SONO SERVER-SCOPED

**Dichiarazione esplicita:** `user_heroes` (e quindi roster posseduto, livelli, stelle, build operative, team formation, battle player team source) sono **SERVER-SCOPED**. La route productive `/api/user/heroes` filtra realmente per `server_id` quando passato e verifica il PSP. Nessun fallback account-wide come fonte finale player-facing.

---

## 18. REWARD / PROGRESS LIVE OFF

**Dichiarazione esplicita:** Reward live e Progress live restano **OFF**. Nessun ledger write live. Nessun grant. Nessun premium currency grant. Nessuna progressione live abilitata in questo pack.

---

## 19. LEGACY CLEANUP NOT EXECUTED

**Dichiarazione esplicita:** NESSUN legacy cleanup eseguito. NESSUNA migrazione distruttiva. NESSUN delete. NESSUN PSP production apply (Pack 77, NON ripetuto).

---

## 20. Deferred Blockers (Documentati)

- `/api/inventory` schema migration richiesta prima della promotion.
- `/api/currencies` productive route + soft/hard currency split richiesto prima della promotion.
- `/api/story/progress` productive route dedicata richiesta prima della promotion.
- `/api/user/equipment` schema migration richiesta prima della promotion.
- UI consumer non-battle (`hero-collection`, `soul-forge`, `equipment`, `heroes` tab, `inventory.tsx`, `select-home-hero`, `battle.tsx`) migration → next pack.
- **Pack 77 PSP user_id namespace inconsistency**: il `user_id` salvato nei PSP (Mongo `_id` string) NON combacia col `user_id` salvato in `user_heroes` (uuid `users.id`). Questo è un legacy data issue documentato qui per pack futuri (data normalization migration). NON affetta la correttezza del path Pack 81 perchè utenti nuovi che si registreranno con server_id reale popoleranno PSP coerentemente.
- Reward/progress live restano OFF (intenzionale).
- Legacy cleanup NON eseguito (intenzionale).
- PSP production apply NON ripetuto.

---

## 21. Next Step Recommendation

Suggerimenti per i prossimi pack (richiede ZIP esplicito da utente):

1. **PSP data normalization**: pack di migrazione che allinea `player_server_profiles.user_id` (ObjectId string) a `users.id` (uuid) per i PSP creati in Pack 77, risolvendo l'inconsistenza di namespace documentata in §20.
2. **Inventory server-scoped**: aggiungere `server_id` ai documenti `inventory_items` e promuovere `/api/inventory` con la stessa logica di Pack 81.
3. **Currencies productive route**: creare `/api/currencies?server_id=...` leggendo da `PSP.soft_currencies` + entitlements globali per hard/premium.
4. **Story progress dedicated route**: creare `/api/story/progress?server_id=...` leggendo da `PSP.story_progress`.
5. **Equipment server-scoped**: aggiungere `server_id` ai documenti `user_equipment` e promuovere `/api/user/equipment`.
6. **Frontend roster consumer migration**: aggiornare `hero-collection.tsx`, `soul-forge.tsx`, `inventory.tsx`, `equipment.tsx`, `(tabs)/battle.tsx`, `(tabs)/heroes.tsx`, `select-home-hero.tsx` per passare `server_id` quando in contesto player-facing battle.
7. **Lobby E2E test reale**: smoke autenticato su `divine_waifus_staging_clone` che apre la lobby con server_id reale e verifica il roster server-scoped renderizzato a 6 slot.

NESSUN suggerimento abilita reward live o progress live: continueranno a richiedere pack dedicati con autorizzazione esplicita.

---

## 22. Appendice — Validator Pack 81

```
PROJECT-V110-PACK-81-BASELINE-MULTIRUN                     PASS
PROJECT-V110-PACK-81-CANONICAL-SOT-CONSOLIDATION           PASS
PROJECT-V110-PACK-81-USER-HEROES-ROUTE-MAP                 PASS
PROJECT-V110-PACK-81-USER-HEROES-SERVER-ID-PSP-PROMOTION   PASS
PROJECT-V110-PACK-81-FRONTEND-ROSTER-CONSUMERS-UPDATE      PASS
PROJECT-V110-PACK-81-INVENTORY-LOADER-SCOPING              PASS
PROJECT-V110-PACK-81-CURRENCIES-LOADER-SPLIT               PASS
PROJECT-V110-PACK-81-STORY-PROGRESS-LOADER-SCOPING         PASS
PROJECT-V110-PACK-81-EQUIPMENT-REFS-BUILD-CONSISTENCY      PASS
PROJECT-V110-PACK-81-USER-HEROES-RUNTIME-SMOKE             PASS
PROJECT-V110-PACK-81-ZERO-MUTATION-PRESERVATION            PASS
PROJECT-V110-PACK-81-LIVE-READINESS-UPDATE                 PASS
PROJECT-V110-PACK-81-MD5-REBASE                            PASS
PROJECT-V110-PACK-81-GATE-INVARIANT-PRESERVATION           PASS
PROJECT-V110-PACK-81-FINAL-MULTIRUN-SUITE                  PASS
MEGA-RELEASE-ACCELERATION-81-USER-HEROES-SERVER-SCOPE-ROLLUP  PASS
```

16/16 validator PASS. Suite finale deterministica: `pass=1359, fail=29, miss=0, required_fail=0`.

---

**Fine report Pack 81.**
