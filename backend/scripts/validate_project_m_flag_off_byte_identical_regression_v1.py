#!/usr/bin/env python3
"""PROJECT_M Track C validator — flag OFF byte-identical regression guard."""
import copy, hashlib, json, os, random, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_m_flag_off_byte_identical_regression_v1.json')
sys.path.insert(0, '/app/backend')


def fail(msg): print(f'[FAIL] {msg}'); sys.exit(1)


def _make_char(i):
    return {
        'id': f'c{i}', 'name': f'Hero{i}', 'rarity': 3,
        'attack': 100 + i, 'defense': 50 + i, 'hp': 1000 + i * 10, 'max_hp': 1000 + i * 10,
        'speed': 100, 'magic_attack': 80, 'magic_defense': 50,
        'critical_rate': 0.1, 'critical_damage': 1.5,
        'physical_damage': 0, 'physical_defense': 0,
        'magic_damage': 0, 'healing': 0, 'crit_damage': 0, 'crit_rate': 0,
        'element': 'fire', 'faction': 'norse',
        'position': {'row': 0, 'col': i % 3},
        'skills': {},
    }


def _stable(team_a, team_b, result):
    out = {'winner': result.get('winner'), 'turns': result.get('total_turns', result.get('turns'))}
    out['final_hp_a'] = sorted([(c.get('id'), c.get('current_hp', 0)) for c in team_a])
    out['final_hp_b'] = sorted([(c.get('id'), c.get('current_hp', 0)) for c in team_b])
    return out


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_FLAG_OFF_BYTE_IDENTICAL_REGRESSION_GUARD_READY': fail('verdict mismatch')
    if m.get('byte_identical') is not True: fail('marker claims byte_identical False')
    if os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED', '').strip().lower() == 'true':
        fail('flag must be OFF for regression guard')
    # Force a clean import of battle_engine.
    for k in list(sys.modules):
        if k.startswith('battle_engine') or k.startswith('game_logic'):
            del sys.modules[k]
    import battle_engine as be  # noqa: WPS433
    random.seed(42)
    team_a = [_make_char(i) for i in range(3)]
    team_b = [_make_char(i + 10) for i in range(3)]
    result = be.simulate_battle(team_a, team_b, max_turns=5)
    sb = json.dumps(_stable(team_a, team_b, result), sort_keys=True)
    cur_sha = hashlib.sha256(sb.encode()).hexdigest()
    exp_sha = m.get('baseline_sha256')
    if cur_sha != exp_sha: fail(f'regression baseline mismatch: expected {exp_sha} got {cur_sha}')
    print(f'[PASS] PROJECT_M Track C flag OFF byte-identical regression: sha256={cur_sha[:16]}...')
    sys.exit(0)


if __name__ == '__main__': main()
