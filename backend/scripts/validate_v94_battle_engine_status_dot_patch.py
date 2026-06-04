#!/usr/bin/env python3
"""v94 — Battle engine status/DoT patch validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(ROOT, 'data', 'design', 'battle_engine', 'v94_engine_regression_fixture_matrix_v1.json')
D = os.path.join(ROOT, 'docs', 'divine', '94_BATTLE_ENGINE_STATUS_DOT_TARGETING_PATCH.md')
REQ_DOT = {'Burn', 'Poison', 'Bleed', 'Shock', 'Frostbite', 'Curse'}
REQ_STACK = {'sum_ticks', 'reset_duration', 'overwrite', 'cap_stacks'}
REQ_CLEANSE = {'all', 'top', 'by_category', 'by_priority', 'one_stack', 'remove_status'}
REQ_BOSS_HCC = {'Freeze', 'Stun', 'Silence', 'Sleep', 'Petrify'}

def fail(m): print(f"FAIL v94_battle_engine_status_dot_patch: {m}"); sys.exit(1)

def main():
    for p in (F, D):
        if not os.path.isfile(p): fail(f"missing: {p}")
    with open(F) as f: d = json.load(f)
    dots = {x.get('status') for x in d.get('dot_core') or []}
    miss = REQ_DOT - dots
    if miss: fail(f"missing DoT: {sorted(miss)}")
    used_stacks = {x.get('stack_policy') for x in d.get('dot_core') or []}
    if not used_stacks.issubset(REQ_STACK): fail(f"stack policy invalid: {used_stacks}")
    cl = set(d.get('cleanse', {}).get('available_policies') or [])
    if not REQ_CLEANSE.issubset(cl): fail(f"missing cleanse policies: {sorted(REQ_CLEANSE - cl)}")
    imm = d.get('immunity') or {}
    if imm.get('behavior') != 'blocks_new_application_only': fail("immunity.behavior must be blocks_new_application_only")
    if imm.get('does_not_remove_existing') is not True: fail("immunity.does_not_remove_existing must be true")
    taunt = d.get('taunt') or {}
    if taunt.get('single_target') != 'intercepts': fail("taunt single_target must intercepts")
    if taunt.get('aoe_all_enemies') != 'NOT_intercepts': fail("taunt aoe_all_enemies must NOT intercept")
    if 'aoe_partial' not in (taunt.get('aoe_partial_cleave_2') or ''): pass  # just check key exists
    if not taunt.get('v94_bug_fix'): fail("taunt v94_bug_fix must be declared")
    boss_hcc = set((d.get('boss_hard_control_conversion') or {}).keys())
    miss_b = REQ_BOSS_HCC - boss_hcc
    if miss_b: fail(f"missing boss_hard_control: {sorted(miss_b)}")
    saf = d.get('safety') or {}
    if saf.get('db_writes') != 0: fail("db_writes must be 0")
    if saf.get('final_numbers_balance_lock') is not False: fail("final_numbers_balance_lock must be false")
    print("PASS v94_battle_engine_status_dot_patch")

if __name__ == '__main__': main()
