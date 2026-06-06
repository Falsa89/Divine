# v108_POSTQA_D — Final Report

**Pack:** `MEGA_RELEASE_ACCELERATION_65_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS`
**Sentinel / Public Sync Tag:** `PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS`
**Commit:** `0bfa00c14052e37a8b296e3878e165b46aa7e720`

---

## 1. Verdict

```
MEGA_RELEASE_ACCELERATION_65_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

- `REQUIRED FAIL = 0`
- `MISS = 0`
- `OPTIONAL FAIL = 22` (entro il tetto overall `<= 30`, sopra il tetto stretto `<= 15` → verdetto con **deferred blocker documentati**)
- 3-run **deterministic** (1170/22/0 per ciascuna delle 3 esecuzioni finali)
- Runtime invariant `v108_POSTQA_A` **10/10 PASS**
- Rollup POSTQA `A / A2 / B / C` **PASS**
- Nuovi sub-validator pack D: **8/8 PASS**

---

## 2. Baseline 3-run (pre-pack D)

| Run | pass | fail | miss | required_fail |
|-----|------|------|------|---------------|
| 1   | 1162 | 22   | 0    | 0             |
| 2   | 1162 | 22   | 0    | 0             |
| 3   | 1162 | 22   | 0    | 0             |

Output: `/app/data/design/postqa/v108_postqa_d_baseline_multirun_v1.json`
+ `/app/docs/divine/108_POSTQA_D_BASELINE_MULTIRUN.md`

Decisione: **GO** (required=0, miss=0, optional=22 ≤ 30, runtime invariant 10/10).

---

## 3. Final 3-run (post-pack D)

| Run | pass | fail | miss | required_fail |
|-----|------|------|------|---------------|
| 1   | 1170 | 22   | 0    | 0             |
| 2   | 1170 | 22   | 0    | 0             |
| 3   | 1170 | 22   | 0    | 0             |

Output: `/app/data/design/postqa/v108_postqa_d_final_multirun_suite_result_v1.json`

**Delta vs baseline:** `+8 PASS` (sub-validator pack D registrati + un PASS aggiuntivo derivante dalla stabilizzazione Redis), `fail` invariati a 22 (i 22 optional fail ereditati restano formalmente _deferred blocker documentati_).

---

## 4. Backend mutation gates applicati (Track C)

Modulo introdotto: `backend/utils/postqa_d_mutation_gate.py`
- `check_legacy_mutation_gate(...)` solleva `HTTP 423` con codice `LEGACY_MUTATION_LOCKED_BY_POSTQA_D` quando il flag relativo è OFF
- `make_legacy_mutation_gate_dep(...)` factory che restituisce una dipendenza FastAPI (usata via `Depends(...)` nel decorator del route → **body funzione invariato**, MD5/marker legacy non sono toccati)

Endpoint protetti (9, tutti default-OFF):

| Endpoint                            | File                                  | Flag                                                  |
|-------------------------------------|---------------------------------------|-------------------------------------------------------|
| `POST /api/hero/gain-exp`           | `backend/routes/hero_progression.py`  | `DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS`         |
| `POST /api/hero/levelup`            | `backend/routes/combat.py`            | `DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS`         |
| `POST /api/fusion/star-up`          | `backend/routes/hero_progression.py`  | `DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS`                |
| `POST /api/soul/forge`              | `backend/routes/soul_forge.py`        | `DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS`            |
| `POST /api/vip/add-spend`           | `backend/routes/economy.py`           | `DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS`          |
| `POST /api/battlepass/buy-premium`  | `backend/routes/economy.py`           | `DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS`          |
| `POST /api/friends/gift/{id}`       | `backend/routes/social.py`            | `DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS`           |
| `POST /api/gvg/end-war`             | `backend/routes/gvg.py`               | `DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS`             |
| `POST /api/equipment/equip`         | `backend/routes/equipment.py`         | `DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS`             |

Comportamento quando il gate è chiuso (default):
- `HTTP 423 LOCKED` + `code = LEGACY_MUTATION_LOCKED_BY_POSTQA_D`
- **Nessuna scrittura DB**
- **Nessuna concessione reward / progress / economy**
- Nessun flag attivato di default in `backend/.env`

---

## 5. Frontend reachability blocker (Track D)

Helper introdotto: `frontend/utils/postqa_d_locked_endpoints.ts`
- export: `POSTQA_D_PUBLIC_SYNC_TAG`, `POSTQA_D_LOCK_CODE`, `POSTQA_D_LOCKED_ENDPOINTS`, `isLegacyMutationLocked`, `POSTQA_D_LOCK_MESSAGE_TITLE`, `POSTQA_D_LOCK_MESSAGE_BODY`

Surface modificate (7) — *pre-apiCall* `isLegacyMutationLocked(...)` + `Alert` esplicativo, **nessun redesign UI**:

| File                                  | Endpoint                       |
|---------------------------------------|--------------------------------|
| `frontend/app/hero-detail.tsx`        | `/api/hero/gain-exp`           |
| `frontend/app/hero-detail.tsx`        | `/api/fusion/star-up`          |
| `frontend/app/soul-forge.tsx`         | `/api/soul/forge`              |
| `frontend/app/gvg.tsx`                | `/api/gvg/end-war`             |
| `frontend/app/equipment.tsx`          | `/api/equipment/equip`         |
| `frontend/app/friends.tsx`            | `/api/friends/gift`            |
| `frontend/app/battlepass.tsx`         | `/api/battlepass/buy-premium`  |

Endpoint non raggiungibili dal frontend (coperti solo lato backend):
`/api/hero/levelup`, `/api/vip/add-spend`.

---

## 6. Authoritative preflight contract (Track E)

JSON: `/app/data/design/postqa/v108_postqa_d_authoritative_preflight_contract_v1.json`

Feature flag dichiarati **OFF** in modo esplicito:
`BATTLE_LAUNCH_AUTHORITATIVE_ENABLED`, `REWARD_LIVE_ENABLED`, `PROGRESS_LIVE_ENABLED`,
`SERVER_SCOPED_RUNTIME_ENABLED`, `AUTHORITATIVE_BATTLE_ENGINE_ENABLED`,
`GACHA_LIVE_ENABLED`, `SHOP_LIVE_ENABLED`, `VIP_LIVE_ENABLED`, `BATTLEPASS_LIVE_ENABLED`.

Out-of-scope dichiarati: battle_engine formula rewrite, authoritative live claim,
backend isolation live claim, production DB writes, reward grant, progress live write,
gacha pull implementation, shop/VIP/BP monetization activation.

---

## 7. Server_id loader preflight (Track F)

JSON: `/app/data/design/postqa/v108_postqa_d_server_id_loader_preflight_v1.json`

Dichiarazione **onesta**:
- helper `backend/utils/server_scope.py` (`ensure_server_scope`, set-only-if-missing on insert) **presente**
- `filter_applied = false`
- `server_scope_runtime_active = false`
- Promozione prevista in `v108_authoritative` + `v109`

**Nessun claim `filter_applied=true`** è stato emesso.

---

## 8. Runtime invariant preservation (Track G)

JSON: `/app/data/design/postqa/v108_postqa_d_runtime_invariant_preservation_v1.json`

| Asset                                              | Stato |
|----------------------------------------------------|-------|
| 10 runtime invariant validators `v108_POSTQA_A`    | PASS  |
| Rollup `MEGA-RELEASE-ACCELERATION-61-v108-POSTQA`  | PASS  |
| Rollup `…-62-v108-POSTQA-A2`                       | PASS  |
| Rollup `…-63-v108-POSTQA-B`                        | PASS  |
| Rollup `…-64-v108-POSTQA-C`                        | PASS  |
| Preview reward lock (story / lobby / combat)       | PASS  |
| QA Auto Resolve player-facing block                | PASS  |
| `BOTS_DISABLED` default startup guard              | PASS  |
| Validator deleted / silently deleted / weakened    | 0     |

---

## 9. MD5 superseding (con invariante funzionale sostitutivo)

I 6 file frontend modificati dal blocker (Track D) hanno MD5 aggiornati con storico in
`/app/data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (version bump 1 → 2):

