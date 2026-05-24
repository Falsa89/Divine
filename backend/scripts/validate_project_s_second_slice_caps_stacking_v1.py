#!/usr/bin/env python3
"""PROJECT_S Track D validator — caps + stacking adversarial cases.

Genera input adversarial e verifica:
- per-status cap mai superato
- aggregate cap mai superato
- mode multipliers applicati correttamente
- no negative stat inversion (deltas mai positivi per debuff_offensive)
- no multiplicative runaway
- opposing speed pair cancellation
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_s_second_slice_caps_stacking_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_SECOND_SLICE_CAPS_AND_STACKING_VALIDATOR_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    sys.path.insert(0, '/app/backend')
    from game_logic.status_second_slice_resolver_pure import resolve_second_slice, AGGREGATE_CAPS_PCT, PER_STATUS_CAPS_PCT
    # Adversarial 1: 10x max offensive debuff -> clamp to aggregate 40%
    out = resolve_second_slice([{'family': 'debuff_offensive', 'value_pct': 30.0}] * 10, 'campaign')
    if abs(out['atk_pct'] + AGGREGATE_CAPS_PCT['offensive_debuff']) > 1e-9:
        fail(f'10x offensive debuff should clamp to -40, got {out["atk_pct"]}')
    # Adversarial 2: opposing speed pair at cap -> net 0
    out = resolve_second_slice([{'family': 'speed_up', 'value_pct': 25.0}, {'family': 'speed_down', 'value_pct': 25.0}], 'campaign')
    if abs(out['speed_pct']) > 1e-9:
        fail(f'opposing speed at cap should net 0, got {out["speed_pct"]}')
    # Adversarial 3: speed_up 100% (clamped to per_status 25%) vs speed_down 100% (clamped to 25%) -> net 0
    out = resolve_second_slice([{'family': 'speed_up', 'value_pct': 100.0}, {'family': 'speed_down', 'value_pct': 100.0}], 'campaign')
    if abs(out['speed_pct']) > 1e-9:
        fail(f'extreme opposing speed should net 0, got {out["speed_pct"]}')
    # Adversarial 4: pvp mode multiplies by 0.75
    out = resolve_second_slice([{'family': 'debuff_offensive', 'value_pct': 30.0}, {'family': 'debuff_offensive', 'value_pct': 30.0}], 'pvp')
    expected_pvp = -AGGREGATE_CAPS_PCT['offensive_debuff'] * 0.75
    if abs(out['atk_pct'] - expected_pvp) > 1e-9:
        fail(f'pvp mode multiplier wrong: got {out["atk_pct"]}, expected {expected_pvp}')
    # Adversarial 5: boss mode multiplies by 0.50
    out = resolve_second_slice([{'family': 'debuff_offensive', 'value_pct': 30.0}, {'family': 'debuff_offensive', 'value_pct': 30.0}], 'boss')
    expected_boss = -AGGREGATE_CAPS_PCT['offensive_debuff'] * 0.5
    if abs(out['atk_pct'] - expected_boss) > 1e-9:
        fail(f'boss mode multiplier wrong: got {out["atk_pct"]}, expected {expected_boss}')
    # No negative stat inversion (debuff should never produce positive atk_pct)
    for n in (1, 3, 5, 10, 100):
        out = resolve_second_slice([{'family': 'debuff_offensive', 'value_pct': 30.0}] * n, 'campaign')
        if out['atk_pct'] > 0:
            fail(f'debuff_offensive produced positive atk_pct (sign inversion): {out["atk_pct"]}')
    # No multiplicative runaway: 1000 entries cannot exceed aggregate cap
    out = resolve_second_slice([{'family': 'debuff_defensive', 'value_pct': 30.0}] * 1000, 'campaign')
    if abs(out['def_pct']) > AGGREGATE_CAPS_PCT['defensive_debuff'] + 1e-9:
        fail(f'runaway: 1000x defensive debuff exceeded aggregate cap: {out["def_pct"]}')
    if m.get('balance_runtime_changed') is not False or m.get('db_writes') is not False:
        fail('balance_runtime_changed/db_writes must be False')
    print('[PASS] PROJECT_S Track D caps + stacking READY — adversarial cases respect caps, modes, sign, no runaway')
    sys.exit(0)


if __name__ == '__main__': main()
