# 114 — SLC-F COSMETICS SCHEMA SPLIT REFACTOR (READY_NOT_APPLIED — design-only)

> **Verdict finale:** `SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR_READY_NOT_APPLIED`
> **Tipo task:** **DESIGN-ONLY** — refactor strutturale non applicato in questo task perché richiede DB migration + behavior change + decisione prodotto, tutti esplicitamente vietati dal guardrail. Esito esplicitamente previsto dal prompt.
> **Progress globale:** **96% invariato** (ready-not-applied non incrementa progress; certifica blueprint per un futuro apply gated).
> **Suite master:** 350/350 PASS (+1 validator design-only).

---

## 1. Executive Verdict

✅ **PASS (READY_NOT_APPLIED)** — Audit di refactor cosmetics completato. Lo schema split tra "cosmetic ownership account-wide" e "cosmetic equipped/usage state server-bound" **non è stato applicato in questo task** perché l'audit ha confermato che richiede 3 azioni esplicitamente vietate dal guardrail:

1. **DB migration/backfill** dei doc `user_cosmetics` esistenti per spostare `active_*` in nuova collection.
2. **Behavior change** sui contratti dei 3 endpoint cosmetics (target collection di lettura/scrittura cambia).
3. **Decisione prodotto** non risolta su default state multi-server e inheritance.

