# ULTRA-COMBO V19 — STAGE3 EXTENDED MONITORING + LOCUST REAL LOW-IMPACT + PUBLIC UI PREVIEW READ-ONLY + BROAD-ROLLOUT READINESS PLAN-ONLY + SAFETY-ROLLUP-N

**Project**: Divine RPG / Divine Waifus
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`
**Stato**: ✅ COMPLETATO — Stage3 stabile, Locust reale OK, UI preview read-only implementata, broad-rollout PLAN-ONLY. Suite 112/112 PASS.

---

## 1. File creati

### Scripts (`/app/backend/scripts/`)
- `validate_af2n_v19_preflight.py`
- `run_af2n_stage3_extended_monitoring_v19.py`
- `validate_af2n_stage3_extended_monitoring_v19.py`
- `run_af2n_stage3_locust_low_impact.py`
- `validate_af2n_stage3_locust_low_impact_result.py`
- `audit_affinity_gifts_public_preview_implementation.py`
- `validate_af2n_broad_rollout_readiness_plan.py`
- `run_af2n_v19_rollback_readiness.py`
- `validate_af2n_v19_rollback_readiness.py`
- `validate_collection_affinity_runtime_activation_rollup_v14.py`
- `validate_ultra_combo_v19_stage3_locust_ui_broadprep.py`

### Locust
- `/app/loadtests/af2n_stage3_locustfile.py` (read-only + reject paths + idempotent replay; ZERO fresh spend tasks)

### Design / safety JSON
- `/app/data/design/affinity/af2n_v19_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_stage3_extended_monitoring_v19_result.json`
- `/app/data/design/affinity/af2n_stage3_locust_low_impact_result_v1.json`
- `/app/data/design/affinity/af2n_broad_rollout_readiness_plan_v1.json`
- `/app/data/design/affinity/af2n_v19_rollback_readiness_result_v1.json`
- `/app/data/design/ui/affinity_gifts_public_preview_implementation_result_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v14.json`

### Frontend UI (read-only)
- `/app/frontend/app/affinity-gifts-preview.tsx` — route `/affinity-gifts-preview` SOLO GET su `canary-status` sanitizzato

### Reports / docs
- `/app/backend/reports/suite_v19.json` (overall PASS, 112/112)
- `/app/backend/reports/ultra_combo_v19_validator_summary_v1.json`
- `/app/docs/divine/79_ULTRA_COMBO_V19_STAGE3_LOCUST_UI_BROADPREP.md` (questo)

---

## 2. File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (registrati 8 nuovi validator V19 + nuovo bucket `SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW` per V18 audit/composite quando il file preview è presente)

**File esplicitamente NON modificati (invariante hard)**:
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`
- `/app/frontend/app/combat.tsx`
- `/app/backend/synergy_system.py`
- `/app/backend/game_systems.py`
- `/app/backend/routes/affinity_gift_spend.py` (zero modifiche in V19)
- `/etc/supervisor/conf.d/backend.conf` (zero modifiche in V19; runtime invariato)

---

## 3. Preflight V19

**Status**: PASS. Tutti i gates verde:
- API health 200, /api/heroes=100, no-borea
- canary_flag_on, inv_writes_flag_on
- stage3_allowlist≥200, cap≥2500, ledger entro cap
- battle_runtime_attached=false, applied_to_combat=false, buffs=false
- borea 404, non-allow 423
- battle files unchanged
- ugi/uas presenti, no negative inventory, V18_STAGE3 seed 100
- rollback scripts present (Stage2 + Stage3 + Stage1)
- V18 composite PASS (oppure UI preview implementata → V18 superseded)
- baseline v6 diff PASS
- **locust_binary_present** ✅
- ui_safety_no_spend_in_combat

---

## 4. Stage3 Extended Monitoring (V19)

**Status**: PASS. **310 campioni** (target ≥300), **0 trigger**.
- 130 health 200, 50 canary-status 200, 30 /api/heroes=100
- 30 Borea POST: tutti 404 (0 bad)
- 30 non-allowlist: tutti 423 (0 bad)
- 30 idempotent replay su tx storiche: tutti 200 `idempotent_replay` con inventory_unchanged + affinity_unchanged
- 10 fresh Stage3 spend (`stage3_qa_010..019`): inventory −1 / affinity +1 esatti
- 0 HTTP 5xx, 0 negative inventory, 0 buffs, 0 battle wiring
- inv_mut_delta = aff_mut_delta = 10

---

## 5. Locust Real Low-Impact (V19)

