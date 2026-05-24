# 123D — PROJECT_A Track D — COMBAT_SKILL_STATUS_RUNTIME_MAP

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: D  
**Mode**: `audit_design_no_combat_mutation`  
**Verdict**: 🟢 `TRACK_D_COMBAT_SKILL_STATUS_RUNTIME_MAP_READY`  
**Rollback**: N/A (audit/design only)

---

## 1. Scopo

Produrre la **mappa di implementazione MVP combat/skill/status runtime** senza alcun cambiamento al combat. Identifica file/ruoli, definisce uno slice MVP minimo isolato dal combat live, propone una sequenza di pack futuri.

## 2. Combat runtime inventory

| Ruolo | File | Forbidden change | Stato |
|---|---|---|---|
| engine | `/app/backend/services/battle_engine.py` | ✅ | UNCHANGED |
| core | `/app/backend/services/battle_core.py` | ✅ | UNCHANGED |
| frontend combat screen | `/app/frontend/app/combat.tsx` | ✅ | UNCHANGED |
| backend combat routes | `/app/backend/routes/combat.py` | ❌ | present, future inventory |
| skill kit adapter | `/app/backend/services/hero_skill_kit_runtime_adapter.py` | ❌ | present, wiretest v1 ok |
| skill kit catalog | `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json` | ❌ | baseline v6 PASS |

## 3. MVP runtime slice proposto

**Nome**: `COMBAT_SKILL_STATUS_MVP_V1`

**Scope**: skill activation + status apply su un singolo hero non-Borea (es. `zeus`) in un sandbox endpoint dedicato `/api/combat/_skill_kit_wiretest` (read-only adapter call gia' presente).

### In scope
- `hero_skill_kit_runtime_adapter.resolve_skill_kit()` call
- status effect catalog read-only fetch
- unit test harness via existing wiretest fixtures

### Out of scope
- `battle_engine.py` modification
- `battle_core.py` modification
- `combat.tsx` modification
- damage application live combat
- buff/debuff persistence on `user_heroes`

**LOC estimate**: ~30 LOC additive in **nuovo file** `skill_kit_mvp_runner.py` **NOT imported by combat**.

## 4. No-diff guard

File watchati per non-mutation:
- `/app/backend/services/battle_engine.py`
- `/app/backend/services/battle_core.py`
- `/app/frontend/app/combat.tsx`

**Current status**: tutti presenti e **NOT mutated** in Track D.  
**Future validator proposto**: `validate_combat_runtime_no_diff_v1.py` (sha256 baseline + FAIL if mismatch).

## 5. Future apply gates (3)

| Gate | Name | Prereq |
|---|---|---|
| **CSK-G1** | MVP_SANDBOX_NO_LIVE_COMBAT | design map + adapter wiretest + status effect catalog freeze |
| **CSK-G2** | PARTIAL_LIVE_COMBAT_SKILL_HOOK_DESIGN | CSK-G1 + product signoff + 1 release cycle sandbox |
| **CSK-G3** | FULL_LIVE_COMBAT_SKILL_HOOK_APPLY | CSK-G2 + QA full regression + explicit user approval |

## 6. Implementation sequence proposta (5 pack)

1. `HERO_SKILL_KIT_CATALOG_FREEZE_PACK`
2. `STATUS_EFFECT_CATALOG_BASELINE_PACK`
3. `SKILL_KIT_MVP_SANDBOX_RUNNER_PACK` (new file, NOT imported by combat)
4. `SKILL_KIT_MVP_VALIDATOR_PACK` (HTTP smoke on sandbox)
5. `COMBAT_RUNTIME_NO_DIFF_GUARD_PACK` (sha256 invariant)

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| `battle_engine.py` changes | ❌ No |
| `battle_core.py` changes | ❌ No |
| `combat.tsx` changes | ❌ No |
| Combat behavior mutation | ❌ No |
| Skill/status live activation | ❌ No |
