#!/usr/bin/env python3
"""PROJECT_N Track C validator — canary flag ON behavior smoke (re-runs with flag ON in-process)."""
import copy, hashlib, importlib.util, json, os, random, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_canary_flag_on_behavior_smoke_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
FORBIDDEN_SEAM_KEYWORDS = ('apply_dot', 'damage_over_time', 'heal_over_time', 'tick_loop')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _make_char(i):
    return {'id': f'c{i}', 'name': f'Hero{i}', 'rarity': 3, 'attack': 100+i, 'defense': 50+i, 'hp': 1000+i*10, 'max_hp': 1000+i*10,
            'speed': 100, 'magic_attack': 80, 'magic_defense': 50, 'critical_rate': 0.1, 'critical_damage': 1.5,
            'physical_damage': 0, 'physical_defense': 0, 'magic_damage': 0, 'healing': 0, 'crit_damage': 0, 'crit_rate': 0,
            'element': 'fire', 'faction': 'norse', 'position': {'row': 0, 'col': i%3}, 'skills': {}}


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_CANARY_FLAG_ON_BEHAVIOR_SMOKE_READY': fail('verdict mismatch')
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    try:
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        # B1-B6: in-process behavior smoke (mirror Track D fixtures from Pack M)
        cases = [
            ('B1', 'buff_offensive', 'atk_pct', 0.10, 'atk_pct', 0.10),
            ('B2', 'buff_offensive', 'crit_pct', 0.05, 'crit_pct', 0.05),
            ('B3', 'buff_defensive', 'def_pct', 0.10, 'def_pct', 0.10),
            ('B4', 'buff_defensive', 'hp_pct', 0.15, 'hp_pct', 0.15),
        ]
        for cid, cat, stat, val, key, exp in cases:
            out = mod.apply_prefight_status_slice_preview({}, [{'category': cat, 'stat': stat, 'value': val}], dry_run=True)
            env = out.get('status_envelope_preview', {})
            if abs(env.get(key, 0.0) - exp) > 1e-9: fail(f'{cid} {key} expected {exp} got {env.get(key)}')
        # B5: out-of-slice
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'debuff', 'stat': 'atk_pct', 'value': 0.5}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if any(env.get(k, -1.0) != 0.0 for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct')): fail('B5 out-of-slice must yield zero envelope')
        # B6: cap clamp
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.99}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('atk_pct', 0.0) - 0.30) > 1e-9: fail(f'B6 cap clamp expected 0.30 got {env.get("atk_pct")}')
        # B7: seam source has NO DoT/tick keywords
        seam_txt = SEAM.read_text(encoding='utf-8', errors='ignore')
        for kw in FORBIDDEN_SEAM_KEYWORDS:
            if kw in seam_txt: fail(f'B7 seam contains forbidden keyword: {kw}')
        # Battle byte-identical even with flag ON in-process (live call site uses dry_run=False).
        sys.path.insert(0, '/app/backend')
        for k in list(sys.modules):
            if k.startswith('battle_engine') or k.startswith('game_logic'):
                del sys.modules[k]
        import battle_engine as be
        random.seed(42)
        ta = [_make_char(i) for i in range(3)]
        tb = [_make_char(i+10) for i in range(3)]
        r = be.simulate_battle(ta, tb, max_turns=5)
        sb = json.dumps({'winner': r.get('winner'), 'turns': r.get('total_turns', r.get('turns')),
                         'final_hp_a': sorted([(c.get('id'), c.get('current_hp', 0)) for c in ta]),
                         'final_hp_b': sorted([(c.get('id'), c.get('current_hp', 0)) for c in tb])}, sort_keys=True)
        sha = hashlib.sha256(sb.encode()).hexdigest()
        if sha != 'd951767a72b54b339eb660f6308d72c943a9a9e318539f639ce9fc7f416d3725':
            fail(f'battle behavior changed with flag ON in-process; sha={sha}')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    print('[PASS] PROJECT_N Track C flag ON behavior smoke READY: B1-B7 PASS; battle byte-identical with flag ON')
    sys.exit(0)


if __name__ == '__main__': main()
