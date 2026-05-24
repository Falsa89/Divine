# 125C — PROJECT_C Track C — STATUS_EFFECT_CATALOG_BASELINE

**Verdict**: 🟢 `TRACK_C_STATUS_EFFECT_CATALOG_BASELINE_READY`

## 10 categorie canonical
buff_offensive, buff_defensive, buff_support, debuff_offensive, debuff_defensive, control, dot, hot, shield, meta.

## 10 effetti baseline
atk_up_pct, def_up_pct, hot_pct, shield_pct, atk_down_pct, def_down_pct, stun, freeze, bleed_pct, immunity.

## Hard invariants (anti-power-creep)
- duration_turns ∈ [1..10]
- stack_max ≤ 5
- value_pct ∈ [-50..+50]
- no `always_active=true`

**Runtime active**: ❌ False (catalog baseline only, deferred a `STATUS_EFFECT_RUNTIME_ATTACH_PACK`).
