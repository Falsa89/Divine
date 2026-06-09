# Pack 90 — MEGA_RELEASE_ACCELERATION_90_INVENTORY_WRITE_PATHS_STRICT_SERVER_SCOPE — Final Report

> **Lingua**: italiano (per direttiva utente).
> **Pacchetto**: `MEGA_RELEASE_ACCELERATION_90_INVENTORY_WRITE_PATHS_STRICT_SERVER_SCOPE`
> **Sentinella**: `PUBLIC_SYNC_TAG_v110_INVENTORY_WRITE_PATHS_STRICT_SERVER_SCOPE`
> **Track**: M (inventory write paths)
> **Generato**: 2026-06-09 (UTC)

---

## 1. Verdict

```
verdict = MEGA_RELEASE_ACCELERATION_90_INVENTORY_WRITE_PATHS_STRICT_SERVER_SCOPE_RUNTIME_READY_WITH_DEFERRED_FRONTEND_CONSUMER_MIGRATION_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
verdict_class = RUNTIME_READY
required_fails = 0
miss = 0
optional_fails = 29   # invariato vs baseline Pack 89
deterministic = true  # 3 esecuzioni consecutive identiche
zero_regression_vs_pack_89 = true
```

---

## 2. Commit hash & Git diff --stat

> Il commit verrà eseguito al termine di questo report; il valore esatto del SHA
> sarà aggiunto come post-script `commit_hash` dopo l'esecuzione di
> `git add … && git commit -m …` (come da prassi Pack 86–89).

### git diff --stat (file runtime + design rilevanti)

```
backend/routes/items.py                                            | 100 +++++++++++++--------
data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_md5_rebase_v1.json |  12 ++-
docs/divine/110_INVENTORY_WRITE_PATHS_STRICT_SERVER_SCOPE_FINAL_REPORT.md     | (new file)
data/design/v110_pack_90_inventory_write_paths_strict_server_scope/...        | (new design dir)
```

Il resto del `git diff --stat` (≈177 file `*_result.json` + `*.pyc`) è
puramente derivato (touch dei result-file da parte dei validator
deterministici e pyc rigenerati durante le 3 run della suite). **Nessuna
modifica di codice di produzione al di fuori di `backend/routes/items.py`**.

---

## 3. Baseline & Final suite — 3-run multirun

| Run | pass | fail | miss | deterministic | command |
|-----|------|------|------|---------------|---------|
| 1   | 1474 | 29   | 0    | true          | `python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py` |
| 2   | 1474 | 29   | 0    | true          | idem |
| 3   | 1474 | 29   | 0    | true          | idem |

**Risultato**: `REQUIRED_FAIL=0`, `MISS=0`, `OPTIONAL_FAIL=29`, `deterministic=true`.

Le 29 fail residue sono **tutte note e classificate OPTIONAL** (ereditate dal
baseline Pack 85→89, vincolate da Redis di ambiente o da pacchetti
storici già documentati come deferiti). Elenco completo:

```
PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN
PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE
PROJECT-V96-MD5-BASELINE-LOCK
MEGA-RELEASE-ACCELERATION-45-v96-ROLLUP
PROJECT-V108-POSTQA-B-REDIS-ENVIRONMENTAL-STABILIZATION
MEGA-RELEASE-ACCELERATION-63-v108-POSTQA-B-ROLLUP
V23-PREFLIGHT
AF2-N-V23-REDIS-SWITCH
ULTRA-COMBO-V23
V24-PREFLIGHT
ULTRA-COMBO-V24
LIVE-MODES-SLC-NEXT-COMBO-A
BENCHMARK-CANONICAL-COMBO-A
SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1
PROJECT-M-TRACK-B-BATTLE-ENGINE-STATUS-SEAM-WIRING
PROJECT-M-TRACK-G-STATUS-FIRST-SLICE-CANARY-ENV-RC-GATE
PROJECT-V-TRACK-F-SECOND-SLICE-DEV-LIVE-ROLLBACK-KILL-SWITCH
PROJECT-SP-UI-LOCK-TRACK-H-COMPLETION
PROJECT-SP-DUAL-READ-TRACK-H-COMPLETION
PROJECT-SP-AUTH-TRACK-F-NO-MUTATION-REGRESSION
PROJECT-BATCH1-V2-TRACK-F-MENU-HARDENING
PROJECT-ALIGN-FIX-TRACK-H-COMPLETION
PROJECT-SF-MERGE-TRACK-F-NAVIGATION
PROJECT-SF-MERGE-TRACK-H-COMPLETION
PROJECT-FORGE-CRASH-TRACK-G-HYGIENE
PROJECT-INLINE-CONFIRM-TRACK-E-API-CONTRACT
PROJECT-BETA-TESTING-TRACK-F-REDIS
PROJECT-BETA-TESTING-TRACK-G-REPORTING
PROJECT-GACHA-RATE-SANITY-FINAL-SIGNOFF
```

`Δ vs baseline Pack 89 = 0` — nessuna nuova fail introdotta, nessun
validator indebolito, nessun `fake_PASS`.

---

## 4. Inventory mutation path audit

Audit statico e dinamico delle mutation path di inventario in
`backend/routes/items.py`:

| Endpoint                               | Metodo | server_id richiesto | PSP-check | selector include server_id | hardcoded `"s1"` | account-wide write |
|----------------------------------------|--------|---------------------|-----------|-----------------------------|------------------|---------------------|
| `/api/item-shop/buy`                   | POST   | **SÌ**              | **SÌ**    | **SÌ** (find + upsert)      | **NO**           | **NO**              |
| `/api/inventory/use-exp`               | POST   | **SÌ**              | **SÌ**    | **SÌ** (find + dec)         | **NO**           | **NO**              |
| `/api/hero/skills-upgrade/{id}` (GET)  | GET    | **SÌ**              | **SÌ**    | **SÌ** (find)               | **NO**           | n/a (read-only)     |
| `/api/hero/skill-upgrade`              | POST   | **SÌ**              | **SÌ**    | **SÌ** (find + dec materiali)| **NO**          | **NO**              |
| `/api/inventory` (GET)                 | GET    | richiesto per modalità strict (Pack 89) | **SÌ** se presente | **SÌ** | **NO** | **NO (read-only)** |

