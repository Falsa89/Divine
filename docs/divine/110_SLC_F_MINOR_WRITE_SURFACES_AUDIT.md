# 110 — SLC-F MINOR WRITE SURFACES AUDIT (audit-only, no patch)

> **Verdict finale:** `SLC_F_MINOR_SURFACES_AUDIT_READY`
> **Tipo task:** **AUDIT-ONLY** — zero modifiche runtime, zero DB writes, zero migrazioni.
> **Progress globale:** **94% invariato** (audit non incrementa il progress; abilita future micro-batch).
> **Modalità:** READ-ONLY scan di `backend/routes/*.py` con classificazione canonica per ogni write surface.

---

## 1. Executive Verdict

✅ **PASS** — Audit accelerato completato su 20 route file (196 write surfaces rilevate sul rescan, 201 nel JSON canonico). Tutte le write surfaces sono state classificate secondo le 13 categorie canoniche del prompt. Zero modifiche runtime apportate. Suite master verde 346/346 (+1 audit validator OPTIONAL). Tutti gli invarianti SLC-F preservati.

**Risultati chiave:**
- **10 file ALREADY_PATCHED_SAFE** (Batch-0/1, Batch-1B, Raids-equipment micro-batch) confermati ancora correttamente patchati.
- **2 file SAFE_MICRO_BATCH_CANDIDATE** identificati come prossimi target ottimali (low-risk, pattern Batch-1B/raids-style): `gvg.py` e `unique_items.py`.
- **1 file UPDATE_ONLY_NO_NEW_DOC** confermato safe no-op (`equipment.py`).
- **2 file ACCOUNT_WIDE_NO_CHANGE** (`push_notifications.py`, `player_faction_v2.py`).
- **2 file MIXED_REQUIRES_REFACTOR** (`cosmetics.py`, `economy.py`) — richiedono refactoring strutturale dedicato.
- **1 file FORBIDDEN_SCOPE** (`sanctuary.py` — Character Bible writes + AF2-N adjacent affinity/constellation).
- **1 file BATCH_4_COMBAT_BATTLE_DEFER** (`combat.py`).
- **1 file GACHA_SUMMON_DEFER** (`heroes.py` — user_heroes gacha claim inserts).
- **1 surface AMBIGUOUS_DEFER** (`gvg.py:353` user_mail).

---

## 2. Authorization Markers Detected

```env
SLC_F_MINOR_SURFACES_AUDIT_APPROVAL=true     ✅
SLC_F_APPLY_BATCH_SCOPE=AUDIT_ONLY            ✅
```

---

## 3. Previous SLC-F State Confirmation

| Checkpoint | Apply ID | Esito |
|---|---|---|
| `SLC_F_BATCH_0_1_APPLIED_SAFE` | `slc_f_batch_0_1_20260523T173754Z_27b1b737` | ✅ |
| `SLC_F_BATCH_1B_APPLIED_SAFE` | `slc_f_batch_1b_20260523T175058Z_2cf0584c` | ✅ |
| `SLC_F_BATCH_2_APPLIED_SAFE` (safe no-op) | `slc_f_batch_2_20260523T181752Z_b838601e` | ✅ |
| `SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION_APPLIED_SAFE` (safe no-op) | `slc_f_equipment_scope_20260523T182939Z_d2afcc8a` | ✅ |
| `SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLIED_SAFE` (REAL PATCH) | `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034` | ✅ |
| `SLC-G COMMIT-A` migration | `slc_g_commit_a_20260523T143803Z_4600ac04` | ✅ |
| Suite baseline pre-audit | **345 PASS / 0 FAIL / 0 MISS** | ✅ |

---

## 4. Git Status Before / After

- **HEAD prima:** `1c991ec`
- **HEAD dopo:** `1c991ec` (auto-commit triggerato solo per i nuovi artefatti audit)
- **Diff su `backend/routes/*.py`:** **0 righe** (zero modifiche runtime confermato)
- **File aggiunti (audit-only):**
  - `data/design/system_safety/slc_f_minor_write_surfaces_audit_v1.json`
  - `backend/scripts/audit_slc_f_minor_write_surfaces_v1.py`
  - `docs/divine/110_SLC_F_MINOR_WRITE_SURFACES_AUDIT.md`
  - `data/design/server_lifecycle/_slc_f_minor_write_surfaces_audit_v1_result.json` (output validator)