Il refactor è stato completamente **progettato** come blueprint multi-fase (A→E) ed è pronto per essere applicato in un futuro task gated con i marker appropriati. Zero diff su `cosmetics.py` o qualunque altro file runtime. Suite 350/350 PASS.

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_COSMETICS_REFACTOR_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=COSMETICS_SCHEMA_SPLIT_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **350/350 PASS** (+1 validator) | ✅ |
| Nuovo validator design-only | PASS | PASS (errors=0) | ✅ |
| Diff su `cosmetics.py` vs HEAD | 0 | 0 | ✅ |
| Decision documented | sì | `READY_NOT_APPLIED` | ✅ |
| Blueprint multi-fase per futuro apply | sì | 5 fasi (A→E) | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_COSMETICS_REFACTOR_APPROVAL=true                  ✅
SLC_F_APPLY_BATCH_SCOPE=COSMETICS_SCHEMA_SPLIT_ONLY      ✅
```

---

## 3. Cosmetics Route Audit Table

| Surface | Endpoint | Line | Operation | Fields | Current Classification | Refactor Action |
|---|---|:-:|---|---|---|---|
| **COS-W1** | `GET /api/cosmetics` | 18 | `db.user_cosmetics.insert_one` (default doc init) | `user_id`, `owned_auras`, `owned_frames`, `active_aura`, `active_frame` | **MIXED** | Split: ownership → `user_cosmetics`; equipped → `user_cosmetics_equipped` (per-server) |
| **COS-W2** | `POST /api/cosmetics/buy` | 41 | `db.user_cosmetics.insert_one` (idempotent init) | `user_id`, `owned_auras`, `owned_frames` | ACCOUNT_WIDE | Keep on ownership collection |
| **COS-W3** | `POST /api/cosmetics/buy` | 50 | `db.user_cosmetics.update_one` (`$push owned_*`, upsert=True) | `owned_auras OR owned_frames` | ACCOUNT_WIDE | Keep on ownership collection |
| **COS-W4** | `POST /api/cosmetics/equip` | 61 | `db.user_cosmetics.update_one` (`$set active_*`, upsert=True) | `active_aura OR active_frame` | **SERVER_BOUND** | **MOVE** target to `user_cosmetics_equipped(user_id, server_id)` — BEHAVIOR CHANGE |
| **COS-W5** | `POST /api/territory/attack` | 104 | `db.territory_control.update_one` (`$inc defense_power`) | `defense_power` | SERVER_BOUND | Out of cosmetics schema scope (territory subsystem) |
| **COS-W6** | `POST /api/territory/attack` | 108 | `db.territory_control.update_one` (`$set guild_id+...`, upsert=True) | `guild_id`, `defense_power`, `captured_at`, `captured_by` | SERVER_BOUND | Out of cosmetics schema scope |

---

## 4. Ownership vs Equipped Classification

**Schema corrente `db.user_cosmetics`** (single doc per `user_id`):

| Campo | Layer canonical | Note |
|---|---|---|
| `user_id` | account-wide | identity |
| `owned_auras: [string]` | **account-wide** | paid cosmetics ownership (per canonical policy) |
| `owned_frames: [string]` | **account-wide** | paid cosmetics ownership |
| `active_aura: string \| null` | **server-bound** | equipped state (per canonical) — conflitto schema |
| `active_frame: string` | **server-bound** | equipped state — conflitto schema |

**Riferimento canonical:** `/app/data/design/server_lifecycle/account_server_data_scope_policy_v1.json` → `paid_cosmetics_account_wide_but_use_requires_hero_on_server` (ownership=account_wide, bonus_activation=server_bound).

**Violazione:** single doc conflate i 2 layer (esattamente l'issue flaggato da Batch-2 audit come MIXED_REQUIRES_REFACTOR).

---

## 5. Refactor Decision Table

| Surface | Safe in this task | Reason |
|---|:-:|---|
| COS-W1 default doc init | ❌ | Inserisce active_* in single doc; in target schema vive in collection diversa ⇒ behavior change |
| COS-W2 idempotent init | ❌ | Dipende da identità della collection ownership (decisione di naming) |
| COS-W3 $push ownership | ❌ | Decisione di rinominare `user_cosmetics` ⇒ `user_cosmetics_ownership` non risolta |
| COS-W4 active_* equip | ❌ | Cambio target collection = behavior change + backfill dei legacy doc richiesto |
| COS-W5/COS-W6 territory | ❌ | Out of cosmetics schema scope (subsistem territory_control) |

**Conclusione:** 0/6 surfaces patchabili in questo task.

---

## 6. Reasons Blocking Apply

1. **`DB_MIGRATION_REQUIRED`** — i doc `user_cosmetics` esistenti contengono `active_*` che devono essere migrati a `user_cosmetics_equipped(user_id, server_id="s1")` per consistency sul read path; senza migrazione GET /cosmetics perderebbe lo stato equipaggiato per utenti esistenti.
2. **`BACKFILL_REQUIRED`** — backfill sincrono di ogni doc esistente; esplicitamente vietato.
3. **`BEHAVIOR_CHANGE_REQUIRED`** — POST /cosmetics/equip cambierebbe collection target; GET /cosmetics cambierebbe a dual-collection read; comportamento runtime osservabile diverso anche se outputs equivalenti.
4. **`PRODUCT_DECISION_REQUIRED_DEFAULT_FRAME`** — su un nuovo server profile, il default `bronze` è uguale o si eredita da s1? Decisione aperta.
5. **`PRODUCT_DECISION_REQUIRED_ACTIVE_INHERITANCE`** — quando un utente apre un secondo server, `active_aura`/`active_frame` si trasferiscono da s1 o si resettano? Decisione aperta.
6. **`CANONICAL_COLLECTION_NAME_DECISION`** — rinominare `user_cosmetics` ⇒ `user_cosmetics_ownership` per chiarezza, o mantenere il nome storico? Decisione che impatta downstream code paths.

---

## 7. Proposed Apply Blueprint (5 fasi gated, per futuri task)

### Phase A — Design-only (questo task)
- ✅ Documentare schema target, dual-collection read path, write splits, default frame policy, inheritance rules. NO runtime change.
- ✅ Deliverable: questo report + audit JSON con audit table, decision table, reasons blocking, blueprint.

### Phase B — Migration gated
- **Markers:** `SLC_F_COSMETICS_BACKFILL_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=COSMETICS_BACKFILL_ONLY`
- Backfill TUTTI i doc esistenti `user_cosmetics`: copy `active_*` → new doc `user_cosmetics_equipped(user_id, server_id="s1")`. NO field removal yet (dual-write compat).
- Validator: counts match, per-doc backfill verified.

### Phase C — Dual-write runtime
- **Markers:** `SLC_F_COSMETICS_DUAL_WRITE_APPROVAL=true`
- Patch `cosmetics.py` per scrivere `active_*` su BOTH old field on `user_cosmetics` AND new `user_cosmetics_equipped` (dual-write); read da new collection con fallback to old.
- Rollback: revert a single-write su old collection.

### Phase D — Cutover runtime
- **Markers:** `SLC_F_COSMETICS_CUTOVER_APPROVAL=true`
- Dopo dual-write stabilizzato, stop scrittura `active_*` su `user_cosmetics`; read SOLO da new collection.

### Phase E — Cleanup
- **Markers:** `SLC_F_COSMETICS_CLEANUP_APPROVAL=true`
- Backfill che rimuove campi `active_*` orfani dai doc `user_cosmetics`.

---

## 8. Files Changed

### File di codice runtime patchati
**NESSUNO.** Task = design-only.

### File aggiunti (non-codice runtime)
- `data/design/system_safety/slc_f_cosmetics_refactor_audit_v1.json` (canonical audit + blueprint)
- `backend/scripts/validate_slc_f_cosmetics_refactor_v1.py` (validator design-only)
- `data/design/server_lifecycle/_slc_f_cosmetics_refactor_v1_result.json` (validator output PASS)
- `docs/divine/114_SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR.md` (questo report)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga OPTIONAL)

---

## 9. No Apply Rationale

Il prompt prevede esplicitamente questo esito:

> *"Se il refactor richiede migrazione DB, backfill o decisione prodotto, fermati con `SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR_READY_NOT_APPLIED`."*

L'audit ha confermato che **tutti e 3 i blocking conditions** sono presenti:
- ✅ Migrazione DB richiesta
- ✅ Backfill richiesto
- ✅ Decisione prodotto richiesta (default state multi-server + inheritance)

Pertanto NON è stato applicato alcun patch runtime. È stato invece prodotto un blueprint dettagliato per il futuro apply gated multi-fase.

---

## 10. Suite Result

```
Overall: PASS  (pass=350, fail=0, miss=0)
Δ vs Consolidation end-state: +1 PASS (validator design-only aggiunto)
JSON report: /tmp/slc_f_cos_suite.json
```

---

## 11. API Smoke Result

| Endpoint | HTTP | Note |
|---|---|---|
| `GET /api/heroes` | 200, **100** elementi | catalogo intatto |
| `GET /api/heroes/primordial_gaia` | **404** | esclusione preservata |
| `GET /api/heroes/borea` | **200** | catalog-only inert |
| `GET /api/cosmetics` | 401 | auth richiesta, no 5xx, **comportamento invariato** |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato |

✅ Zero 5xx su cosmetics routes. Behavior identico al pre-task.

---

## 12. Invariants

✅ Tutti preservati: heroes=100, gaia=404, borea/greek_borea=200, AF2-N cap=50000 allowlist=2500, SLC-G migration_id preserved, env flags unset, Phase 11=false, **zero diff su `backend/routes/*.py`** (inclusi `cosmetics.py`), tutti i marker SLC-F precedenti preservati.

---

## 13. Forbidden Scope Verification

| Scope vietato | Esito |
|---|:-:|
| `backend/routes/cosmetics.py` | ✅ 0 diff vs HEAD |
| `backend/routes/economy.py` | ✅ 0 diff |
| `backend/routes/*.py` (tutti gli altri) | ✅ 0 diff |
| AF2-N files | ✅ intatti |
| Combat/battle files | ✅ intatti |
| Character Bible (`sanctuary.py`, `db.heroes`) | ✅ non toccata |
| Housing runtime / `/api/housing` | ✅ non implementato |
| SLC-H runtime endpoints | ✅ non implementati |
| Second server / `SERVER_PROFILES_RUNTIME_ENABLED` | ✅ unset |
| Phase 11 | ✅ non eseguita |
| Frontend `/app/frontend/app/*` | ✅ nessuna modifica |
| Catalog/pricing (AURAS, AVATAR_FRAMES) | ✅ invariati |
| Drift docs gacha/summon (7) | ✅ non corretti |
| DB writes / migrations | ✅ nessuno |
| Behavior changes | ✅ nessuno |

**Verifica anti-falso-positivo:** `cosmetics.py` NON contiene `from utils.server_scope import ensure_server_scope` (skip reale, non patch silente). Schema markers originali tutti preservati (`owned_auras`, `owned_frames`, `active_aura`, `active_frame`, `user_cosmetics`).

---

## 14. Risk Assessment Post-Audit

| Rischio | Severità | Mitigazione |
|---|:-:|---|
| Schema mixed cosmetics resta in produzione | 🟡 media | Coperto dal blueprint multi-fase; non urgente perché single-server attivo, default `s1` fallback funziona |
| Cliente migrato a multi-server con default frame errato | 🟢 informativa | Decisione prodotto da risolvere PRIMA della fase B |
| Drift tra Phase A (design) e implementazione reale | 🟢 informativa | Validator design-only verifica integrità blueprint |
| Redis rate-limit stability | 🟡 media | `bash /app/ops/ensure_redis_rate_limit.sh` |

Nessun rischio severità **alta** introdotto da questo task (zero modifiche runtime).

---

## 15. Recommended Next Step

🟢 **Quick-win immediato:** `HOUSEKEEPING_DRIFT_DOCS_GACHA_SUMMON_ONLY` (alternativa B dall'audit di consolidamento)
- Rationale: metadata-only, rischio informativo, sblocca un quick-win documentale prima di affrontare il refactor di economy.py.
- Marker richiesti: `SLC_F_DRIFT_DOCS_CLEANUP_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=DRIFT_DOCS_GACHA_SUMMON_ONLY`.

🟠 **Refactor strutturale prossimo (a maggior rischio):** `ECONOMY_REFACTOR_PAID_FREE_SPLIT` (alternativa A dall'audit di consolidamento)
- Rationale: prerequisito per SLC-H live wiring (rimozione legacy `/server/select`).

🔵 **Cosmetics refactor — futuro apply gated multi-fase:**
- Phase B (Migration backfill): `SLC_F_COSMETICS_BACKFILL_APPROVAL=true` + `SLC_F_APPLY_BATCH_SCOPE=COSMETICS_BACKFILL_ONLY`
- Phase C (Dual-write): `SLC_F_COSMETICS_DUAL_WRITE_APPROVAL=true`
- Phase D (Cutover): `SLC_F_COSMETICS_CUTOVER_APPROVAL=true`
- Phase E (Cleanup): `SLC_F_COSMETICS_CLEANUP_APPROVAL=true`
- **Prerequisito esterno:** product decision document su default state multi-server + inheritance rules.

⚠️ **Esplicitamente NON raccomandato ora:**
- BATCH_3 AF2-N routing, BATCH_4 combat/battle
- Character Bible / sanctuary split
- Gacha/summon scope task
- SLC-H live wiring (richiede economy refactor prima)
- Phase 11 / secondo server

---

## 16. Updated Progress Estimate

| Fase | Stato pre-task | Stato post-task |
|---|---|---|
| SLC-F Batch-0/1, Batch-1B, Batch-2, Equipment-scope, Raids-equipment, GVG-war, Unique-items | ✅ done | ✅ done |
| SLC-F Minor-Audit + Post-microbatch Consolidation | ✅ ready | ✅ ready |
| **SLC-F Cosmetics Schema Split — Phase A design-only** | 🟡 pending | ✅ **READY_NOT_APPLIED (blueprint ready)** |
| SLC-F Cosmetics Phase B (migration backfill) | 🔵 backlog | 🔵 backlog gated (richiede product decision) |
| SLC-F Cosmetics Phase C/D/E | 🔵 backlog | 🔵 backlog gated |
| SLC-F Economy refactor | 🔵 backlog | 🔵 backlog |
| Drift docs housekeeping | 🔵 backlog | 🟢 quick-win recommended |
| SLC-F Batch-3, Batch-4, gacha/summon, Character Bible split | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **96% invariato** (READY_NOT_APPLIED non incrementa progress; blueprint completo certificato per futuro apply gated multi-fase).

---

## 17. Markers di audit (riferimenti rapidi)

- `audit_id`: `slc_f_cosmetics_refactor_20260523T200524Z_dee18b8c`
- `audit_executed_at_utc`: `2026-05-23T20:05:24+00:00`
- `decision`: `READY_NOT_APPLIED`
- `verdict_target`: `SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR_READY_NOT_APPLIED` → ✅ **RAGGIUNTO**
- Diff `cosmetics.py` vs HEAD: **0 righe**
- Tutti i 10 marker SLC-F precedenti preservati
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`

---

**FINE REPORT 114_SLC_F_COSMETICS_SCHEMA_SPLIT_REFACTOR.md**