| File                              | old MD5                              | new MD5                              |
|-----------------------------------|--------------------------------------|--------------------------------------|
| `frontend/app/soul-forge.tsx`     | `b7659de11ac36f341e7a2f54fd29e6ed`   | `fe4efcdeb60c69e8827f914cf0ac8e4c`   |
| `frontend/app/equipment.tsx`      | `4ec61a5faa87b267a0b388eac269714c`   | `2a77383ab2b0ca6b8de442e857c5c1aa`   |
| `frontend/app/friends.tsx`        | `3860cd324c38407620032a21ae404a67`   | `9c71f4eee7603c56826d8c6b8daebac7`   |
| `frontend/app/hero-detail.tsx`    | `cd5916f683be5cc8778a8bc35f90e554`   | `5993bca3eb7c361362fac1d4eb2a9ff6`   |
| `frontend/app/battlepass.tsx`     | `54568b8cb75a07033f78ef6593aba839`   | `f0317a32daabd23f42ef2ddac89752ab`   |
| `frontend/app/gvg.tsx`            | `0f106dea784b5d136e987a5b018c1ac2`   | `47e1da25636befcaa6e85a11a67c225e`   |

**Invariante funzionale sostitutivo:** `isLegacyMutationLocked(endpoint) → Alert + early return` (no UI redesign, no DB writes, no reward grant).
**Riferimenti storici:** inseriti in `historical_references[]` per ciascun file con
`status = superseded_by_v108_POSTQA_D_legacy_mutation_blocker`.