**Status**: PASS. Locust **installato system-wide** (`/usr/local/bin/locust` v2.44.0).
- Comando: `locust -f /app/loadtests/af2n_stage3_locustfile.py --headless -u 8 -r 4 -t 20s --host http://127.0.0.1:8001 --only-summary --csv /tmp/v19_locust_csv --csv-full-history`
- Exit code: **0**
- Scenari: solo GET (health, canary-status, heroes, gifts catalog) + POST non-allowlist (expect 423) + POST Borea (expect 404) + replay idempotente (expect 200 `idempotent_replay`). **ZERO fresh spend** in Locust.
- Snapshot DB pre/post Locust + Python fallback:
  - `delta.ledger_total` = **0** (replay idempotente → nessuna nuova riga)
  - `delta.borea_hero` = 0, `delta.buffs` = 0, `delta.battle_wiring` = 0, `delta.negative_inventory` = 0
- Python fallback concorrente (ThreadPool 10 worker, 1150 richieste): 0 HTTP 5xx, 0 borea_bad, 0 non_allowlist_bad, 0 replay_bad.

**ZERO uncontrolled ledger growth da load test reale**.

---

## 6. Public UI Preview READ-ONLY

**Status**: PASS — **implementata e auditata**.

File: `/app/frontend/app/affinity-gifts-preview.tsx` (route auto-registrata da expo-router come `/affinity-gifts-preview`).

Caratteristiche:
- Solo `GET /api/affinity/gift-spend/canary-status` (sanitizzato: niente allowlist size esposta, niente user_id, niente ledger counts; mostra solo il count di alias bloccati).
- Etichetta esplicita "Design only — Spend disabled".
- Pull-to-refresh, ActivityIndicator, error state.
- SafeAreaView + Stack.Screen (expo-router header).

Audit `audit_affinity_gifts_public_preview_implementation.py` PASS (13/13):
- ✅ Solo `/api/affinity/gift-spend/canary-status` come endpoint
- ✅ Nessun `method: 'POST/PUT/PATCH/DELETE'`
- ✅ Nessun bottone Spend/Claim/Give
- ✅ Nessun alias Borea visibile
- ✅ JSON implementation_result valido
- ✅ `combat.tsx` invariato
- ✅ Battle backend files invariati

**Nessun link in menu/Tabs aggiunto** (no public discoverability) — il route esiste ma non è promosso pubblicamente.

---

## 7. Broad-Rollout Readiness PLAN-ONLY

**Status**: PASS (`af2n_broad_rollout_readiness_plan_v1.json`).
- `explicit_status`: **`READY_NOT_APPLIED_DESIGN_ONLY`**
- `design_only: true`, `runtime_attached: false`, `applied: false`
- `broad_rollout_authorized: false`, `public_spend_enabled: false`, `battle_wiring: false`
- **15 gate** richiesti prima di qualsiasi autorizzazione (Stage3 extended monitoring clean, Locust clean, UI preview audit, rollback drills, rate-limit, abuse monitoring, Borea safety, economy caps, support plan, 5 signoffs v5 + autorizzazione utente esplicita v5)
- **Staged rollout**: stage4_internal_beta (700 users, cap 5k) → public_beta_1pct (cap 25k) → 5pct (cap 100k) → 10pct (cap 200k), con `abort_thresholds` esplicite per ogni stage
- **Rollback thresholds**: rollback immediato per 5xx critico, non-allow success>0, borea_not_404>0, negative_inventory>0, inv/aff mismatch, battle file mutation, public spend button detection
- Safety invariants documentate, support plan documentato

**Plan NON applicato. Plan NON apply-able dalla suite runner.**

---

## 8. Rollback Readiness V19

**Status**: PASS.
- 7 rollback script presenti (Stage1 1pct, inventory wiring, inventory wiring retry, Stage1 QA seed, **Stage2**, **Stage3**, ops shell)
- Directory `/app/ops/backups/` scrivibile
- Dry-run Stage3 + Stage2 rollback OK
- **UI preview rollback strategy** documentata: `rm /app/frontend/app/affinity-gifts-preview.tsx` + rebuild
- `ui_preview_present`: true

---

## 9. Safety Rollup N

