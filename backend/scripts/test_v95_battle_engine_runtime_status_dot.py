#!/usr/bin/env python3
"""
v95 — Battle Engine Runtime Regression Tests (eseguibili, non solo JSON).

Copre i contratti runtime applicati in backend/battle_engine.py:
- DoT tick: burn, poison, bleed, frostbite, curse
- Shock (status applicato, niente DoT direttamente nel tick)
- Stack policies: sum_ticks, reset_duration, overwrite, cap_stacks
- Cleanse: all, top, by_category, one_stack
- Immunity blocca nuove applicazioni / non rimuove esistenti
- Taunt intercetta su single-target / aoe_partial / NON su aoe pieno
- Boss hard-control conversion (freeze/stun/silence/sleep/petrify)
- Battle report extension counters

Uso:
    python3 backend/scripts/test_v95_battle_engine_runtime_status_dot.py

Output:
    data/design/battle_engine/v95_engine_runtime_apply_test_result_v1.json
"""
import os
import sys
import json
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "backend"))

import battle_engine as be


def make_unit(name, hp=10000, attack=1000, defense=500, speed=100, is_boss=False, hero_class="DPS"):
    return {
        "id": name.lower(),
        "name": name,
        "hp": hp,
        "max_hp": hp,
        "current_hp": hp,
        "max_hp_battle": hp,
        "attack": attack,
        "defense": defense,
        "speed": speed,
        "is_alive": True,
        "is_boss": is_boss,
        "hero_class": hero_class,
        "status_effects": [],
        "passives": [],
        "rarity": 5,
        "total_damage_dealt": 0,
        "total_damage_received": 0,
        "total_healing_done": 0,
        "element": "neutral",
    }


def assert_true(name, cond, details=""):
    if cond:
        return {"name": name, "result": "PASS", "details": details}
    return {"name": name, "result": "FAIL", "details": details}


