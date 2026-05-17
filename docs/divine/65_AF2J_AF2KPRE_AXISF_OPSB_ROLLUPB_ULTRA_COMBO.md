# 65. ULTRA-COMBO V7 — AF2-J · AF2-K-PRE · AXIS-F · OPS-B · SAFETY-ROLLUP-B (+ AF2-L-PRE)

> **Stato:** ✅ CHIUSO (PASS) — Suite **77/77 PASS**, combo validator
> **90/90 PASS**, baseline diff PASS auto-detect v6.
>
> **Categoria:** *Accelerated safe layering after baseline v6*
>
> **Anchor baseline:** `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (clean, no v7)

---

## 1. Obiettivo

Accelerare il più possibile dopo baseline v6 combinando:
1. **AF2-J** — contract concreto auth + rate-limit + idempotency middleware bound al disabled POST.
2. **AF2-K-PRE** — design-only contract per il futuro `gift_transaction_ledger` (idempotency / replay / audit-trail).
3. **AXIS-F** — espansione read-only delle route gifts: `by-faction/greek`, `by-faction/tides` (deferred 404), `by-element/dark`, `by-element/darkness → dark` alias.
4. **OPS-B** — persistenza `start-expo.sh` sotto `/app/ops/` + restore helper one-shot.
5. **SAFETY-ROLLUP-B** — refresh rollup con axis GO + runtime NO_GO.
6. (Optional) **AF2-L-PRE** — plan-only per load test + rollback rehearsal pre-flag-flip.

---

## 2. AF2-J summary

- Contract: `/app/data/design/affinity/affinity_gift_spend_auth_ratelimit_contract_v1.json`
- Audit: `/app/backend/scripts/audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py` → **45/45 PASS**
- Endpoint POST `/api/affinity/gift-spend` resta **HTTP 423 / no-write**.
- `auth_required: true`, `auth_enforcement_status: deferred_until_runtime_flag`.
- Rate-limit: 30/min user, 240/h user, 60/min ip, burst_window 60s, max 6.
- Idempotency: window 24h, key 8–128, replay protection (409 duplicate).
- Borea aliases rifiutati con **404** prima della shape validation.
- 0 DB write token in `affinity_gift_spend.py` (verificati 6 pattern), 0 driver imports (3 pattern).
- 0 middleware ATTACHED today (wiring deferred a AF2-K runtime).

---

## 3. AF2-K-PRE summary

- Contract: `/app/data/design/affinity/affinity_gift_spend_idempotency_ledger_contract_v1.json`
- Validator: `/app/backend/scripts/validate_affinity_gift_spend_idempotency_ledger_contract.py` → **49/49 PASS**
- `future_collection_name: gift_transaction_ledger`, `future_migration_id: AF2-K-MIG-001`.
- Idempotency scope: (user_id, gift_id, hero_id, idempotency_key); finestra 24h.
- 4 index drafts; 1 **partial unique** su `(user_id, idempotency_key, created_at_utc)`.
- 7 status enumerati: `pending / committed / rolled_back / duplicate_replay / rejected_borea_alias / rejected_validation / rejected_rate_limit / rejected_auth`.
- Duplicate replay → **409** con payload originale, no mutation.
- 7 abuse cases documentati.
- **Nessuna collection creata**, **nessuna migration shipped** (`MIG_DIR` clean).
- Rollback plan in 6 step.

---

## 4. AXIS-F summary

- Route patch: `/app/backend/routes/affinity_gifts.py`
  - aggiunto `_CANONICAL_ELEMENTS`, `_ELEMENT_ALIASES = {'darkness': 'dark'}`, `_DEFERRED_FACTIONS = {'tides'}`.
  - aggiunti `greek_borea` a `_FORBIDDEN_ALIASES`.
  - `by-faction/{id}`: tides → **404 deferred_not_live**; Borea aliases → 404 forbidden.
  - nuova `by-element/{id}`: `dark` → 200 (alias_applied=false), `darkness` → 200 (alias_applied=true, canonical=dark), `tides` → **404 axis_type_mismatch**, factions canoniche (greek/egyptian/...) → **404 axis_type_mismatch**, Borea aliases → 404 forbidden.
- Audit: `/app/backend/scripts/audit_affinity_gifts_axis_readonly_routes.py` → **32/32 PASS**.
- Mutazioni POST/PUT/PATCH/DELETE su queste rotte → **405** (4 mutation × 2 endpoint = 8 check tutti PASS).

---

## 5. OPS-B summary

- Persistent wrapper: `/app/ops/start-expo.sh` (508 byte, executable, allineato OPS-A: no `CI=1`, HMR preservato).
- Restore helper: `/app/ops/restore_start_expo_wrapper.sh` (executable, copia in `/usr/local/bin`, `chmod +x`, `supervisorctl reread/update/restart expo`, smoke curl 3000).
- Audit: `/app/backend/scripts/audit_ops_start_expo_persistence.py` → **19/19 PASS**.
- Confermato: `/usr/local/bin/start-expo.sh` ricreato dall'helper, supervisor `expo RUNNING`, frontend `localhost:3000 → HTTP 200`.
- Supervisor `[program:expo]` block riferisce correttamente il wrapper.

---

## 6. SAFETY-ROLLUP-B summary

- Report: `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v2.json`
- Validator: `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v2.py` → **30/30 PASS**.
- `axis_layer_activation_ready: true`, `overall_runtime_activation_ready: false`.
- Decisione: `go_no_go_decision: NO_GO_RUNTIME`, `axis_layer_decision: GO_AXIS`.
- Subsystem status: axis_layer GO · auth_layer NO_GO · idempotency_layer NO_GO · rate_limit_layer NO_GO · db_layer NO_GO · battle_runtime_layer NO_GO · borea_layer GO · ops_layer GO.
- 10 `runtime_no_go_reasons`, 12 invariants_currently_holding, 5 `recommended_unblock_sequence`.

---

## 7. AF2-L-PRE summary (optional, eseguito)

- Plan: `/app/data/design/affinity/affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1.json`
- Validator: `/app/backend/scripts/validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py` → **26/26 PASS**.
- Load test targets: 200 VU, 15 min, RPS 60 (ceiling 80), 10% replay, 5% Borea injection.
- Acceptance thresholds: p95 ≤ 250 ms, 5xx ≤ 0.1%, Borea 404 100%, idem 409 ≥ 99.5%, duplicate charge 0%.
- Rollback rehearsal `AF2-L-REHEARSAL-001`: flag flip ≤ 5s, 6 step, operator sign-off richiesto.
- `load_test_executed_in_this_task: false`, `rollback_rehearsal_executed_in_this_task: false`.

---

## 8. Borea safety

| Check | Esito |
|---|---|
| `/api/heroes`: borea / greek_borea / primordial_gaia in lista | ❌ assenti |
| `/api/affinity/gifts/by-faction/borea` | ✅ 404 |
| `/api/affinity/gifts/by-faction/greek_borea` | ✅ 404 |
| `/api/affinity/gifts/by-faction/primordial_gaia` | ✅ 404 |
| `POST /api/affinity/gift-spend` con qualunque alias Borea | ✅ 404 |
| Marchio Boreale leak su non-Borea 6★ | ✅ 0 |

---

## 9. Validator results (individuale)

| Task | Script | Esito |
|---|---|---|
| AF2-J | `audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py` | ✅ 45/45 |
| AF2-K-PRE | `validate_affinity_gift_spend_idempotency_ledger_contract.py` | ✅ 49/49 |
| AXIS-F | `audit_affinity_gifts_axis_readonly_routes.py` | ✅ 32/32 |
| OPS-B | `audit_ops_start_expo_persistence.py` | ✅ 19/19 |
| SAFETY-ROLLUP-B | `validate_collection_affinity_runtime_activation_rollup_v2.py` | ✅ 30/30 |
| AF2-L-PRE | `validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py` | ✅ 26/26 |
| ULTRA-COMBO-V7 | `validate_af2j_af2kpre_axisf_opsb_rollupb_combo.py` | ✅ **90/90** |

---

## 10. Suite / baseline results

```
run_hero_skill_kit_validator_suite.py --include-baseline-diff
Overall: PASS  (pass=77, fail=0, miss=0)
```

JSON: `/tmp/ultra_combo_v7_suite.json`. Baseline diff PASS con auto-detection v6.

---

## 11. API smoke

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` count | 100 | ✅ 100 |
| `/api/heroes` borea/greek_borea/primordial_gaia | assenti | ✅ |
| `GET /api/affinity/gifts` | 200 | ✅ 200 |
| `GET /api/affinity/gifts/by-faction/greek` | 200 | ✅ 200 |
| `GET /api/affinity/gifts/by-faction/egyptian` | 200 | ✅ 200 |
| `GET /api/affinity/gifts/by-faction/tides` | 404 deferred_not_live | ✅ 404 |
| `GET /api/affinity/gifts/by-faction/borea` | 404 forbidden | ✅ 404 |
| `GET /api/affinity/gifts/by-faction/greek_borea` | 404 forbidden | ✅ 404 |
| `GET /api/affinity/gifts/by-element/dark` | 200 alias_applied=false | ✅ |
| `GET /api/affinity/gifts/by-element/darkness` | 200 alias_applied=true, canonical=dark | ✅ |
| `GET /api/affinity/gifts/by-element/light` | 200 | ✅ |
| `GET /api/affinity/gifts/by-element/fire` | 200 | ✅ |
| `GET /api/affinity/gifts/by-element/tides` | 404 axis_type_mismatch | ✅ 404 |
| `POST /api/affinity/gift-spend` empty | 423 | ✅ 423 |
| `POST /api/affinity/gift-spend` valid greek_zeus | 423 no-write | ✅ 423 |
| `POST /api/affinity/gift-spend` borea / greek_borea / primordial_gaia | 404 | ✅ 404 / 404 / 404 |
| Mutation POST/PUT/PATCH/DELETE su routes read-only | 405 | ✅ 405 (8/8) |