**Status**: PASS (`collection_affinity_runtime_activation_readiness_rollup_v14.json`).
- `supersedes`: rollup_v13
- `runtime_state`: **`stage3_qa_active_no_broad_rollout`**
- `stage3_state`: APPLIED
- `public_ui_preview_state`: **`READONLY_IMPLEMENTED`**
- `broad_rollout_plan_state`: `READY_NOT_APPLIED_DESIGN_ONLY`
- `broad_rollout_authorized`: false
- `public_spend_ui`: false
- `battle_wiring_live`: false
- `buffs_enabled`: false
- `Borea_hidden`: true
- `inventory_live_scope`: **`stage3_allowlist_only`**
- `rollback_ready`: true
- `canary_allowlist_size`: 200, `ledger_cap`: 2500, `ledger_total_rows`: 64
- `stage3_extended_monitoring.overall_status`: PASS (310 samples, 0 5xx)
- `locust_low_impact_status.overall`: PASS (delta_ledger=0, locust_exit_code=0)
- `public_ui_preview_readonly.no_public_spend_ui`: true
- `next_decision`: **`stage4_internal_beta_prep`**

---

## 10. Borea Safety

- `/api/heroes` count = **100**, nessun id Borea/greek_borea/primordial_gaia.
- POST `/api/affinity/gift-spend` con hero_id Borea → **HTTP 404** (verificato 30 volte in extended monitoring + ulteriori volte in Locust + python fallback).
- Ledger query `hero_id IN [borea, greek_borea, primordial_gaia]` → **0 righe**.
- Preview UI: nessuna stringa `borea` / `greek_borea` / `primordial_gaia` nel file.

---

## 11. Validator Results

| Task | Status |
|---|---|
| V19-PREFLIGHT | ✅ PASS |
| AF2-N-STAGE3-EXTENDED-MONITORING-V19 | ✅ PASS (310 samples, 0 trigger) |
| AF2-L-LOCUST-LOW-IMPACT-V19 | ✅ PASS (locust exit 0, delta_ledger=0) |
| AF2-N-PUBLIC-UI-PREVIEW-IMPLEMENTATION | ✅ PASS (13/13 audit) |
| AF2-N-BROAD-ROLLOUT-READINESS-PLAN | ✅ PASS (PLAN-ONLY) |
| V19-ROLLBACK-READINESS | ✅ PASS |
| SAFETY-ROLLUP-N | ✅ PASS |
| ULTRA-COMBO-V19 composite (41 checks) | ✅ PASS |

---

## 12. Suite / Baseline

- `python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff --json-out /app/backend/reports/suite_v19.json`
- **Overall: PASS** — pass=112, fail=0, miss=0
- Validator SUPERSEDED auto-marked (5 frozenset): `SUPERSEDED_AFTER_AF2N`, `SUPERSEDED_AFTER_INV_WRITES`, `SUPERSEDED_AFTER_STAGE2`, `SUPERSEDED_AFTER_STAGE3`, nuovo **`SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW`** per V18 audit + V18 composite quando il file preview esiste.
- **RM1.32-PRE baseline diff**: PASS (`hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` invariato).

---

## 13. API Smoke (post-V19)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | ✅ |
| `GET /api/heroes` | 100, no Borea | ✅ |
| `GET /api/affinity/gift-spend/canary-status` | 200, size=200, cap=2500 | ✅ size=200 cap=2500 ledger=64 |
| `POST gift-spend` Borea | 404 | ✅ 404 |
| `POST gift-spend` non-allowlist | 423 | ✅ 423 |
| `POST gift-spend` Stage3 user (`stage3_qa_080`) | 200 `applied_inventory_live` | ✅ inv 10→9, aff 0→1 |
| `POST gift-spend` idempotent replay | 200 `idempotent_replay`, no state change | ✅ (verificato anche in Locust) |
| `GET /api/affinity/gifts` | catalog 200 | ✅ |

---

## 14. UI Safety

- ❌ Nessun bottone public spend.
- ❌ Nessun bottone claim/give.
- ❌ Nessun runtime toggle in UI.
- ❌ Nessun battle wiring UI.
- ❌ Nessuna rivelazione Borea (zero stringhe alias nella nuova preview).
- ✅ Public UI preview implementata **READ-ONLY** con etichetta `Design only — Spend disabled`.
- ✅ `combat.tsx` invariato (git diff stat vuoto).
- ✅ Audit V19 PASS 13/13.

---

## 15. Runtime / DB / Gacha / Roster / Catalog Safety

- **Runtime**: feature flag + inventory writes attivi su allowlist 200 Stage3. `applied_to_combat=false`, `battle_runtime_attached=false`, `buffs_enabled=false`. Stato invariato rispetto a V18 (zero supervisor.conf changes in V19).
- **DB**:
  - `gift_transaction_ledger`: 64 righe totali, tutte `canary=True`, ben entro cap 2500. `inventory_mutated` == `affinity_points_mutated`. 0 buffs, 0 battle wiring, 0 Borea heroes.
  - `user_gift_inventory`: 0 docs `quantity<0`.
  - `user_affinity_state`: incrementi esatti per ogni spend.