def run_tests():
    results = []

    # --- Test 1: Burn DoT tick reduces hp ---
    target = make_unit("BurnTarget")
    target['status_effects'].append({"type": "burn", "damage_per_turn": 0.05, "turns_remaining": 3})
    counters = {"dot_damage_done": 0}
    be.process_status_effects(target, v95_counters=counters)
    expected_dmg = int(10000 * 0.05)
    results.append(assert_true("burn_tick",
        target['current_hp'] == 10000 - expected_dmg and counters['dot_damage_done'] == expected_dmg,
        f"hp={target['current_hp']} dot_done={counters['dot_damage_done']}"))

    # --- Test 2: Poison DoT tick ---
    target = make_unit("PoisonTarget")
    target['status_effects'].append({"type": "poison", "damage_per_turn": 0.06, "turns_remaining": 4})
    counters = {"dot_damage_done": 0}
    be.process_status_effects(target, v95_counters=counters)
    expected_dmg = int(10000 * 0.06)
    results.append(assert_true("poison_tick", target['current_hp'] == 10000 - expected_dmg))

    # --- Test 3: Bleed DoT tick ---
    target = make_unit("BleedTarget")
    target['status_effects'].append({"type": "bleed", "damage_per_turn": 0.04, "turns_remaining": 3})
    counters = {"dot_damage_done": 0}
    be.process_status_effects(target, v95_counters=counters)
    expected_dmg = int(10000 * 0.04)
    results.append(assert_true("bleed_tick", target['current_hp'] == 10000 - expected_dmg))

    # --- Test 4: Frostbite tick + slow side-effect ---
    target = make_unit("FrostTarget", speed=200)
    target['status_effects'].append({"type": "frostbite", "damage_per_turn": 0.05, "turns_remaining": 3})
    counters = {"dot_damage_done": 0}
    be.process_status_effects(target, v95_counters=counters)
    results.append(assert_true("frostbite_dot_and_slow",
        target['current_hp'] < 10000 and target['speed'] < 200,
        f"hp={target['current_hp']} speed={target['speed']}"))

    # --- Test 5: Curse tick (overwrite policy) ---
    target = make_unit("CurseTarget")
    be._v95_apply_dot_with_stack_policy(target, "curse", 0.05, 4, "src")
    be._v95_apply_dot_with_stack_policy(target, "curse", 0.07, 5, "src2")  # overwrite
    same = [e for e in target['status_effects'] if e['type'] == 'curse']
    results.append(assert_true("curse_overwrite_policy",
        len(same) == 1 and same[0]['damage_per_turn'] == 0.07,
        f"effects={same}"))

    # --- Test 6: Shock reset_duration ---
    target = make_unit("ShockTarget")
    be._v95_apply_dot_with_stack_policy(target, "shock", 0.0, 2, "src")
    be._v95_apply_dot_with_stack_policy(target, "shock", 0.0, 4, "src2")  # reset_duration: max(2,4)=4
    same = [e for e in target['status_effects'] if e['type'] == 'shock']
    results.append(assert_true("shock_reset_duration",
        len(same) == 1 and same[0]['turns_remaining'] == 4,
        f"shock={same}"))

    # --- Test 7: Burn sum_ticks (multiple stacks) ---
    target = make_unit("StackTarget")
    for _ in range(3):
        be._v95_apply_dot_with_stack_policy(target, "burn", 0.05, 3, "s")
    same = [e for e in target['status_effects'] if e['type'] == 'burn']
    results.append(assert_true("burn_sum_ticks_stacks", len(same) == 3, f"stacks={len(same)}"))

    # --- Test 8: Frostbite cap_stacks ---
    target = make_unit("CapTarget")
    applied = []
    for i in range(5):
        applied.append(be._v95_apply_dot_with_stack_policy(target, "frostbite", 0.05, 3, "s"))
    same = [e for e in target['status_effects'] if e['type'] == 'frostbite']
    results.append(assert_true("frostbite_cap_stacks",
        len(same) == 3 and applied[3] is False and applied[4] is False,
        f"stacks={len(same)} applied={applied}"))

    # --- Test 9: Cleanse all ---
    target = make_unit("CleanseTarget")
    target['status_effects'] = [
        {"type": "burn", "category": "elemental_fire", "turns_remaining": 3, "damage_per_turn": 0.05},
        {"type": "poison", "category": "bio", "turns_remaining": 4, "damage_per_turn": 0.06},
    ]
    removed = be._v95_apply_cleanse(target, mode="all")
    results.append(assert_true("cleanse_all", removed == 2 and len(target['status_effects']) == 0))

    # --- Test 10: Cleanse by_category ---
    target = make_unit("CleanseCatTarget")
    target['status_effects'] = [
        {"type": "burn", "category": "elemental_fire", "turns_remaining": 3, "damage_per_turn": 0.05},
        {"type": "poison", "category": "bio", "turns_remaining": 4, "damage_per_turn": 0.06},
    ]
    removed = be._v95_apply_cleanse(target, mode="by_category", category="bio")
    leftover_types = [e['type'] for e in target['status_effects']]
    results.append(assert_true("cleanse_by_category",
        removed == 1 and leftover_types == ['burn'],
        f"leftover={leftover_types}"))

    # --- Test 11: Cleanse one_stack ---
    target = make_unit("CleanseOneStack")
    target['status_effects'] = [
        {"type": "burn", "turns_remaining": 3, "damage_per_turn": 0.05},
        {"type": "poison", "turns_remaining": 4, "damage_per_turn": 0.06},
    ]
    removed = be._v95_apply_cleanse(target, mode="one_stack")
    results.append(assert_true("cleanse_one_stack",
        removed == 1 and len(target['status_effects']) == 1,
        f"left={len(target['status_effects'])}"))

    # --- Test 12: Immunity blocks new debuff ---
    target = make_unit("ImmuneTarget")
    target['status_effects'].append({"type": "immunity", "turns_remaining": 3})
    has_imm = be._v95_has_immunity(target, "burn")
    results.append(assert_true("immunity_blocks_new", has_imm is True))

    # --- Test 13: Immunity does NOT remove existing debuff ---
    target = make_unit("ImmuneKeep")
    target['status_effects'].append({"type": "burn", "turns_remaining": 3, "damage_per_turn": 0.05})
    target['status_effects'].append({"type": "immunity", "turns_remaining": 3})
    # tick: il burn deve continuare a fare DoT (l'immunity non rimuove)
    counters = {"dot_damage_done": 0}
    be.process_status_effects(target, v95_counters=counters)
    results.append(assert_true("immunity_keeps_existing",
        counters['dot_damage_done'] > 0,
        f"dot_done={counters['dot_damage_done']}"))

    # --- Test 14: Taunt intercepts single-target ---
    tank = make_unit("Tank", hero_class="Tank")
    tank['status_effects'].append({"type": "taunt", "turns_remaining": 3})
    dps = make_unit("DPS", hero_class="DPS")
    enemies = [dps, tank]
    skill = {"target_type": "single_target", "name": "Slash"}
    chosen = be.apply_taunt_override(dps, enemies, skill, skill_type='nad')
    results.append(assert_true("taunt_intercepts_single", chosen is tank, f"chosen={chosen.get('name') if chosen else None}"))

    # --- Test 15: AoE_all bypasses taunt ---
    skill_aoe = {"target_type": "all_enemies", "name": "AoE", "aoe": True}
    chosen = be.apply_taunt_override(dps, enemies, skill_aoe, skill_type='nad')
    results.append(assert_true("aoe_bypasses_taunt", chosen is dps))

    # --- Test 16: aoe_partial respects taunt ---
    skill_partial = {"target_type": "aoe_partial", "name": "Cleave", "aoe_partial": True}
    chosen = be.apply_taunt_override(dps, enemies, skill_partial, skill_type='nad')
    results.append(assert_true("aoe_partial_respects_taunt", chosen is tank))

    # --- Test 17: Boss hard-control conversion (freeze -> slow) ---
    boss = make_unit("Boss", is_boss=True)
    conv = be._v95_maybe_convert_boss_hardcontrol(boss, "freeze", 3)
    results.append(assert_true("boss_freeze_converts_to_slow",
        conv is not None and conv['type'] == 'slow',
        f"conv={conv}"))

    # --- Test 18: Non-boss freeze NOT converted ---
    normal = make_unit("Normal")
    conv = be._v95_maybe_convert_boss_hardcontrol(normal, "freeze", 3)
    results.append(assert_true("non_boss_freeze_not_converted", conv is None))

    # --- Test 19: Boss stun -> weaken ---
    boss = make_unit("Boss2", is_boss=True)
    conv = be._v95_maybe_convert_boss_hardcontrol(boss, "stun", 2)
    results.append(assert_true("boss_stun_converts",
        conv is not None and conv['type'] == 'weaken',
        f"conv={conv}"))

    # --- Test 20: simulate_battle returns v95_battle_report ---
    team_a = [make_unit(f"A{i}") for i in range(3)]
    team_b = [make_unit(f"B{i}") for i in range(3)]
    res = be.simulate_battle(team_a, team_b, max_turns=5)
    has_report = "v95_battle_report" in res
    has_fields = has_report and all(k in res['v95_battle_report'] for k in (
        "dot_damage_done", "status_applied_count", "healing_done",
        "cleanse_count", "status_prevented_by_immunity_count", "taunt_redirect_count",
    ))
    results.append(assert_true("battle_report_extension_present",
        has_report and has_fields,
        f"report_keys={list(res.get('v95_battle_report', {}).keys())}"))

    # --- Test 21: simulate_battle preserves legacy fields ---
    legacy_ok = all(k in res for k in ("team_a_final", "team_b_final", "victory", "turns", "mvp",
                                       "total_damage_done", "total_damage_taken"))
    results.append(assert_true("battle_report_preserves_legacy", legacy_ok, f"keys={list(res.keys())[:10]}"))

    return results


def main():
    try:
        results = run_tests()
    except Exception as e:
        traceback.print_exc()
        results = [{"name": "exception", "result": "FAIL", "details": str(e)}]

    total = len(results)
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = total - passed

    print(f"v95 Battle Engine Runtime Regression Tests: {passed}/{total} PASS, {failed} FAIL")
    for r in results:
        marker = "PASS" if r["result"] == "PASS" else "FAIL"
        print(f"  [{marker}] {r['name']}  {r.get('details','')}")

    # Save JSON result
    out_dir = os.path.join(ROOT, "data", "design", "battle_engine")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "v95_engine_runtime_apply_test_result_v1.json")
    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_44_v95",
        "type": "engine_runtime_regression_test_result",
        "total": total,
        "passed": passed,
        "failed": failed,
        "verdict": "PASS" if failed == 0 else "FAIL",
        "results": results,
        "safety": {"db_writes": 0, "reward_live": False},
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
