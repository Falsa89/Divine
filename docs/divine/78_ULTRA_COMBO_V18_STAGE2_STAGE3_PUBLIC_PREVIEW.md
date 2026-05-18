# ULTRA-COMBO V18 — STAGE2 EXTENDED MONITORING + STAGE3 QA EXPANSION (APPLIED-GATED) + PUBLIC UI PREVIEW READINESS (PLAN-ONLY) + K6/LOCUST REAL ATTEMPT (LOCUST INSTALLED) + SAFETY-ROLLUP-M

**Project**: Divine RPG / Divine Waifus
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`
**Stato**: ✅ COMPLETATO — Stage3 APPLIED (allowlist 100→200, cap 1000→2500) — Suite 106/106 PASS

---

## 1. File creati

### Scripts (`/app/backend/scripts/`)
- `validate_af2n_v18_preflight.py`
- `run_af2n_stage2_extended_monitoring_v18.py`
- `validate_af2n_stage2_extended_monitoring_v18.py`
- `apply_af2n_stage3_qa_expansion.py`
- `rollback_af2n_stage3_qa_expansion.py`
- `validate_af2n_stage3_qa_expansion_apply_result.py`
- `run_af2n_stage3_monitoring_v18.py`
- `validate_af2n_stage3_monitoring_v18.py`
- `audit_affinity_gifts_public_preview_safety.py`
- `run_af2n_v18_k6_locust.py`
- `validate_af2n_v18_k6_locust_result.py`
- `run_af2n_v18_rollback_readiness.py`
- `validate_af2n_v18_rollback_readiness.py`
- `validate_collection_affinity_runtime_activation_rollup_v13.py`
- `validate_ultra_combo_v18_stage2_stage3_publicpreview.py`

### Design / safety JSON
- `/app/data/design/affinity/af2n_v18_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_stage2_extended_monitoring_v18_result.json`
- `/app/data/design/affinity/af2n_stage3_qa_expansion_plan_v1.json`
- `/app/data/design/affinity/af2n_stage3_qa_expansion_apply_result_v1.json`
- `/app/data/design/affinity/af2n_stage3_monitoring_v18_result.json`
- `/app/data/design/affinity/af2n_v18_k6_locust_result_v1.json`
- `/app/data/design/affinity/af2n_v18_rollback_readiness_result_v1.json`
- `/app/data/design/ui/affinity_gifts_public_preview_readiness_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v13.json`

### Reports / docs
- `/app/backend/reports/suite_v18.json` (overall PASS, 106/106)
- `/app/backend/reports/ultra_combo_v18_validator_summary_v1.json`
- `/app/docs/divine/78_ULTRA_COMBO_V18_STAGE2_STAGE3_PUBLIC_PREVIEW.md` (questo)

### Backup operativo
- `/app/ops/backups/backend.conf.v18_pre_stage3.20260518T004844Z.bak`

---

## 2. File modificati

- `/etc/supervisor/conf.d/backend.conf` (allowlist 100→200, ledger cap 1000→2500; backup preservato)
- `/app/backend/routes/affinity_gift_spend.py` (hard cap interno `_canary_ledger_cap()` alzato da `min(v, 1000)` a `min(v, 5000)` per consentire la cap V18 di 2500 mantenendo un tetto invalicabile di 5000)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (registrati 9 nuovi validator V18 + nuovo bucket `SUPERSEDED_AFTER_STAGE3` per V17 preflight/composite/sub-validators)

**File esplicitamente NON modificati (invariante hard)**:
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`
- `/app/frontend/app/combat.tsx`
- `/app/backend/synergy_system.py`
- `/app/backend/game_systems.py`
- Tutti i file in `/app/frontend/app/*` (audit `frontend_source_unchanged_in_v18` PASS escludendo solo `yarn.lock`)

---

## 3. Preflight V18

**Status**: PASS. Tutti i gates verde:
- API health 200, /api/heroes=100, no-borea
- canary_flag_on, inv_writes_flag_on
- stage2_allowlist≥100, cap≥1000, ledger entro cap
- battle_runtime_attached=false, applied_to_combat=false, buffs=false
- borea 404, non-allow 423
- battle files unchanged
- ugi/uas presenti, no negative inventory, V16 seed 50 + V17_STAGE2 seed 50
- rollback scripts present
- V17 composite PASS, baseline v6 diff PASS
- ui_safety_no_spend_token, no_shadow_adapter_live_leak

---

## 4. Stage2 Extended Monitoring (V18)