---

## 12. UI safety

`grep -rnE "gift_spend|gift-spend|GiftSpendButton|RuntimeToggle|gift_transaction_ledger|AFFINITY_GIFT_RUNTIME_ENABLED|IdempotencyKey"` in `/app/frontend/app/*.tsx` → **0 hit**.

Nessun bottone di spend, nessun toggle runtime, nessuna mutation fetch, nessuna reference all'idempotency ledger lato UI.

---

## 13. Runtime / DB / gacha / roster / catalog safety

- `battle_engine.py`, `battle_core.py`, `combat.tsx` → 0 reference a (6 token chiave verificati): `affinity_gift_spend_auth_ratelimit_contract_v1`, `affinity_gift_spend_idempotency_ledger_contract_v1`, `collection_affinity_runtime_activation_readiness_rollup_v2`, `affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1`, `restore_start_expo_wrapper`, `AFFINITY_GIFT_RUNTIME_ENABLED`.
- 0 DB write nel codice route gift-spend (verificati 6 pattern + 3 driver imports).
- Roster / heroes_master / heroes_kits / Character Bible / gacha / skill kit catalog / DW catalog / status catalog / final_numbers / assets / baseline v6 / baseline v5 → **non toccati**.
- `feature_flag_currently_enabled: false` confermato sull'envelope live.
- Baseline diff central PASS con auto-detection v6.