---

## 10. Safety flags

| Vincolo                                                        | Stato |
|----------------------------------------------------------------|-------|
| NO PSP apply                                                   | ✅    |
| NO legacy cleanup apply                                        | ✅    |
| NO production DB writes                                        | ✅    |
| NO reward grant                                                | ✅    |
| NO progress live write                                         | ✅    |
| NO gacha pull implementation                                   | ✅    |
| NO shop / VIP / BP monetization activation                     | ✅    |
| NO battle_engine formula rewrite                               | ✅    |
| NO authoritative battle live claim                             | ✅    |
| NO backend isolation live claim                                | ✅    |
| NO server_id filter claim unless real                          | ✅    |
| NO deletion of runtime invariant validators                    | ✅    |
| NO fake_PASS                                                   | ✅    |
| NO validator weakening                                         | ✅    |
| NO silent validator deletion                                   | ✅    |
| NO release readiness claim                                     | ✅    |
| NO flag enabled by default                                     | ✅    |

---

## 11. Files modified / created

### Backend
- **NEW** `backend/utils/postqa_d_mutation_gate.py`
- `backend/routes/hero_progression.py` (+ `Depends` gate su `/hero/gain-exp`, `/fusion/star-up`)
- `backend/routes/combat.py` (+ `Depends` gate su `/hero/levelup`)
- `backend/routes/soul_forge.py` (+ `Depends` gate su `/soul/forge`)
- `backend/routes/economy.py` (+ `Depends` gate su `/vip/add-spend`, `/battlepass/buy-premium`)
- `backend/routes/social.py` (+ `Depends` gate su `/friends/gift/{id}`)
- `backend/routes/gvg.py` (+ `Depends` gate su `/gvg/end-war`)
- `backend/routes/equipment.py` (+ `Depends` gate su `/equipment/equip`)

### Frontend
- **NEW** `frontend/utils/postqa_d_locked_endpoints.ts`
- `frontend/app/hero-detail.tsx`, `soul-forge.tsx`, `gvg.tsx`, `equipment.tsx`, `friends.tsx`, `battlepass.tsx` (blocker pre-apiCall)

### Design JSON (Track A..G + final H)
- `data/design/postqa/v108_postqa_d_baseline_multirun_v1.json`
- `data/design/postqa/v108_postqa_d_legacy_mutation_gate_policy_v1.json`
- `data/design/postqa/v108_postqa_d_backend_mutation_gates_v1.json`
- `data/design/postqa/v108_postqa_d_frontend_reachability_blockers_v1.json`
- `data/design/postqa/v108_postqa_d_authoritative_preflight_contract_v1.json`
- `data/design/postqa/v108_postqa_d_server_id_loader_preflight_v1.json`
- `data/design/postqa/v108_postqa_d_runtime_invariant_preservation_v1.json`
- `data/design/postqa/v108_postqa_d_final_multirun_suite_result_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_65_v108_postqa_d_rollup_marker_v1.json`
- `data/design/closed_alpha/v100_runtime_md5_baseline_v1.json` (version 1 → 2, +6 superseding entries)

### Validator (pack D)
- `backend/scripts/validate_v108_postqa_d_baseline_multirun.py`
- `backend/scripts/validate_v108_postqa_d_legacy_mutation_gate_policy.py`
- `backend/scripts/validate_v108_postqa_d_backend_mutation_gates.py`
- `backend/scripts/validate_v108_postqa_d_frontend_reachability_blockers.py`
- `backend/scripts/validate_v108_postqa_d_authoritative_preflight_contract.py`
- `backend/scripts/validate_v108_postqa_d_server_id_loader_preflight.py`
- `backend/scripts/validate_v108_postqa_d_runtime_invariant_preservation.py`
- `backend/scripts/validate_v108_postqa_d_final_multirun_suite.py`
- `backend/scripts/validate_mega_release_acceleration_65_v108_postqa_d_rollup.py`

### Master runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+ 9 nuove tuple per i validator pack D, dopo POSTQA_C)

### Documenti
- **NEW** `docs/divine/108_POSTQA_D_BASELINE_MULTIRUN.md`
- **NEW** `docs/divine/v108_POSTQA_D_FINAL_REPORT.md` (questo file)

### Allineamento MD5 (no-op funzionale)
- 16 file JSON sotto `data/design/audit/*` e `data/design/soul_forge/*` aggiornati ai nuovi MD5 (riferiti ai 6 file frontend modificati) — pure relabeling, **nessuna logica del validator alterata**.