**Status**: PASS. 160 campioni, 0 trigger.
- 70 health 200, 20 canary-status 200, 20 /api/heroes=100
- 15 Borea POST: tutti 404 (0 bad)
- 15 non-allowlist: tutti 423 (0 bad)
- 12 idempotent replay su tx storiche: tutti 200 `idempotent_replay` con inventory_unchanged + affinity_unchanged
- 8 fresh Stage2 spend (`stage2_qa_011..018`): inventory −1 / affinity +1 esatti
- 0 HTTP 5xx, 0 negative inventory, 0 buffs, 0 battle wiring
- inv_mut_delta = aff_mut_delta = 8

---

## 5. Stage3 QA Expansion — Prep / Apply

**Status**: **APPLIED_PASS** (tutti i gate verde → apply commesso).

Espansione applicata in modo gated:
- Aggiunti 100 utenti sintetici QA: `stage3_qa_001..stage3_qa_100`
- Allowlist totale: **100 → 200** (Stage1 + Stage2 + Stage3)
- Ledger cap: **1000 → 2500**
- Seed inventory: 100 docs `gift_test_001 x10` con `metadata.seed_task=V18_STAGE3`
- Backup supervisor.conf: `/app/ops/backups/backend.conf.v18_pre_stage3.20260518T004844Z.bak`
- Hard caps salvaguardia: max_total_allowlist=500, max_ledger_cap=5000, max_stage3_users=200
- Smoke verify post-restart: PASS

**Nota tecnica**: in fase di smoke, il primo apply ha rilevato che il cap effettivo restava bloccato a 1000 a causa di un hard-cap legacy `min(v, 1000)` in `_canary_ledger_cap()`. Alzato in modo controllato a `min(v, 5000)` (tetto V18). Apply rieseguito → APPLIED_PASS.

---

## 6. Stage3 Monitoring (V18)

**Status**: PASS. 101 campioni, 0 trigger.
- 40 health, 15 heroes=100, 15 Borea POST (tutti 404), 15 non-allowlist (tutti 423)
- 8 fresh Stage3 spend (`stage3_qa_001..008`): inventory −1 / affinity +1 esatti
- 8 idempotent replay Stage3: tutti 200 `idempotent_replay`, NO state change
- 0 HTTP 5xx, 0 negative inventory, 0 buffs, 0 battle wiring
- inv_mut_delta = aff_mut_delta

---

## 7. Public UI Preview Readiness

**Status**: PASS — **plan-only**.

`affinity_gifts_public_preview_readiness_v1.json` (`design_only: true`, `runtime_attached: false`, `phase: DESIGN_PLAN_ONLY_NO_UI_MUTATION_IN_V18`).

Audit `audit_affinity_gifts_public_preview_safety.py`:
- ✅ Readiness JSON design_only + plan-only
- ✅ Nessun `fetch/axios/post()` verso `/api/affinity/gift-spend` nel frontend
- ✅ Nessun import JS/TS di `battle_engine` / `battle_core` / `synergy_system` / `game_systems`
- ✅ Nessun bottone testuale `>Spend Gift<` / `>Claim Gift<` / `>Claim Affinity<`
- ✅ `combat.tsx` invariato
- ✅ `frontend/` source invariato in V18 (escluso `yarn.lock`)

Riferimenti a Borea esistenti (`isBorea = hero.id === 'borea'` in `sanctuary.tsx` / `divine-weapons-catalog.tsx`) sono **filtri di sicurezza** che già blocchino la rivelazione, NON una rivelazione. L'audit aggiornato distingue chiamate reali da filtri.

**Nessun pulsante public spend creato. Nessun pulsante claim. Nessuna mutazione UI.**

---

## 8. K6 / Locust Real Attempt

**Status**: PASS.
- **k6**: non installato (richiederebbe sudo install: rinviato a task gated separato; istruzioni esatte in `af2n_v18_k6_locust_result_v1.json`).
- **Locust**: ✅ **installato con successo** via `pip3 install --quiet --no-warn-script-location locust`. Smoke run reale: 3 vus, 5s, headless, target `http://127.0.0.1:8001`, paths read-only (`/api/health`, `/api/affinity/gift-spend/canary-status`). Exit code 0.
- **Python fallback**: 3500 req totali (1400 health + 400 canary-status + 200 heroes + 700 non-allowlist + 800 borea reject) — 0 HTTP 5xx, 0 borea_bad, 0 non_allowlist_bad, ~185 RPS sostenuti (con concurrency=1 sequenziale).

**Raccomandazione**: Locust LIVE plan a piena scala (multi-user) resta task gated separato. k6 install dipende dall'autorizzazione sudo.

---

## 9. Rollback Readiness V18

