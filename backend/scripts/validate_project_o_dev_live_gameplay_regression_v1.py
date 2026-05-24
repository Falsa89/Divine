#!/usr/bin/env python3
"""PROJECT_O Track C validator — dev-live gameplay regression + SHA guard."""
import hashlib, json, os, random, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_dev_live_gameplay_regression_v1.json')
sys.path.insert(0, '/app/backend')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def _mc(i): return {'id':f'c{i}','name':f'H{i}','rarity':3,'attack':100+i,'defense':50+i,'hp':1000+i*10,'max_hp':1000+i*10,'speed':100,'magic_attack':80,'magic_defense':50,'critical_rate':0.1,'critical_damage':1.5,'physical_damage':0,'physical_defense':0,'magic_damage':0,'healing':0,'crit_damage':0,'crit_rate':0,'element':'fire','faction':'norse','position':{'row':0,'col':i%3},'skills':{}}


def _run():
    for k in list(sys.modules):
        if k.startswith('battle_engine') or k.startswith('game_logic'): del sys.modules[k]
    import battle_engine as be
    random.seed(42)
    ta = [_mc(i) for i in range(3)]; tb = [_mc(i+10) for i in range(3)]
    r = be.simulate_battle(ta, tb, max_turns=5)
    sb = json.dumps({'winner': r.get('winner'), 'turns': r.get('total_turns', r.get('turns')), 'final_hp_a': sorted([(c.get('id'), c.get('current_hp', 0)) for c in ta]), 'final_hp_b': sorted([(c.get('id'), c.get('current_hp', 0)) for c in tb])}, sort_keys=True)
    return hashlib.sha256(sb.encode()).hexdigest()


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_DEV_LIVE_GAMEPLAY_REGRESSION_AND_SHA_GUARD_READY': fail('verdict mismatch')
    baseline = m.get('baseline_sha256')
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    try:
        os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        sha_off = _run()
        if sha_off != baseline: fail(f'flag OFF sha {sha_off} != baseline {baseline}')
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        sha_on = _run()
        if sha_on != baseline: fail(f'flag ON sha {sha_on} != baseline {baseline}')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    print(f'[PASS] PROJECT_O Track C SHA guard READY: flag OFF == flag ON == baseline (sha {baseline[:16]}…)')
    sys.exit(0)


if __name__ == '__main__': main()
