#!/usr/bin/env python3
"""v94 — Battle report extensions validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(ROOT, 'data', 'design', 'battle_engine', 'v94_engine_regression_fixture_matrix_v1.json')
REQ = {'dot_damage_done', 'status_applied_count', 'healing_done', 'cleanse_count',
       'status_prevented_by_immunity_count', 'taunt_redirect_count'}
REQ_NOT_BROKEN = {'PostBattleSummary', 'total_damage_done', 'team_a_final', 'team_b_final'}

def fail(m): print(f"FAIL v94_battle_report_extensions: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(F): fail(f"missing: {F}")
    with open(F) as f: d = json.load(f)
    ext = d.get('battle_report_extension') or {}
    fields = set(ext.get('fields') or [])
    miss = REQ - fields
    if miss: fail(f"missing report fields: {sorted(miss)}")
    not_broken = set(ext.get('does_not_break') or [])
    if not REQ_NOT_BROKEN.issubset(not_broken): fail(f"missing does_not_break declarations: {sorted(REQ_NOT_BROKEN - not_broken)}")
    print("PASS v94_battle_report_extensions")

if __name__ == '__main__': main()