**Status**: PASS.
- 7 rollback script presenti (V14/V15/V16 + Stage1 seed + Stage2 + **Stage3 NEW V18** + ops shell)
- Directory backup `/app/ops/backups/` scrivibile
- Dry-run Stage3 rollback OK; dry-run Stage2 rollback OK

---

## 10. Safety Rollup M

**Status**: PASS (`collection_affinity_runtime_activation_readiness_rollup_v13.json` generato).
- `supersedes`: rollup_v12
- `runtime_state`: **`stage3_qa_active_no_broad_rollout`**
- `stage2_state`: APPLIED
- `stage3_state`: **APPLIED**
- `broad_rollout_authorized`: false
- `public_spend_ui`: false
- `battle_wiring_live`: false
- `buffs_enabled`: false
- `Borea_hidden`: true
- `inventory_live_scope`: allowlist_only
- `canary_allowlist_size`: 200, `ledger_cap`: 2500
- `rollback_ready`: true
- `stage2_extended_monitoring.overall_status`: PASS (160 samples, 0 5xx)
- `stage3_monitoring.overall_status`: PASS (101 samples, 0 5xx)
- `k6_locust_v18_state.locust_binary_present_after_attempt`: true, `real_locust_smoke_exit`: 0
- `next_decision`: **`extended_monitoring`**

---

## 11. Borea Safety

- `/api/heroes` count = 100, nessun id Borea/greek_borea/primordial_gaia.
- POST `/api/affinity/gift-spend` con hero_id Borea → **HTTP 404** (verificato 30+ volte durante monitoring).
- Ledger query `hero_id IN [borea, greek_borea, primordial_gaia]` → **0 righe**.
- Frontend: riferimenti a `borea` solo come safety filter (`isBorea` guard), nessuna rivelazione.

---

## 12. Validator Results

| Task | Status |
|---|---|
| V18-PREFLIGHT | ✅ PASS |
| AF2-N-STAGE2-EXTENDED-MONITORING-V18 | ✅ PASS |
| AF2-N-STAGE3-QA-EXPANSION-APPLY | ✅ PASS (APPLIED_PASS) |
| AF2-N-STAGE3-MONITORING-V18 | ✅ PASS |
| AF2-N-PUBLIC-UI-PREVIEW-SAFETY | ✅ PASS |
| AF2-L-K6-LOCUST-V18 | ✅ PASS (Locust installed + smoke) |
| V18-ROLLBACK-READINESS | ✅ PASS |
| SAFETY-ROLLUP-M | ✅ PASS |
| ULTRA-COMBO-V18 composite (42 checks) | ✅ PASS |

---

## 13. Suite / Baseline

- `python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff --json-out /app/backend/reports/suite_v18.json`
- **Overall: PASS** — pass=106, fail=0, miss=0
- Validator SUPERSEDED auto-marked (V12-V17 pre-Stage3): documentati in 4 frozenset (`SUPERSEDED_AFTER_AF2N`, `SUPERSEDED_AFTER_INV_WRITES`, `SUPERSEDED_AFTER_STAGE2`, nuovo `SUPERSEDED_AFTER_STAGE3`).
- **RM1.32-PRE baseline diff**: PASS (`hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` invariato).

---

## 14. API Smoke (post-Stage3)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | ✅ 200 |
| `GET /api/heroes` count | 100, no Borea | ✅ |
| `GET /api/affinity/gift-spend/canary-status` | 200, size=200, cap=2500, flag on, inv on | ✅ |
| `POST gift-spend` Borea | 404 | ✅ 404 |
| `POST gift-spend` non-allowlist | 423 | ✅ 423 |
| `POST gift-spend` Stage2 user | 200 `applied_inventory_live` | ✅ |
| `POST gift-spend` Stage3 user (es. `stage3_qa_050`) | 200 `applied_inventory_live`, inv 10→9, aff 0→1 | ✅ |
| `POST gift-spend` idempotent replay | 200 `idempotent_replay`, no state change | ✅ |

---

## 15. UI Safety

- ❌ Nessun pulsante public spend creato.
- ❌ Nessun pulsante claim.
- ❌ Nessuna mutazione UI in V18.
- ❌ Nessun runtime toggle esposto in UI.
- ❌ Nessuna wiring battle UI.
- ❌ Nessuna rivelazione Borea (riferimenti esistenti sono safety filters).
- ✅ Public UI preview resta **PLAN-ONLY** (`design_only: true`, gated da futura autorizzazione esplicita).
- ✅ `combat.tsx` invariato (git diff stat vuoto).
- ✅ Audit `audit_affinity_gifts_public_preview_safety.py` PASS.