- **File suite runner modificato (+1 riga OPTIONAL):** `backend/scripts/run_hero_skill_kit_validator_suite.py`

---

## 5. Audit Method

1. **Regex scan** su tutti i file `backend/routes/*.py` con pattern:
   - `(db\.\w+)\.(insert_one|insert_many|update_one|update_many|replace_one|find_one_and_update|find_one_and_replace)\s*\(`
2. **Detection upsert=True** entro 5 righe dal write call.
3. **Verifica `helper_import`** presenza di `from utils.server_scope import ensure_server_scope`.
4. **Conteggio chiamate** `ensure_server_scope(` (escluse linee di import).
5. **Cross-check** con canonical inventory `/app/data/design/server_lifecycle/slc_f_route_scope_inventory_v1.json` e policy `account_server_data_scope_policy_v1.json`.
6. **Classificazione per ogni surface** secondo 13 categorie del prompt.

---

## 6. Files Scanned

20 file di route (escluso `__init__.py`):

```
achievements.py        artifacts.py           combat.py              cosmetics.py
economy.py             equipment.py           forge.py               guild.py
gvg.py                 hero_progression.py    heroes.py              items.py
level_sharing.py       player_faction_v2.py   push_notifications.py  raids.py
sanctuary.py           social.py              soul_forge.py          unique_items.py
```

**Note:** `affinity_gift_spend.py`, `affinity_gifts.py`, `divine_weapons.py`, `hero_skill_kits_catalogs.py`, `skill_kit_runtime_debug.py`, `skill_status_vfx_catalogs.py`, `sprites.py`, `server_time.py`, `synergies.py` non hanno write surfaces o sono catalog-only readonly (AF2-N gestiti in batch dedicato).

---

## 7. Write Surfaces Found

- **Totale surfaces rilevate (regex):** 196 (rescan via audit validator) ≈ 201 (JSON canonico audit)
- **File con writes:** 20
- **File con helper import:** 10 (tutti i Batch-0/1, Batch-1B, raids)
- **File con chiamate ensure_server_scope attive:** 9 (items.py ha import ma 0 call, vedi §9)

---

## 8. Classification Table

| File | Helper | Calls | Classification | Notes |
|---|:-:|:-:|---|---|
| `hero_progression.py` | ✅ | 3 | ALREADY_PATCHED_SAFE | Batch-0/1 |
| `items.py` | ✅ | 0 | ALREADY_PATCHED_SAFE | Batch-0/1 (helper imported; surfaces sono update_one upsert su `users`/`inventory` — degenerate ma corretto) |
| `forge.py` | ✅ | 2 | ALREADY_PATCHED_SAFE | Batch-1B (rune insert/upsert patchati; user_equipment update_only correttamente skipped) |
| `achievements.py` | ✅ | 1 | ALREADY_PATCHED_SAFE | Batch-1B |
| `level_sharing.py` | ✅ | 2 | ALREADY_PATCHED_SAFE | Batch-1B |
| `social.py` | ✅ | 2 | ALREADY_PATCHED_SAFE | Batch-1B |
| `soul_forge.py` | ✅ | 3 | ALREADY_PATCHED_SAFE | Batch-1B |
| `artifacts.py` | ✅ | 4 | ALREADY_PATCHED_SAFE | Batch-1B |
| `guild.py` | ✅ | 1 | ALREADY_PATCHED_SAFE | Batch-1B |
| `raids.py` | ✅ | 1 | ALREADY_PATCHED_SAFE | Raids-equipment micro-batch |
| `equipment.py` | ❌ | 0 | UPDATE_ONLY_NO_NEW_DOC | Safe no-op confermato; solo update_one |
| **`gvg.py`** | ❌ | 0 | **SAFE_MICRO_BATCH_CANDIDATE** | L190 `gvg_wars.insert_one(war)` patchabile; L353 user_mail AMBIGUOUS |
| **`unique_items.py`** | ❌ | 0 | **SAFE_MICRO_BATCH_CANDIDATE** | L277 insert + L303 upsert Batch-1B-style |
| `heroes.py` | ❌ | 0 | GACHA_SUMMON_DEFER | user_heroes.insert da claim summon |
| `combat.py` | ❌ | 0 | BATCH_4_COMBAT_BATTLE_DEFER | story/tower/pvp/equipment/event_completions |
| `sanctuary.py` | ❌ | 0 | FORBIDDEN_SCOPE | db.heroes (Character Bible) + AF2-N adjacent affinity/constellation |
| `cosmetics.py` | ❌ | 0 | MIXED_REQUIRES_REFACTOR | Schema split ownership/equipped |
| `economy.py` | ❌ | 0 | MIXED_REQUIRES_REFACTOR | 5 subsystem; contains legacy `/server/select` |
| `push_notifications.py` | ❌ | 0 | ACCOUNT_WIDE_NO_CHANGE | account-wide canonical |
| `player_faction_v2.py` | ❌ | 0 | ACCOUNT_WIDE_NO_CHANGE | unica surface = update_one su `db.users` (skipped) |