Verifica statica `grep server_id="s1" backend/routes/items.py` → 0 occorrenze
attive (rimane unicamente un commento `# nessun hardcoded "s1"; nessun
fallback account-wide.` che documenta l'invariante).

---

## 5. Strict write implementation — dettaglio runtime

Per ciascun endpoint mutante è stata applicata la seguente sequenza
runtime (riferimento `backend/routes/items.py`):

```python
# 1) server_id query param obbligatorio
if not server_id or not isinstance(server_id, str) or not server_id.strip():
    raise HTTPException(status_code=400, detail="SERVER_ID_REQUIRED")
sid = server_id.strip()

# 2) PSP existence check (no auto-create)
psp = await db.player_server_profiles.find_one(
    {"user_id": user_id, "server_id": sid}
)
if not psp:
    raise HTTPException(status_code=409, detail="PLAYER_SERVER_PROFILE_REQUIRED")

# 3) Tutti i selettori inventory/materials/user_heroes includono server_id
await db.inventory.update_one(
    {"user_id": user_id, "server_id": sid, "item_id": req.item_id},
    {"$inc": {"quantity": req.quantity},
     "$setOnInsert": {"server_id": sid, "account_id": user_id,
                      "_slc_pack_90_strict_server_scoped_write": True}},
    upsert=True,
)
```

Invariante di sostituzione (replacement invariant):

```
∀ write su collection inventory:
    selector ⊇ {user_id, server_id, item_id}
    setOnInsert ⊇ {server_id, account_id}
    NO {"_id": ...}
    NO account-wide ({user_id, item_id}) selector
    NO server_id hardcoded ("s1" / valori magici)
```

---

## 6. Item shop buy — server scope

- Endpoint: `POST /api/item-shop/buy?server_id=<sid>`
- Body: `BuyItemRequest{item_id, quantity}`
- Comportamento Pack 90:
  - `400 SERVER_ID_REQUIRED` se `server_id` mancante/blank
  - `409 PLAYER_SERVER_PROFILE_REQUIRED` se nessun PSP per `(user_id, sid)`
  - `404` item non in `EXP_ITEMS ∪ SKILL_MATERIALS`
  - `400` se currency insufficiente (gold/gems)
  - decremento currency su `users` (account-wide è corretto: la valuta
    resta account-wide finché currencies PSP-loader-promotion non avviene
    — feature deferita esplicitamente, cfr. §15)
  - upsert su `inventory` con selector `(user_id, server_id, item_id)`
  - response include `server_id` e flag
    `pack_90_strict_server_scoped_write=true`

---

## 7. Use-exp / consume — server scope

- Endpoint: `POST /api/inventory/use-exp?server_id=<sid>`
- Body: `UseExpItemRequest{user_hero_id, item_id, quantity=1}`
- Comportamento Pack 90:
  - `400 SERVER_ID_REQUIRED` / `409 PLAYER_SERVER_PROFILE_REQUIRED` come §5
  - `inventory.find_one({user_id, server_id, item_id})` — **nessun lookup
    account-wide**
  - hero lookup: `user_heroes.find_one({id, user_id, server_id})` — niente
    cross-server hero leak
  - aggiornamento `user_heroes` scoped da `(id, user_id, server_id)`
  - decremento `inventory` scoped da `(user_id, server_id, item_id)`
  - response include `server_id`, `pack_90_strict_server_scoped_write=true`,
    nuovo `hero_name` con suffisso `"Eroe non trovato per questo server"`
    nel 404 path

---

## 8. Skill / material checks — server scope

- Endpoint read-only: `GET /api/hero/skills-upgrade/{user_hero_id}?server_id=<sid>`
  - hero `(id, user_id, server_id)` + inventory `(user_id, server_id)`
- Endpoint mutante: `POST /api/hero/skill-upgrade?server_id=<sid>`
  - PSP check + hero `(id, user_id, server_id)` + materiali letti con
    `(user_id, server_id, item_id)` + decremento materiali con
    `(user_id, server_id, item_id)` + skill update su `user_heroes`
    `(id, user_id, server_id)`
- Tutti i `find_one`/`update_one` sui materiali skill **passano `server_id`
  esplicitamente**. Nessun materiale viene letto o decrementato senza
  scope di server.

---

## 9. GET /api/inventory — regression guard (Pack 89)

- Comportamento Pack 89 **preservato** integralmente:
  - con `server_id` presente → strict read `(user_id, server_id)` + PSP check
  - senza `server_id` → legacy non-player-facing path, flag
    `inventory_source=legacy_account_wide_deprecated`,
    `legacy_account_inventory_used=true`,
    `_slc_pack_89_legacy_path_warning` valorizzato
  - **NO DB writes** (read-only invariante)
- Validator `validate_v110_pack_89_*` continuano a passare (15/15 tracks);
  rollup Pack 89 → PASS.

---

## 10. Frontend mutation consumer check

Grep su `/app/frontend/` per le mutation path di inventario:

```
/app/frontend/app/item-shop.tsx:35   apiCall('/api/item-shop/buy', POST, body)
/app/frontend/app/inventory.tsx:91   apiCall('/api/inventory/use-exp', POST, body)
```

Stato attuale: **il frontend NON passa ancora `server_id` come query
param** verso questi due endpoint. Con Pack 90 il backend risponderà
`400 SERVER_ID_REQUIRED`, che è esattamente il comportamento desiderato
per **forzare la migrazione consumatori**: nessun bypass silenzioso,
nessun fallback account-wide.

Questo è classificato come **deferred blocker non-bloccante per Pack 90**
(cfr. §15): il pack di interesse è una hardenizzazione runtime backend;
il frontend dev'essere migrato in un pack successivo (vedi §16), assieme
a eventuale propagazione del `server_id` dal contesto utente all'apiCall.

Nota: l'enablement live di reward/progress resta OFF (cfr. §17), quindi
non c'è impatto su utenti reali.

---

## 11. Runtime smoke E2E

Smoke check statico (read-only, niente call live verso staging/live):

| Caso                                                  | Esito atteso                          | Validator-equivalent |
|-------------------------------------------------------|---------------------------------------|----------------------|
| `POST buy` senza `server_id`                          | 400 SERVER_ID_REQUIRED                | static contract OK   |
| `POST buy` con `server_id` ma senza PSP               | 409 PLAYER_SERVER_PROFILE_REQUIRED    | static contract OK   |
| `POST use-exp` su hero di altro server                | 404 "Eroe non trovato per questo server" | static contract OK |
| `POST skill-upgrade` materiale presente su s2 ma non su s1, chiamata con `server_id=s1` | 400 "Materiali insufficienti" | static contract OK |
| `GET inventory?server_id=sX` con PSP esistente        | strict read di sX                     | Pack 89 preservato   |

Nessuna chiamata a `/api/battle/simulate` da staging/live (vincolo
non-negoziabile). Nessuna esecuzione di legacy cleanup. Nessuna
mutazione di `users.team_formation`, `player_level`, `user_heroes` fuori
dallo scope server.

---

## 12. Data invariants

Invarianti dati verificati staticamente e dichiarati:

```
∀ doc ∈ inventory creato/modificato da Pack 90:
    doc.server_id ∈ PSP[user_id]
    doc.server_id != "s1" se la chiamata indica un altro server
    doc.account_id == doc.user_id (mantenuto da $setOnInsert)
    doc._slc_pack_90_strict_server_scoped_write == true (solo per nuovi insert)
∀ doc ∈ user_heroes aggiornato da Pack 90:
    update_one selector contiene (user_id, server_id)
∀ doc ∈ player_server_profiles:
    INVARIATO (nessuna scrittura PSP da Pack 90)
∀ doc ∈ users:
    solo decremento currency (gold/gems) account-wide come da Pack 89;
    NESSUNA mutazione di player_level, team_formation, premium grants
```

`account_wide_inventory_leak_in_server_scoped_path = false`
`copy_s1_to_s2_inventory = false`

---

## 13. Cleanup / rollback

- **Cleanup eseguito**: nessuno (legacy_cleanup_not_executed=true).
- **Rollback plan**: ripristinare la revisione precedente di
  `backend/routes/items.py` (commit Pack 89 — vedi commit history) e
  ripristinare il vecchio MD5 `86ed0118090306a92cb4f8b1cb2f8d74` in
  `data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_md5_rebase_v1.json`.
  Nessuna migration / nessun backfill da invertire.
- **Preflight backup**: ereditato dal Pack 89 (read-only audit dei doc
  inventory); non necessario nuovo backup poiché Pack 90 non muta lo
  schema fisico e non esegue migration.

---

## 14. Live readiness update

```
inventory_strict_write_paths_runtime_ready = true
inventory_strict_read_path_runtime_ready  = true   (ereditato Pack 89)
reward_live                               = false  (OFF, INVARIATO)
progress_live                             = false  (OFF, INVARIATO)
release_readiness_claimed                 = false
postqa_d_gates_unlocked                   = false
public_sync_status                        = pending (no remote available)
```

---

## 15. MD5 rebase (autorizzato da utente)

Riferimento: `data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_md5_rebase_v1.json`

```
file                                : backend/routes/items.py
md5_post_pack_89 (precedente)       : 86ed0118090306a92cb4f8b1cb2f8d74
md5_post_pack_90 (avanzato)         : f887c3ce5eea0a847a1d9a05ae9e2aa5
replacement_invariant_functional    : true
validator_weakening                 : false
fake_PASS                           : false
rebase_reason_pack_90               : strict inventory write paths server scope
historical_reference_preserved      : true
  (storico Pack 84→89 mantenuto nel campo historical_reference,
   incluso il vecchio MD5 post-Pack-89 86ed0118…)
```

Validator `validate_v110_pack_89_md5_rebase.py` → PASS post-rebase.
Rollup `validate_mega_release_acceleration_89_inventory_psp_scoped_rollup.py`
→ PASS (15/15 tracks).

---

## 16. Gate invariant preservation

Tutti i gate Pack 85→89 restano sigillati:

| Gate                                                  | Stato       |
|-------------------------------------------------------|-------------|
| `POSTQA_D_*` unlock                                   | **CHIUSO**  |
| `battle_engine_formula_rewrite`                       | **OFF**     |
| `battle_simulate_called_from_staging_or_live`         | **OFF**     |
| `inventory_schema_migration_executed`                 | **OFF**     |
| `inventory_backfill_executed`                         | **OFF**     |
| `currencies_db_writes` / `story_db_writes` / `equipment_db_writes` | **OFF** |
| `premium_grant` / `currency_grant`                    | **OFF**     |
| `reward_live` / `progress_live`                       | **OFF**     |
| `legacy_cleanup_executed`                             | **OFF**     |
| `destructive_migration` / `delete_of_real_data`       | **OFF**     |
| `player_level_mutation` / `user_heroes_mutation` (cross-server) | **OFF** |
| `team_route_regression`                               | **OFF**     |
| `release_readiness_claimed`                           | **OFF**     |

---

## 17. Safety flags (snapshot)

```json
{
  "fake_PASS": false,
  "validator_weakening": false,
  "release_readiness_claimed": false,
  "inventory_schema_migration_executed": false,
  "inventory_backfill_executed": false,
  "inventory_db_writes_unauthorized": false,
  "inventory_account_wide_write": false,
  "inventory_write_selector_missing_server_id": false,
  "inventory_consume_selector_missing_server_id": false,
  "hardcoded_server_id_s1_in_writes": false,
  "currencies_db_writes": false,
  "story_db_writes": false,
  "equipment_db_writes": false,
  "false_filter_applied_true": false,
  "account_wide_inventory_leak_in_server_scoped_path": false,
  "copy_s1_to_s2_inventory": false,
  "premium_grant": false,
  "currency_grant": false,
  "reward_live": false,
  "progress_live": false,
  "legacy_cleanup_executed": false,
  "destructive_migration": false,
  "delete_of_real_data": false,
  "player_level_mutation": false,
  "user_heroes_cross_server_mutation": false,
  "team_route_regression": false,
  "postqa_d_gates_unlocked": false,
  "battle_engine_formula_rewrite": false,
  "battle_simulate_called_from_staging_or_live": false
}
```

---

## 18. Dichiarazioni esplicite (non-negoziabili)

- **NO account-wide inventory writes** — tutti i selettori di write/consume
  contengono `(user_id, server_id, item_id)`. Verificato staticamente su
  `backend/routes/items.py`.
- **NO hardcoded `s1` inventory writes** — `grep server_id="s1"` su
  `backend/routes/items.py` → 0 occorrenze di codice attive
  (solo un commento descrittivo dell'invariante).
- **Pack 89 GET inventory preserved** — regression guard §9: nessuna
  modifica al comportamento di lettura, validator Pack 89 PASS 15/15.
- **reward / progress live OFF** — `reward_live=false`, `progress_live=false`
  invariato.
- **legacy cleanup NOT executed** — `legacy_cleanup_executed=false`,
  nessuna `users.team_formation` rimossa, nessun documento legacy
  cancellato.
- **NO schema migration / NO backfill** — `inventory_schema_migration_executed=false`,
  `inventory_backfill_executed=false`. Schema fisico inventory già
  server-scoped da Pack 89.
- **NO S1 → S2 inventory copy** — `copy_s1_to_s2_inventory=false`.
- **NO currencies / story / equipment promotion** — deferiti (cfr. §19).
- **NO premium grant / NO currency grant**.
- **NO destructive migration / NO delete of real data**.
- **NO player_level mutation / NO team_route regression**.
- **NO POSTQA_D unlock / NO battle_engine formula rewrite / NO
  /api/battle/simulate dal contesto staging o live**.
- **NO fake_PASS / NO validator weakening** — 1474/29/0/0 deterministico
  su 3 run, baseline 29 OPTIONAL preservata.
- **NO release readiness claim** — Pack 90 è hardenizzazione runtime,
  non promozione live.

---

## 19. Deferred blockers & Next step

### Deferred blockers (documentati, NON eseguiti)

1. **Frontend mutation consumer migration** — `item-shop.tsx` (line 35)
   e `inventory.tsx` (line 91) devono propagare `server_id` come
   query param. Pack candidato: Pack 91 / Pack 91+.
2. **Currencies PSP-scoped loader promotion** — la valuta (gold/gems)
   è ancora account-wide su `users`. Audit + promotion deferita.
3. **Story progress PSP-scoped loader promotion** — deferita.
4. **Equipment PSP-scoped loader promotion** — deferita.
5. **Skill upgrade frontend consumer** — se/quando il frontend chiama
   `/api/hero/skills-upgrade/{id}` o `/api/hero/skill-upgrade`, dovrà
   anch'esso passare `server_id` (oggi nessuna chiamata frontend ai due
   endpoint skill: la migrazione è preventiva).
6. **Inventory onboarding / starter rewards** — NON concessi, futuro pack
   dedicato.
7. **Legacy cleanup pre-Pack-86 user_heroes account-wide** — deferito.

### Next step

- Attendere upload del **Pack 91** (probabile: currencies / story / equipment
  loaders promotion oppure frontend consumer migration).
- Nel frattempo: **nessuna esecuzione di legacy cleanup, nessuna
  promozione live di reward/progress, nessuna mutazione di currency
  o story progress**.

---

## 20. Sync status

```
local_commit_only            = true
public_push_managed_externally = true
no_remote_available          = true
```

---

## 21. Comando di verifica (riproducibilità)

```bash
# 3-run deterministico
for i in 1 2 3; do
  python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | tail -3
done
# Atteso ogni run: Overall: FAIL  (pass=1474, fail=29, miss=0)
# (fail=29 sono TUTTI OPTIONAL noti baseline; REQUIRED_FAIL=0)

# Verifica MD5 rebase
md5sum /app/backend/routes/items.py
# Atteso: f887c3ce5eea0a847a1d9a05ae9e2aa5  /app/backend/routes/items.py

python3 /app/backend/scripts/validate_v110_pack_89_md5_rebase.py
# Atteso: [v110 PACK_89_MD5_REBASE] OK items.py=f887c3ce5eea …

python3 /app/backend/scripts/validate_mega_release_acceleration_89_inventory_psp_scoped_rollup.py
# Atteso: [v110 MEGA_RELEASE_ACCELERATION_89_INVENTORY_PSP_SCOPED_ROLLUP] OK tracks=15/15
```

---

## 22. Post-script — commit hash

> Il SHA verrà inserito qui sotto immediatamente dopo l'esecuzione del
> commit locale (`git add … && git commit -m "feat(pack-90): …"`).

```
commit_hash = <da inserire dopo `git commit`>
```

---

*Fine report Pack 90.*
