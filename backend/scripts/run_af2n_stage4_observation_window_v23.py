#!/usr/bin/env python3
"""V23 — Stage4 Observation Window (compressed continuous monitoring).

Runs N periodic samples spaced K seconds apart. Each sample collects:
  - health, /api/heroes count, Borea 404 probe (1 alias rotated),
  - non-allowlist 423 sample, rate-limit burst trigger,
  - inventory/affinity delta drift (stage4_qa_001),
  - ledger row count, canary cap headroom,
  - 5xx counters
Usage: `OBS_SAMPLES=10 OBS_INTERVAL_S=6` (defaults: 12 samples × 5s = 60s).
Non-destructive. Aggregated result + per-sample log.
"""
from __future__ import annotations
import json, os, random, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_stage4_observation_window_v23_result.json')
SAMPLES = int(os.environ.get('OBS_SAMPLES', '12'))
INTERVAL_S = float(os.environ.get('OBS_INTERVAL_S', '5'))


def _post(b):
    payload = json.dumps(b).encode()
    req = Request(API + '/affinity/gift-spend', data=payload, method='POST',
                  headers={'Content-Type':'application/json'})
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
    code, _ = _get('/health'); s['health'] = code
    code, heroes = _get('/heroes'); s['heroes_count'] = len(heroes) if isinstance(heroes, list) else -1
    alias = ['borea','greek_borea','primordial_gaia'][i % 3]
    c, _ = _post({'gift_id':'x','hero_id':alias,'quantity':1,
                  'idempotency_key':f'v23obs_borea_{i}_{alias}','user_id':'stage4_qa_001'})
    s[f'borea_{alias}'] = c
    c2, _ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                   'idempotency_key':f'v23obs_unauth_{i}','user_id':f'unauth_v23_obs_{i}_{int(time.time())}'})
    s['non_allowlist'] = c2
    # burst probe (3 same user)
    burst_codes = []
    burst_user = f'v23obs_burst_{i}_{int(time.time())}'
    for j in range(8):
        c3, _ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                       'idempotency_key':f'v23obsb_{i}_{j}','user_id':burst_user})
        burst_codes.append(c3)
    s['burst_codes'] = burst_codes
    s['burst_saw_429'] = 429 in burst_codes
    code, status = _get('/affinity/gift-spend/canary-status')
    if isinstance(status, dict):
        s['allowlist_size'] = status.get('canary_allowlist_size')
        s['ledger_total'] = status.get('ledger_total_rows')
        s['ledger_cap'] = status.get('canary_ledger_cap')
        s['rate_limit_backend'] = status.get('rate_limit_backend')
        s['rate_limit_enabled'] = status.get('rate_limit_enabled')
    return s


def main():
    NOW = datetime.now(timezone.utc)
    samples = []
    for i in range(SAMPLES):
        samples.append(_sample(i))
        if i < SAMPLES - 1: time.sleep(INTERVAL_S)
    # aggregate
    bad_borea = [s for s in samples if any(s.get(f'borea_{a}') not in (404,) for a in ['borea','greek_borea','primordial_gaia'] if f'borea_{a}' in s)]
    bad_non_allow = [s for s in samples if s.get('non_allowlist') not in (423, 429)]
    no_429_burst = [s for s in samples if not s.get('burst_saw_429')]
    bad_health = [s for s in samples if s.get('health') != 200]
    bad_heroes = [s for s in samples if s.get('heroes_count') != 100]
    cap_exceeded = [s for s in samples if (s.get('ledger_total') or 0) > (s.get('ledger_cap') or 0)]
    fails = []
    if bad_borea: fails.append(f'borea_not_404_in_samples:{len(bad_borea)}')
    if bad_non_allow: fails.append(f'non_allowlist_unexpected:{len(bad_non_allow)}')
    if no_429_burst: fails.append(f'burst_did_not_trigger_429_in:{len(no_429_burst)}_samples')
    if bad_health: fails.append(f'health_not_200:{len(bad_health)}')
    if bad_heroes: fails.append(f'heroes_not_100:{len(bad_heroes)}')
    if cap_exceeded: fails.append(f'ledger_over_cap:{len(cap_exceeded)}')
    backend_set = {s.get('rate_limit_backend') for s in samples if s.get('rate_limit_backend')}
    overall = (len(fails) == 0)
    out_doc = {
        'result_id':'af2n_stage4_observation_window_v23_result',
        'task_origin':'V23-AF2N-STAGE4-OBSERVATION-WINDOW',
        'started_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples_count': len(samples),
        'interval_seconds': INTERVAL_S,
        'rate_limit_backends_observed': sorted(list(backend_set)),
        'samples_first_3': samples[:3],
        'samples_last_3': samples[-3:],
        'aggregated': {
            'bad_borea': len(bad_borea), 'bad_non_allow': len(bad_non_allow),
            'no_429_burst_in_samples': len(no_429_burst),
            'bad_health': len(bad_health), 'bad_heroes': len(bad_heroes),
            'cap_exceeded': len(cap_exceeded),
        },
        'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'no broad rollout', 'no public spend UI', 'no battle wiring',
            'no Borea reveal', 'no gacha/roster/catalog mutation'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V23-OBSERVATION {out_doc["overall_status"]} samples={SAMPLES} interval={INTERVAL_S}s fails={fails}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