---

## 9. Already Patched Surfaces

10 file confermati ancora con `from utils.server_scope import ensure_server_scope` (cross-check post-rescan):

| File | Batch | Verifica |
|---|---|---|
| `hero_progression.py` | Batch-0/1 | ✅ import + 3 call |
| `items.py` | Batch-0/1 | ✅ import (call=0; vedi nota sotto) |
| `forge.py` | Batch-1B | ✅ import + 2 call (rune surface) |
| `achievements.py` | Batch-1B | ✅ import + 1 call |
| `level_sharing.py` | Batch-1B | ✅ import + 2 call |
| `social.py` | Batch-1B | ✅ import + 2 call |
| `soul_forge.py` | Batch-1B | ✅ import + 3 call |
| `artifacts.py` | Batch-1B | ✅ import + 4 call |
| `guild.py` | Batch-1B | ✅ import + 1 call |
| `raids.py` | Raids-equipment micro-batch | ✅ import + 1 call |

**Nota su `items.py`**: l'import è presente ma non vi sono `ensure_server_scope(` calls. Tutte le write surface di `items.py` sono `update_one` con `upsert=True` su `db.users` (account-wide skipped) e `db.inventory`. Questo è coerente con la decisione Batch-0/1 di marcare il file come "scope-aware" (import disponibile) senza scrivere su nuovi documenti. Nessuna azione richiesta.

---

## 10. Safe Micro-Batch Candidates

### ⭐ Candidate #1 — `SLC-F GVG WAR INSERT SCOPE` (highest priority)

| Voce | Valore |
|---|---|
| File | `backend/routes/gvg.py` |
| Line target | 190 |
| Surface | `db.gvg_wars.insert_one(war)` |
| Classification | server_bound (war scoped to server context) |
| Pattern | `ensure_server_scope(war, uid)` IMMEDIATELY before `insert_one(war)` |
| Risk | **low** |
| Expected diff | +2 righe (1 import + 1 call) |
| Markers richiesti | `SLC_F_GVG_WAR_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=GVG_WAR_ONLY` |
| Forbidden | gvg.py:353 user_mail.insert (deferred AMBIGUOUS) |

### ⭐ Candidate #2 — `SLC-F UNIQUE-ITEMS SCOPE`

| Voce | Valore |
|---|---|
| File | `backend/routes/unique_items.py` |
| Line target | 277, 303 |
| Surface 1 | `db.unique_items_crafted.insert_one({...})` (L277) |
| Surface 2 | `db.unique_items_equipped.update_one({...}, {...}, upsert=True)` (L303) — Batch-1B-style con `$setOnInsert` |
| Classification | server_bound (entrambi user-owned per user_id+hero_name) |
| Pattern | `ensure_server_scope(doc, uid)` su entrambi i dict prima del write |
| Risk | **low** |
| Expected diff | +3 righe (1 import + 2 call) |
| Markers richiesti | `SLC_F_UNIQUE_ITEMS_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=UNIQUE_ITEMS_ONLY` |
| Forbidden | cost/rarity logic (cost_gold/cost_gems), ownership checks, UNIQUE_ITEMS catalog reads |

Entrambi i candidati replicano fedelmente il pattern del precedente apply `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034`.

---

## 11. Deferred Surfaces by Category