- **Gacha / Roster / Character Bible / asset / skill catalogs / final_numbers**: NESSUNA modifica.

---

## 16. Warnings

- **Locust install**: reinstallato come system-wide (`pip3 install locust` → `/usr/local/bin/locust` v2.44.0). L'install user-site di V18 era stato perso al riavvio del backend. Ora persiste tra restart. Non aggiunto a `requirements.txt` (file controllato dall'ambiente) ma documentato per future ops.
- **V18 audit + V18 composite** ora marcati `SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW` perché il loro contract `frontend/ source unchanged` è naturalmente invalidato dall'aggiunta legittima del file preview UI in V19. Comportamento documentato.
- **k6** non installato (richiede sudo); rinviato a task gated separato. Istruzioni esatte in `af2n_v18_k6_locust_result_v1.json`.

---

## 17. Final Recommendation

**Recommendation**: **STAGE4_INTERNAL_BETA_PREP (PLAN-ONLY)**.

V19 ha consolidato Stage3 con successo:
- Stage3 extended monitoring 310 campioni PASS con 0 trigger
- Locust reale low-impact (8 vus, 20s) OK con delta_ledger=0
- Public UI preview READ-ONLY pubblicamente leggibile e completamente safe (no spend, no Borea, no mutation)
- Broad-rollout PLAN documentato esaustivamente come `READY_NOT_APPLIED_DESIGN_ONLY` con 15 gate, 4 stage, 7 rollback threshold
- Rollback readiness completa (7 script + UI preview rollback strategy)
- Tutti gli invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle/combat files NON modificati, no public spend UI, no broad rollout, no battle wiring, no buffs

Prossimo passo **prudente**: pianificare Stage4 internal beta (PLAN-ONLY, no apply) seguendo il `af2n_broad_rollout_readiness_plan_v1.json`. Eseguire rollback drills + signoffs prima di considerare qualsiasi autorizzazione esplicita.

**Broad rollout, public spend UI, STACK-G full wiring restano gated tasks separati e NON autorizzati.**

---

## 18. Suggested Next Tasks

- **P1** `AF2-N-STAGE4-INTERNAL-BETA-PREP` — PLAN-ONLY: definire allowlist target (≈700 users), cap target (≈5000), seed strategy, gates, abort thresholds. NESSUN apply.
- **P1** `AF2-N-ROLLBACK-DRILLS-V19` — esecuzione drills `--execute` su backup Stage3 in ambiente isolato per validare end-to-end il flow di rollback.
- **P1** `AF2-N-STAGE3-OBSERVATION-LONG-WINDOW` — 24-72h di osservazione continuata con scheduled cron sui validator V19.
- **P2** `AF2-L-LOCUST-RAMP-PLAN` — definire scaling controllato di Locust (20 vus → 50 vus → 100 vus) con caps espliciti.
- **P2** `AF2-N-PUBLIC-PREVIEW-MENU-LINK` — task gated separato per aggiungere link in menu/Tabs alla preview (dopo autorizzazione esplicita).
- **P2** `AF2-L-K6-INSTALL-GATED` — install k6 via tarball (richiede sudo): task gated separato con rollback.
- **P2** `OPS-E-RATE-LIMIT-VERIFICATION` — verifica rate-limiting in vista futuro broad rollout (per-user/min, per-ip/min).
- **P3** `AF2-N-PUBLIC-PREVIEW-UI-ENHANCEMENTS` — copy education, accessibility, i18n.
- **P3** `STACK-G-WIRING-FULL` — collegamento `affinity_state` → `battle_engine.py`/`combat.tsx`. **Strettamente deferred**.

---

## Acceptance V19 — Checklist Finale

- [x] no broad rollout
- [x] no public spend UI
- [x] Stage3 resta gated (200 users, cap 2500)
- [x] inventory/affinity mutation esatta e idempotente
- [x] no battle wiring
- [x] /api/heroes = 100
- [x] Borea hidden/404
- [x] no unauthorized spend success
- [x] 0 HTTP 5xx
- [x] rollback readiness PASS (7 script + UI preview rollback)
- [x] suite/baseline PASS (112/112, RM1.32-PRE PASS)
- [x] UI safety PASS (audit 13/13)
- [x] no battle/gacha/roster/catalog mutation

**ULTRA-COMBO V19 — COMPLETATO**
