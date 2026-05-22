# 99 · SLC-G — DEFAULT S1 MIGRATION COMMIT GATED PREP

**Stato finale**: ✅ `READY_TO_COMMIT_NOT_APPLIED`
**Modalità**: `PRE_COMMIT / GATED / BACKUP-FIRST / DRY-RUN-FIRST`
**Approvazione esplicita utente**: ❌ **NON presente** nel prompt corrente → nessuna scrittura DB eseguita
**Suite globale**: `RM1.31-B` → **323 PASS / 0 FAIL / 0 MISS** (317 → 323, +6 SLC-G OPTIONAL)
**Baseline diff RM1.32-PRE**: ✅ PASS

---

## 1. Obiettivo

Preparare il percorso di **commit di default `server_id=s1`** per i dati server-bound,
in vista della futura transizione runtime al modello multi-shard, **senza** mai
eseguire scritture DB irreversibili in assenza di approvazione esplicita.

Tutti i requisiti hard-guardrail sono stati rispettati: nessuna modifica a runtime,
combat, gacha, roster, Character Bible, cataloghi, AF2-N, Redis runtime, route
runtime, feature flag o legacy fallback.

---

## 2. Invarianti post-task

| Check | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` count | 100 | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | 404 | **404** ✅ |
| `GET /api/heroes/borea` | 200 inert | **200** ✅ |
| `GET /api/heroes/greek_borea` | 200 inert | **200** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | **unset** ✅ |
| AF2-N cap | 50000 | **50000** ✅ |
| AF2-N allowlist | 2500 | **2500** ✅ |
| `migration_applied` | false | **false** ✅ |
| `db_write` | false | **false** ✅ |
| `route_patch_applied` (SLC-F) | false | **false** ✅ |

---

## 3. Artefatti creati

### 3.1 Contratti JSON (`/app/data/design/server_lifecycle/`)

| File | Scopo |
|---|---|
| `slc_g_default_s1_migration_preflight_v1.json` | Preflight: verifica prerequisiti SLC-A/C/BE/F/D + baseline invariants |
| `slc_g_default_s1_backfill_plan_v1.json` | Piano backfill dry-run: ordine, set-only-if-missing, idempotente, index intent listing senza creazione |
| `slc_g_write_gate_contract_v1.json` | Contratto **12 gate** (G1..G12) tutti obbligatori prima di qualsiasi scrittura |
| `slc_g_backup_manifest_contract_v1.json` | Contratto backup mongodump + checksum + metadata per collection |
| `slc_g_rollback_plan_v1.json` | Piano rollback con marker field `_slc_g_default_s1_set`, RTO 30/120 min |
| `slc_g_idempotency_contract_v1.json` | Contratto idempotency: rerun zero-write, no duplicates, no overwrite |
| `slc_g_readiness_rollup_v1.json` | Roll-up readiness con criterio default `READY_TO_COMMIT_NOT_APPLIED` |

### 3.2 Validator / Simulator Python (`/app/backend/scripts/`)

| Script | Tipo |
|---|---|
| `validate_slc_g_preflight_v1.py` | Preflight (read-only) |
| `simulate_slc_g_default_s1_backfill_dryrun.py` | Simulator dry-run su MongoDB live (READ-ONLY) |
| `validate_slc_g_write_gate_contract_v1.py` | Validator gate contract |
| `validate_slc_g_rollback_plan_v1.py` | Validator rollback plan |
| `validate_slc_g_idempotency_contract_v1.py` | Validator idempotency |
| `validate_slc_g_combo_v1.py` | Orchestratore combo + decisione final_status |

---

## 4. Dry-run simulation — risultato (READ-ONLY)

Eseguito `simulate_slc_g_default_s1_backfill_dryrun.py` contro MongoDB live
in modalità **read-only** (nessuna `update_one`, `update_many`, `insert_*`).

### 4.1 Totali

| Metrica | Valore |
|---|---|
| Collection server-bound presenti | **8 / 16** |
| Collection server-bound assenti (legacy/non ancora create) | **8 / 16** |
| Documenti che riceverebbero `server_id=s1` | **6 916** |
| Documenti che riceverebbero `account_id=user_id` | **6 916** |
| **`unsafe_unknown` totali** | ⚠️ **2** (in `guilds`) |

### 4.2 Dettaglio per collection (presenti)

| Collection | Total docs | Would set `server_id=s1` | Would set `account_id=user_id` | unsafe_unknown |
|---|---|---|---|---|
| `user_heroes` | 1961 | 1966* | 1966 | 0 |
| `teams` | 21 | 21 | 21 | 0 |
| `inventory` | 10 | 10 | 10 | 0 |
| `story_progress` | 1 | 1 | 1 | 0 |
| `guilds` | 2 | 2 | 0 | **2** ⚠️ |
| `user_affinity_state` | 1914 | 1914 | 1914 | 0 |
| `gift_transaction_ledger` | 502 | 502 | 502 | 0 |
| `user_gift_inventory` | 2500 | 2500 | 2500 | 0 |

*\* La differenza fra `total=1961` e `would_set=1966` è dovuta a `estimated_document_count`
vs `count_documents` esatto su `user_heroes`: il dry-run è informativo, non vincolante.*

### 4.3 Collection assenti (mai create finora)

`servers`, `server_profiles`, `server_wallets_free`, `gacha_history`,
`arena_rankings`, `server_cosmetics`, `equipped_cosmetics`, `event_progress`

→ verranno create al primo write gated; nessuna pressione di backfill.

### 4.4 Collection account-wide (escluse dal backfill `server_id`)

`accounts_wallet_paid`, `accounts_wallet_paid_ledger`, `account_cosmetics`
→ assenti oggi; resteranno **senza** `server_id` per design.

### 4.5 Collection mixed

`users` (25 docs) → mai riceverà `server_id`; potrebbe ricevere `account_id`
(default = `user_id`) solo a gate aperto.

---

## 5. Stato dei 12 gate (read-only check)

| Gate | Descrizione | Stato |
|---|---|---|
| G1 | Prior SLC combo PASS | ✅ |
| G2 | API smoke invariants | ✅ |
| G3 | AF2-N invariants (cap=50k, allowlist=2.5k) | ✅ |
| G4 | Runtime flags unset | ✅ |
| G5 | Protected file no-diff | ✅ (baseline diff RM1.32-PRE PASS) |
| G6 | Dry-run report present | ✅ |
| G7 | Backup manifest present | ✅ (contratto design-only) |
| G8 | Rollback plan present | ✅ |
| G9 | Idempotency contract present | ✅ |
| G10 | `unsafe_unknown_count == 0` | ❌ **2 in guilds** — BLOCCANTE |
| G11 | Approval marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true` nel prompt | ❌ **assente** |
| G12 | Baseline diff RM1.32-PRE PASS | ✅ |

