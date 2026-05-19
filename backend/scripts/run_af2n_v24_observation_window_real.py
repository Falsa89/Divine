#!/usr/bin/env python3
"""V24 — Real Observation Window (longer, with abuse metric snapshot if enabled).

Default: OBS_SAMPLES=20, OBS_INTERVAL_S=4 (≈80s window).
Aggregated drift checks: heroes count drift, ledger growth rate, 5xx zero,
borea 404 across all alias on every sample, rate-limit 429 trigger on burst,
rate_limit_backend stable.
"""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v24_observation_window_real_result.json')
SAMPLES = int(os.environ.get('OBS_SAMPLES','20'))
INTERVAL_S = float(os.environ.get('OBS_INTERVAL_S','4'))


def _post(b):
    payload = json.dumps(b).encode()
    req = Request(API + '/affinity/gift-spend', data=payload, method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=4) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = None
        return e.code, body
    except URLError: return -1, None


def _get(p):
    try:
        with urlopen(API + p, timeout=4) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _sample(i):
    s = {'i': i, 't_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
    hc, _ = _get('/health'); s['health'] = hc
    _, heroes = _get('/heroes'); s['heroes_count'] = len(heroes) if isinstance(heroes, list) else -1
    # rotate all 3 borea aliases each sample
    borea_results = {}
    for alias in ('borea','greek_borea','primordial_gaia'):
        c,_ = _post({'gift_id':'x','hero_id':alias,'quantity':1,
                     'idempotency_key':f'v24obs_borea_{i}_{alias}_{int(time.time()*1000)}',
                     'user_id':'stage4_qa_001'})
        borea_results[alias] = c
    s['borea_results'] = borea_results
    s['all_borea_404'] = all(c == 404 for c in borea_results.values())
    c2,_ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                  'idempotency_key':f'v24obs_unauth_{i}_{int(time.time()*1000)}',
                  'user_id':f'unauth_v24_obs_{i}_{int(time.time())}'})
    s['non_allowlist'] = c2
    # burst probe
    burst_user = f'v24obs_burst_{i}_{int(time.time())}'
    burst_codes = []
    for j in range(8):
        c3,_ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                      'idempotency_key':f'v24obsb_{i}_{j}','user_id':burst_user})
        burst_codes.append(c3)
    s['burst_codes'] = burst_codes
    s['burst_saw_429'] = 429 in burst_codes
    code, status = _get('/affinity/gift-spend/canary-status')
    if isinstance(status, dict):
        s['allowlist_size'] = status.get('canary_allowlist_size')
        s['ledger_total'] = status.get('ledger_total_rows')
        s['ledger_cap'] = status.get('canary_ledger_cap')
        s['rate_limit_backend'] = status.get('rate_limit_backend')
    return s


def main():
    NOW = datetime.now(timezone.utc)
    samples = []
    for i in range(SAMPLES):
        samples.append(_sample(i))
        if i < SAMPLES-1: time.sleep(INTERVAL_S)
    bad_borea = [s for s in samples if not s.get('all_borea_404')]
    bad_non_allow = [s for s in samples if s.get('non_allowlist') not in (423, 429)]
    no_429 = [s for s in samples if not s.get('burst_saw_429')]
    bad_health = [s for s in samples if s.get('health') != 200]
    bad_heroes = [s for s in samples if s.get('heroes_count') != 100]
    cap_exc = [s for s in samples if (s.get('ledger_total') or 0) > (s.get('ledger_cap') or 0)]
    backends = sorted({s.get('rate_limit_backend') for s in samples if s.get('rate_limit_backend')})
    backend_stable = len(backends) == 1
    fails = []
    if bad_borea: fails.append(f'borea_not_404:{len(bad_borea)}')
    if bad_non_allow: fails.append(f'non_allow_bad:{len(bad_non_allow)}')
    if no_429: fails.append(f'no_burst_429:{len(no_429)}')
    if bad_health: fails.append(f'bad_health:{len(bad_health)}')
    if bad_heroes: fails.append(f'bad_heroes:{len(bad_heroes)}')
    if cap_exc: fails.append(f'cap_exceeded:{len(cap_exc)}')
    if not backend_stable: fails.append(f'backend_drifted:{backends}')
    overall = (len(fails) == 0)
    # ledger growth across window
    if samples:
        start_ledger = samples[0].get('ledger_total') or 0
        end_ledger = samples[-1].get('ledger_total') or 0
        ledger_growth = end_ledger - start_ledger
    else:
        ledger_growth = 0
    out_doc = {
        'result_id':'af2n_v24_observation_window_real_result',
        'task_origin':'V24-AF2N-OBSERVATION-WINDOW-REAL',
        'started_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples_count': len(samples),
        'interval_seconds': INTERVAL_S,
        'window_seconds_approx': SAMPLES * INTERVAL_S,
        'rate_limit_backends_observed': backends,
        'backend_stable': backend_stable,
        'ledger_growth_during_window': ledger_growth,
        'samples_first_2': samples[:2],
        'samples_last_2': samples[-2:],
        'aggregated': {
            'bad_borea': len(bad_borea), 'bad_non_allow': len(bad_non_allow),
            'no_burst_429': len(no_429), 'bad_health': len(bad_health),
            'bad_heroes': len(bad_heroes), 'cap_exceeded': len(cap_exc),
        },
        'fails': fails,
        'overall_status':'PASS' if overall else 'FAIL',
        'safety_invariants':[
            'no broad rollout','no public spend UI','no battle wiring',
            'no Borea reveal','no gacha/roster/catalog mutation'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V24-OBSERVATION-REAL {out_doc["overall_status"]} samples={SAMPLES} interval={INTERVAL_S}s growth={ledger_growth} backend={backends}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
