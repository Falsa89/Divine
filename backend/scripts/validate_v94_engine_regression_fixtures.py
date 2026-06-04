#!/usr/bin/env python3
"""v94 — Engine regression fixtures validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(ROOT, 'data', 'design', 'battle_engine', 'v94_engine_regression_fixture_matrix_v1.json')
REQ_FIXTURES = {'burn_tick', 'poison_tick', 'bleed_tick', 'shock_application', 'frostbite_slow_dot',
                'curse_overwrite', 'cleanse_by_category', 'immunity_blocks_new_debuff',
                'taunt_intercepts_single', 'aoe_ignores_taunt', 'aoe_partial_fixed',
                'boss_freeze_conversion', 'battle_report_aggregates'}

def fail(m): print(f"FAIL v94_engine_regression_fixtures: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(F): fail(f"missing: {F}")
    with open(F) as f: d = json.load(f)
    fx = {x.get('id') for x in d.get('regression_fixtures') or []}
    miss = REQ_FIXTURES - fx
    if miss: fail(f"missing fixtures: {sorted(miss)}")
    print("PASS v94_engine_regression_fixtures")

if __name__ == '__main__': main()