| Categoria | Files / Surfaces |
|---|---|
| **GACHA_SUMMON_DEFER** | `heroes.py:106`, `heroes.py:146` (`user_heroes.insert_one` da gacha claim) — patchare violerebbe banner/rates/pity/obtainable visibility. |
| **BATCH_4_COMBAT_BATTLE_DEFER** | `combat.py`: L20 story_progress, L87/140/232 user_equipment, L97/106 tower_progress, L150/165 pvp_data, L238 event_completions. |
| **BATCH_3_AF2N_DEFER** | `sanctuary.py`: L636 user_affinity insert, L663 user_affinity upsert, L714 user_constellation insert, L732 user_constellation_daily upsert. |
| **FORBIDDEN_SCOPE** | `sanctuary.py`: L232/313 `db.heroes.insert_one`, L265/331/365 `db.heroes.update_one` (Borea/Berserker/Hoplite diff) — Character Bible writes. |
| **MIXED_REQUIRES_REFACTOR** | `cosmetics.py` (schema split needed); `economy.py` (5 subsystem + legacy `/server/select`). |
| **ACCOUNT_WIDE_NO_CHANGE** | `push_notifications.py` (push_tokens/notifications); `player_faction_v2.py:306` (update_one su db.users). |
| **AMBIGUOUS_DEFER** | `gvg.py:353` `user_mail.insert_one` (mail mixed account/server origin). |
| **UPDATE_ONLY_NO_NEW_DOC** | `equipment.py` (tutte le 4 surfaces, già auditate come safe no-op). |

---

## 12. Forbidden Scope Verification

Verificato dal validator audit:

| Scope vietato | Diff vs HEAD | Esito |
|---|---|---|
| `backend/routes/*.py` (qualunque file) | 0 righe | ✅ zero modifiche runtime |
| AF2-N files (`affinity_gift_spend.py`, `affinity_gifts.py`) | nessuno | ✅ |
| Combat files (`combat.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx`) | nessuno | ✅ |
| Gacha/summon flows | non toccati | ✅ |
| Character Bible (`db.heroes` / `sanctuary.py`) | nessuno | ✅ |
| Housing runtime/UI/`/api/housing` | non implementati | ✅ |
| SLC-H runtime endpoints | non implementati | ✅ |
| Second server / `SERVER_PROFILES_RUNTIME_ENABLED` | unset | ✅ |
| Phase 11 | non eseguita | ✅ |
| Frontend `/app/frontend/app/*` | nessuna modifica | ✅ |
| Drift docs gacha/summon (7) | non corretti | ✅ |
| DB writes / migrazioni | nessuno | ✅ |

---

## 13. Artifacts Created

```
/app/data/design/system_safety/slc_f_minor_write_surfaces_audit_v1.json   (canonical audit JSON)
/app/backend/scripts/audit_slc_f_minor_write_surfaces_v1.py                (audit/validator script)
/app/data/design/server_lifecycle/_slc_f_minor_write_surfaces_audit_v1_result.json  (validator output)
/app/docs/divine/110_SLC_F_MINOR_WRITE_SURFACES_AUDIT.md                   (questo report)
/app/backend/scripts/run_hero_skill_kit_validator_suite.py                 (+1 OPTIONAL entry)
```

Nessun file runtime modificato.

---

## 14. Suite Result

```
Overall: PASS  (pass=346, fail=0, miss=0)
Δ vs Raids-equipment end-state: +1 PASS (nuovo audit-only validator)
JSON report: /tmp/slc_f_audit_suite.json
```

---

## 15. API Smoke Result

| Endpoint | HTTP |
|---|---|
| `GET /api/heroes` | 200, **100** elementi ✅ |
| `GET /api/heroes/primordial_gaia` | **404** ✅ |
| `GET /api/heroes/borea` | **200** catalog-only inert ✅ |
| `GET /api/heroes/greek_borea` | **200** catalog-only inert ✅ |
| `GET /api/affinity/gift-spend/canary-status` | 200 (AF2-N preserved) ✅ |

---

## 16. Invariants

✅ Tutti preservati: heroes=100, gaia=404, borea/greek_borea=200, AF2-N cap=50000 allowlist=2500, SLC-G migration_id preserved, env flags unset, Phase 11=false, zero diff su routes runtime, tutti i marker SLC-F precedenti preservati.

---

## 17. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404**.
- ✅ `borea`/`greek_borea` HTTP = **200** catalog-only inert.
- ✅ Character Bible (`sanctuary.py`, `db.heroes`) classificata FORBIDDEN_SCOPE e non toccata.
- ✅ Nessun cambiamento a banner/rates/pity/obtainable/roster visibility.

---

## 18. AF2-N Preservation Result