**Conclusione gating**: 2 gate non soddisfatti (G10 + G11) → **nessuna scrittura
eseguibile**. Anche se l'utente avesse fornito approvazione esplicita, G10 richiede
prima una bonifica dei 2 documenti `unsafe_unknown` in `guilds`.

---

## 6. Registrazione suite

I 6 task SLC-G sono registrati nella sezione OPTIONAL di
`/app/backend/scripts/run_hero_skill_kit_validator_suite.py` con prefisso `SLC-G-*`:

```
SLC-G-PREFLIGHT
SLC-G-BACKFILL-DRYRUN
SLC-G-WRITE-GATE-CONTRACT
SLC-G-ROLLBACK-PLAN
SLC-G-IDEMPOTENCY-CONTRACT
SLC-G-COMBO
```

Tutti `[PASS]` exit code `0`. Nessun task pre-esistente indebolito.

---

## 7. Risultato suite globale

```
RM1.31-B — Hero Skill Kit Validator Suite Runner
Overall: PASS  (pass=323, fail=0, miss=0)
JSON report: /app/backend/reports/slc_g_final_suite_run.json
```

Delta vs baseline pre-SLC-G: **+6 OPTIONAL** (317 → 323). Nessuna regressione.

---

## 8. Guardrail rispettati

- ✅ **NO** modifiche a `battle_engine.py`, `battle_core.py`, `combat.tsx`
- ✅ **NO** modifiche a `affinity_gift_spend.py`, AF2-N, Stage4, Redis runtime
- ✅ **NO** modifiche a gacha, roster, Character Bible, cataloghi hero/skill/DW, final_numbers, asset
- ✅ **NO** apertura secondo server
- ✅ **NO** runtime route patch
- ✅ **NO** feature flag enable (SERVER_PROFILES_RUNTIME_ENABLED, SECOND_SERVER_OPENING_ENABLED restano unset)
- ✅ **NO** rimozione legacy fallback
- ✅ **NO** phase 11
- ✅ **NO** indebolimento validator

Tutti i 7 JSON SLC-G hanno `design_only=true`, `db_write=false`,
`migration_applied=false`. La simulation dry-run usa esclusivamente
`estimated_document_count` e `count_documents` (read-only).

---

## 9. Verdict finale

> ## ✅ `READY_TO_COMMIT_NOT_APPLIED`
>
> SLC-G è **pronto a fornire piani e simulazioni di commit**, ma poiché il
> prompt corrente NON contiene il marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true`,
> nessuna scrittura DB è stata eseguita né autorizzata. Inoltre, il gate G10
> (`unsafe_unknown_count == 0`) **non è soddisfatto**: 2 documenti in `guilds`
> non hanno né `user_id` né `account_id` derivabile e dovranno essere classificati
> manualmente prima di qualsiasi tentativo di commit reale.

---

## 10. Prossimi passi (gated, NON eseguiti)

- **Bonifica `unsafe_unknown` in `guilds`** (2 documenti) prima di tentare G10
- **SLC-H** (P1): server selection endpoint (design-only)
- **COSMETIC-B/C/D/E** (P2): read-only/inert
- **Managed Redis Live / Alerting Sink Live** (P3): pendono env vars
- Eventuale flip a `READY_TO_COMMIT` solo dopo:
  1. Approvazione esplicita utente con marker `SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true`
  2. Tutti i 12 gate PASS (incluso G10 dopo bonifica)
  3. Backup manifest realmente generato (env `SLC_G_BACKUP_TARGET_DIR` impostata)
  4. Creazione (separata, gated) di apply script + rollback script

Nessuno di questi è oggetto del task corrente.