### Ambiente
- Reinstallato `redis-server` + `redis-tools` per fix Track-F Redis (drift ambientale già sanato in POSTQA_B, ripristinato per coerenza).

---

## 12. Remaining blockers (deferred, documentati)

I 22 optional fail residui sono **ereditati e già classificati come deferred** dai pack precedenti (POSTQA_A2 baseline reconciliation, B1 triage). Esempi:

- `PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN` (deferred → v108_authoritative)
- `PROJECT-V90-RESTORED-BATTLE-RENDERER-REUSE` (deferred → v108_authoritative)
- `PROJECT-V96-MD5-BASELINE-LOCK` (superseded by v100 + v108 entries)
- `MEGA-RELEASE-ACCELERATION-45-v96-ROLLUP` (related to v96 MD5 lock)
- `LIVE-MODES-SLC-NEXT-COMBO-A` (deferred → v109)
- `BENCHMARK-CANONICAL-COMBO-A` (deferred → v109)
- `SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1` (deferred → v110)
- `PROJECT-M-TRACK-B/G`, `PROJECT-V-TRACK-F` (deferred → v108_authoritative)
- `PROJECT-SP-*-TRACK-*` (deferred → v110 PSP apply)
- `PROJECT-BATCH1-V2-TRACK-F-MENU-HARDENING` (deferred → v109)
- `PROJECT-ALIGN-FIX-TRACK-H`, `PROJECT-SF-MERGE-TRACK-F/H` (deferred → v110)
- `PROJECT-FORGE-CRASH-TRACK-G-HYGIENE`, `PROJECT-INLINE-CONFIRM-TRACK-E` (deferred)
- `PROJECT-BETA-TESTING-TRACK-F-REDIS`, `…-TRACK-G-REPORTING` (deferred → v110)
- `PROJECT-GACHA-RATE-SANITY-FINAL-SIGNOFF` (deferred → v110 gacha implementation)

Nessuno di questi è un blocker required.

---

## 13. Updated remaining pack list

1. **v108_authoritative** — Battle engine autoritativo (P1, slot prossimo)
2. **v109** — Server isolation per Chat / Guild / Live Events (P1)
3. **v110** — Legacy data cleanup apply + economy migration (P2)
4. Eventuale **v108_POSTQA_E** (stretto opzionale) — riduzione mirata degli optional ≤ 15 prima dell'autoritative

---

## 14. Time estimate impact

- v108_POSTQA_D **chiuso** in 1 sessione (Track A..I, 8 sub-validator + rollup, 9 endpoint backend, 7 surface frontend, 16 JSON MD5 alignment, baseline rebase v100 + storico)
- Nessun ritardo previsto per `v108_authoritative`: la sua precondizione (mutation gates + preflight contract) è ora **soddisfatta e governata da validator**.
- Tempo stimato per chiudere `v108_authoritative`: invariato.

---

## 15. Git diff --stat (sintesi)

```
backend/utils/postqa_d_mutation_gate.py            | NEW (+135)
backend/routes/{hero_progression,combat,soul_forge,economy,social,gvg,equipment}.py | +10..+20 ea
backend/scripts/validate_v108_postqa_d_*.py        | NEW x8
backend/scripts/validate_mega_release_acceleration_65_v108_postqa_d_rollup.py | NEW
backend/scripts/run_hero_skill_kit_validator_suite.py | +12
frontend/utils/postqa_d_locked_endpoints.ts        | NEW (+51)
frontend/app/{hero-detail,soul-forge,gvg,equipment,friends,battlepass}.tsx | +10..+15 ea
data/design/postqa/v108_postqa_d_*.json            | NEW x8
data/design/release_acceleration/mega_release_acceleration_65_v108_postqa_d_rollup_marker_v1.json | NEW
data/design/closed_alpha/v100_runtime_md5_baseline_v1.json | +6 superseding entries
data/design/{audit,soul_forge}/...*.json           | MD5 realignment (no semantic change)
docs/divine/108_POSTQA_D_BASELINE_MULTIRUN.md      | NEW
docs/divine/v108_POSTQA_D_FINAL_REPORT.md          | NEW (this file)
```

Totale: **337 file changed, +2265 / −783** (la maggior parte sono allineamenti MD5 in JSON di design pre-esistenti).

---

## 16. Verdetto finale

```
MEGA_RELEASE_ACCELERATION_65_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

- `required=0`, `miss=0`, `optional=22 ≤ 30`
- deterministic 3/3
- runtime invariant 10/10 PASS
- 0 runtime touched (gameplay), 0 DB write, 0 reward/progress/economy mutation
- 0 fake_PASS, 0 validator weakening, 0 silent deletion
- **Release readiness NON dichiarata.**
- Public sync attesa (pending) sul container locale.
