#!/usr/bin/env python3
"""PROJECT_R Track B validator — balance and caps.

Verifica per-status caps, aggregate caps, mode multipliers, stacking + decay policy,
opposing pairs cancellation. Nessun formula/runtime change.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_r_status_second_slice_balance_caps_v1.json')
FAMILIES = ('debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_STATUS_SECOND_SLICE_BALANCE_AND_CAPS_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('design_only') is not True or m.get('runtime_activated') is not False:
        fail('must be design_only and not runtime_activated')
    caps = m.get('per_status_caps_pct') or {}
    for fam in FAMILIES:
        if fam not in caps:
            fail(f'per_status_caps_pct missing family: {fam}')
        c = caps[fam]
        if not (0 < c.get('min_pct', -1) <= c.get('default_pct', -1) <= c.get('max_pct', -1)):
            fail(f'{fam}: min_pct <= default_pct <= max_pct violated')
    agg = m.get('aggregate_caps_pct') or {}
    for k in ('aggregate_offensive_debuff_cap_pct', 'aggregate_defensive_debuff_cap_pct', 'aggregate_speed_cap_pct'):
        if k not in agg or agg[k] <= 0:
            fail(f'aggregate caps missing or non-positive: {k}')
    mc = m.get('mode_caps') or {}
    if mc.get('pvp_stricter_cap_pct_multiplier', 1.0) > 0.75:
        fail('pvp_stricter_cap_pct_multiplier must be <= 0.75')
    if mc.get('boss_endgame_guard_cap_pct_multiplier', 1.0) > 0.50:
        fail('boss_endgame_guard_cap_pct_multiplier must be <= 0.50')
    stk = m.get('stacking_policy') or {}
    if int(stk.get('max_simultaneous_active_statuses_per_unit', 0)) > 4:
        fail('max_simultaneous_active_statuses_per_unit must be <= 4')
    if not stk.get('opposing_pairs_cancel'):
        fail('opposing_pairs_cancel missing')
    dd = m.get('decay_duration_policy') or {}
    if not (1 <= int(dd.get('min_duration_rounds', 0)) <= int(dd.get('default_duration_rounds', 0)) <= int(dd.get('max_duration_rounds', 0))):
        fail('duration policy ordering violated')
    if m.get('formula_changes') is not False or m.get('battle_engine_touched') is not False:
        fail('formula_changes/battle_engine_touched must be False')
    print('[PASS] PROJECT_R Track B balance + caps READY — per-status/aggregate/mode caps consistent, no formula change')
    sys.exit(0)


if __name__ == '__main__':
    main()