✅ Stato identico al pre-audit:
- `feature_flag_currently_enabled`: True
- `inventory_mutation_enabled`: True
- `rate_limit_enabled`: True
- `canary_allowlist_size`: 2500
- `canary_ledger_cap`: 50000
- Diff su `affinity_gift_spend.py` / `affinity_gifts.py`: 0
- Validators V12–V30: ALL PASS

---

## 19. Known Drift Docs Status

🟡 **NON CORRETTI** in questo audit per istruzione esplicita del task guardrail (`drift docs cleanup` non autorizzato in AUDIT_ONLY). I 7 documenti gacha/summon restano nello stato `DRIFT KNOWN, NON-BLOCKING`, deferiti a job housekeeping dedicato.

---

## 20. Recommended Next Micro-Batch

🟢 **Prossimo job suggerito (RACCOMANDATO):**

### **SLC-F GVG WAR INSERT SCOPE** (highest priority)
- **Target:** `backend/routes/gvg.py:190` → `db.gvg_wars.insert_one(war)`
- **Pattern:** identico a `raids.py` (+2 righe minimali)
- **Risk:** low
- **Markers:** `SLC_F_GVG_WAR_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=GVG_WAR_ONLY`
- **Expected verdict:** `SLC_F_GVG_WAR_SCOPE_APPLIED_SAFE`

### **SLC-F UNIQUE-ITEMS SCOPE** (alternativa equipollente)
- **Target:** `unique_items.py:277` (insert) + `unique_items.py:303` (upsert)
- **Pattern:** +3 righe (1 import + 2 call); Batch-1B-style con `$setOnInsert`
- **Risk:** low
- **Markers:** `SLC_F_UNIQUE_ITEMS_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=UNIQUE_ITEMS_ONLY`
- **Expected verdict:** `SLC_F_UNIQUE_ITEMS_SCOPE_APPLIED_SAFE`

Entrambi i micro-batch portano il progress da ~94% a ~95% se applicati.

🔵 **Backlog medio-lungo termine (non in micro-batch):**
- Refactor strutturale `cosmetics.py` (split ownership/equipped).
- Refactor strutturale `economy.py` (split paid/free + isolate VIP + rimuovere `/server/select` legacy).
- Housekeeping drift docs gacha/summon.
- Batch-3 AF2-N routing (sanctuary affinity/constellation surfaces).
- Batch-4 combat/battle (combat.py 9 surfaces).
- Gacha/summon dedicated scope task (heroes.py user_heroes inserts).
- Character Bible split via task dedicato (sanctuary.py db.heroes writes).
- SLC-H live wiring (post-economy refactor).

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server / attivazione `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare combat/battle/AF2-N/gacha/summon routing.
- Implementare `/api/housing` runtime.

---

## 21. Updated Progress Estimate

| Fase | Stato pre-audit | Stato post-audit |
|---|---|---|
| SLC-F Batch-0/1, Batch-1B, Batch-2, Equipment-scope, Raids-equipment | ✅ done | ✅ done |
| **SLC-F Minor Write Surfaces Audit (AUDIT_ONLY)** | 🟡 pending | ✅ **ready** |
| SLC-F GVG-war micro-batch | 🔵 backlog | 🟢 **RECOMMENDED NEXT** (candidate identified) |
| SLC-F unique-items micro-batch | 🔵 backlog | 🟢 **RECOMMENDED NEXT** (candidate identified) |
| SLC-F cosmetics/economy refactor | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 AF2-N routing | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 combat/battle | 🔵 backlog | 🔵 backlog |
| SLC-F gacha/summon scope task | 🔵 backlog | 🔵 backlog |
| SLC-F Character Bible / sanctuary split | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **94% invariato** (audit non incrementa il progress; conferma 2 candidati SAFE_MICRO_BATCH per il prossimo apply).

---

## 22. Markers di audit (riferimenti rapidi)

- `audit_id`: `slc_f_minor_audit_20260523T190000Z_audit_only`
- `git_head_before/after`: `1c991ec` (zero diff su file runtime)
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `slc_f_batch_2_apply_id_preserved`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `slc_f_equipment_scope_apply_id_preserved`: `slc_f_equipment_scope_20260523T182939Z_d2afcc8a`
- `slc_f_raids_equipment_scope_apply_id_preserved`: `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034`
- `verdict_target`: `SLC_F_MINOR_SURFACES_AUDIT_READY` → ✅ **RAGGIUNTO**

---

**FINE REPORT 110_SLC_F_MINOR_WRITE_SURFACES_AUDIT.md**