---

## 16. Runtime / DB / Gacha / Roster / Catalog Safety

- **Runtime**: feature flag + inventory writes attivi (Stage1+Stage2+Stage3 allowlist 200). `applied_to_combat=false`, `battle_runtime_attached=false`, `buffs_enabled=false`.
- **DB**:
  - `gift_transaction_ledger`: tutte righe `canary=True`, count entro cap 2500. `inventory_mutated` == `affinity_points_mutated`. 0 buffs, 0 battle wiring, 0 Borea heroes.
  - `user_gift_inventory`: 200+ docs (50 V16 + 50 V17_STAGE2 + 100 V18_STAGE3 + entries spend). 0 docs `quantity<0`.
  - `user_affinity_state`: incrementi esatti per ogni spend.
- **Gacha / Roster / Character Bible / asset / skill catalogs / final_numbers**: NESSUNA modifica.

---

## 17. Warnings

- `k6` non installato (install richiede sudo / system path); rinviato a task gated separato. Istruzioni complete nel result JSON.
- `_canary_ledger_cap()` hard-cap interno alzato da 1000 a 5000 in `affinity_gift_spend.py` per accomodare Stage3 (cap=2500). Tetto invalicabile resta 5000. Modifica registrata nel git diff della route (file consentito).
- V13/V14/V15/V16/V17 preflight + composite ora marcati `SUPERSEDED` quando Stage3 applicato — comportamento atteso e documentato in 4 frozenset nella suite runner.
- Locust installato in user-site via pip3 (`--no-warn-script-location`). Reversibile via `pip3 uninstall locust`.

---

## 18. Final Recommendation

**Recommendation**: **EXTENDED_MONITORING**.

Stage3 QA expansion APPLICATA in modo gated e safe (100→200 utenti QA sintetici, cap 1000→2500). Inventory live writes operativi su 200 utenti allowlist con tutti gli invarianti hard tenuti:
- /api/heroes = 100, Borea hidden/404
- 0 HTTP 5xx, 0 unauthorized spend, 0 negative inventory, 0 buffs, 0 battle wiring
- battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py NON modificati
- Public UI preview resta plan-only senza pulsante spend
- Rollback Stage3 dry-run OK + backup supervisor.conf disponibile
- Locust ora installato (run smoke OK) → future load test reali low-impact possibili

Prossimo prudente: **AF2-N-STAGE3-EXTENDED-MONITORING (24-72h)** sotto carico QA reale prima di considerare ulteriori espansioni.

**Broad rollout, STACK-G full wiring, public spend UI restano gated tasks separati e NON autorizzati.**

---

## 19. Suggested Next Tasks

- **P1** `AF2-N-STAGE3-EXTENDED-MONITORING` — observation window 24-72h Stage3 sotto carico QA reale.
- **P1** `AF2-L-LOCUST-LIVE-REAL` — sfruttare locust ora installato per load test reali low-impact (read-only paths + replay) con scaling controllato.
- **P2** `AF2-N-STAGE4-INTERNAL-BETA-PREP` — pianificazione (DESIGN_ONLY) eventuale Stage4 controllata (es. 500 users, cap 5000), gated.
- **P2** `OPS-D-SUPERVISOR-RESTART-IDEMPOTENT` — automazione che gestisce reread+update+restart in modo idempotente con validazione env post-restart.
- **P2** `AF2-L-K6-INSTALL-GATED` — install k6 via tarball richiede sudo: task gated separato con rollback.
- **P3** `AF2-N-PUBLIC-PREVIEW-UI-IMPLEMENT` — implementazione concreta read-only della preview UI seguendo `affinity_gifts_public_preview_readiness_v1.json`. **Strettamente deferred fino ad autorizzazione esplicita**.
- **P3** `STACK-G-WIRING-FULL` — collegamento `affinity_state` → `battle_engine.py`/`combat.tsx`. **Strettamente deferred**.

---

## Acceptance V18 — Checklist Finale

- [x] no broad rollout
- [x] Stage3 applicato in modo safe/gated con backup + rollback ready
- [x] no public spend UI
- [x] inventory/affinity mutation esatta e idempotente (Stage1+Stage2+Stage3)
- [x] no battle wiring
- [x] /api/heroes = 100
- [x] Borea hidden/404
- [x] no unauthorized spend success
- [x] no 5xx
- [x] rollback readiness PASS
- [x] suite/baseline PASS (106/106, RM1.32-PRE PASS)
- [x] no battle/gacha/roster/catalog mutation
- [x] UI safety PASS

**ULTRA-COMBO V18 — COMPLETATO**