---

## 14. Warning / discrepanze

1. ⚠️ `/usr/local/bin/start-expo.sh` era sparito di nuovo all'inizio del task (ricorrenza nota). Restore eseguito via `bash /app/ops/restore_start_expo_wrapper.sh` con successo (expo RUNNING, frontend HTTP 200).
2. ⚠️ Nessun warning aggiuntivo. Tutti i validator e regression test PASS.

---

## 15. Final recommendation

✅ **ACCETTARE**. Tutte le condizioni di accettazione richieste sono soddisfatte:
- gift-spend disabled / no-write ✅
- by-faction / by-element GET-only / read-only ✅
- idempotency ledger design-only (no DB write, no migration) ✅
- start-expo wrapper persistito sotto `/app/ops/` ✅
- rollup dice axis GO ma runtime NO_GO ✅
- suite **77/77 PASS** ✅
- suite `--include-baseline-diff` PASS sotto v6 ✅
- `/api/heroes = 100` ✅
- Borea hidden ✅
- zero DB / gacha / roster / catalog / baseline mutation ✅
- zero battle_engine / combat mutation ✅
- UI safety PASS ✅

---

## 16. Suggested next tasks

- 🟡 **AF2-K** (runtime) — ship migration `AF2-K-MIG-001` per `gift_transaction_ledger` dietro flag separato.
- 🟡 **AF2-L** (runtime) — eseguire load test + rollback rehearsal seguendo il plan `AF2-L-REHEARSAL-001`.
- 🟢 **AF2-M** — operator sign-off pre flag flip.
- 🟢 **AF2-N** — flip `AFFINITY_GIFT_RUNTIME_ENABLED → true_explicit_affinity_gift_runtime_on` sotto controlled rollout.
- 🟢 **STACK-G** — connettere `global_modifier_cap_resolver` al battle (gated, no-write).
- 🟢 **OPS-C** — aggiungere un cron / hook per auto-restore del wrapper se sparisce.
- 🟢 **AXIS-G** — espandere read-only routes con `by-element/{e}/by-faction/{f}` combinato.

---

## File creati
- `/app/data/design/affinity/affinity_gift_spend_auth_ratelimit_contract_v1.json`
- `/app/data/design/affinity/affinity_gift_spend_idempotency_ledger_contract_v1.json`
- `/app/data/design/affinity/affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v2.json`
- `/app/ops/start-expo.sh`
- `/app/ops/restore_start_expo_wrapper.sh`
- `/app/backend/scripts/audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py`
- `/app/backend/scripts/validate_affinity_gift_spend_idempotency_ledger_contract.py`
- `/app/backend/scripts/audit_affinity_gifts_axis_readonly_routes.py`
- `/app/backend/scripts/audit_ops_start_expo_persistence.py`
- `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v2.py`
- `/app/backend/scripts/validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py`
- `/app/backend/scripts/validate_af2j_af2kpre_axisf_opsb_rollupb_combo.py`
- `/app/docs/divine/65_AF2J_AF2KPRE_AXISF_OPSB_ROLLUPB_ULTRA_COMBO.md` (questo doc)

## File modificati
- `/app/backend/routes/affinity_gifts.py` — aggiunti `_CANONICAL_ELEMENTS`, `_ELEMENT_ALIASES`, `_DEFERRED_FACTIONS`, `greek_borea` in `_FORBIDDEN_ALIASES`; nuova rotta `by-element/{element_id}` + tides 404 deferred su `by-faction/{id}`.
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunti 7 entry OPTIONAL (AF2-J, AF2-K-PRE, AXIS-F, OPS-B, SAFETY-ROLLUP-B, AF2-L-PRE, ULTRA-COMBO-V7).
- `/usr/local/bin/start-expo.sh` — ripristinato dall'helper `restore_start_expo_wrapper.sh`.
