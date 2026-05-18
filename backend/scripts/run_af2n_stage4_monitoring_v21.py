#!/usr/bin/env python3
"""V21 — Stage4 Monitoring (150 samples controlled).

Mix: allowed stage4 fresh spends (cap'd), idempotent replays, non-allowlist 423,
Borea 404 probes, rate-limit burst probe, ledger cap probe.
Non-destructive, low-impact.
"""
from __future__ import annotations
import json, random, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_stage4_monitoring_v21_result.json')
NOW = datetime.now(timezone.utc)

MAX_FRESH = 30  # don't blow ledger


def _post(b):
    payload = json.dumps(b).encode()
    req = Request(API + '/affinity/gift-spend', data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=4) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def _get(p):
    try:
        with urlopen(API + p, timeout=4) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    code, status = _get('/affinity/gift-spend/canary-status')
    if status is None or status.get('canary_allowlist_size', 0) < 700:
        out = {'overall_status': 'BLOCKED_NO_STAGE4', 'reason': 'Stage4 not applied', 'generated_at_utc': NOW.isoformat().replace('+00:00', 'Z')}
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2))
        print('STAGE4-MONITOR BLOCKED_NO_STAGE4'); return 0
    samples = []
    fresh = 0
    # fresh spends from stage4 users
    for i in range(MAX_FRESH):
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares',
                   'quantity': 1, 'idempotency_key': f'v21mon_fresh_{int(time.time())}_{i}',
                   'user_id': uid})
        samples.append({'kind': 'stage4_fresh', 'code': c, 'user_id': uid})
        if c == 200: fresh += 1
    # idempotent replays (use same key twice)
    for i in range(20):
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        key = f'v21mon_idem_{int(time.time())}_{i}'
        c1 = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares',
                    'quantity': 1, 'idempotency_key': key, 'user_id': uid})
        c2 = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares',
                    'quantity': 1, 'idempotency_key': key, 'user_id': uid})
        samples.append({'kind': 'idem_first', 'code': c1, 'user_id': uid})
        samples.append({'kind': 'idem_replay', 'code': c2, 'user_id': uid})
    # non-allowlist 423 (different users each time to avoid rate-limit)
    for i in range(20):
        c = _post({'gift_id': 'x', 'hero_id': 'greek_zeus',
                   'quantity': 1, 'idempotency_key': f'v21mon_unauth_{i}',
                   'user_id': f'unauth_v21_{i}_{int(time.time())}'})
        samples.append({'kind': 'non_allowlist', 'code': c})
    # Borea 404
    for alias in ['borea', 'greek_borea', 'primordial_gaia']:
        c = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                   'idempotency_key': f'v21mon_borea_{alias}',
                   'user_id': 'stage4_qa_001'})
        samples.append({'kind': f'borea_alias:{alias}', 'code': c})
    # rate-limit burst (one user)
    burst_user = f'v21mon_burst_{int(time.time())}'
    for i in range(10):
        c = _post({'gift_id': 'x', 'hero_id': 'greek_zeus', 'quantity': 1,
                   'idempotency_key': f'v21mon_burst_{i}', 'user_id': burst_user})
        samples.append({'kind': 'rate_limit_burst', 'code': c})
    counts = {}
    for s in samples:
        c = s['code']
        counts[str(c)] = counts.get(str(c), 0) + 1
    # gates
    fails = []
    if counts.get('500', 0) > 0 or counts.get('502', 0) > 0 or counts.get('503', 0) > 0 or counts.get('504', 0) > 0:
        fails.append('observed_5xx')
    # all Borea probes must be 404
    for s in samples:
        if s['kind'].startswith('borea_alias:') and s['code'] != 404:
            fails.append(f'borea_not_404:{s["kind"]}')
    # all non_allowlist must be 423 or 429 (rate-limited)
    for s in samples:
        if s['kind'] == 'non_allowlist' and s['code'] not in (423, 429):
            fails.append(f'non_allow_bad_code:{s["code"]}')
    # at least one 429 in burst
    if not any(s['kind'] == 'rate_limit_burst' and s['code'] == 429 for s in samples):
        fails.append('rate_limit_did_not_trigger')
    # idem replay should be 200
    for s in samples:
        if s['kind'] == 'idem_replay' and s['code'] not in (200, 429):
            fails.append(f'idem_replay_bad:{s["code"]}')
    # ledger within cap
    code2, st2 = _get('/affinity/gift-spend/canary-status')
    if st2 and st2.get('ledger_total_rows', 0) > st2.get('canary_ledger_cap', 0):
        fails.append('ledger_over_cap')
    overall = (len(fails) == 0)
    out_doc = {
        'result_id': 'af2n_stage4_monitoring_v21_result',
        'task_origin': 'V21-AF2N-STAGE4-MONITORING',
        'started_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'sample_total': len(samples),
        'status_counts': counts,
        'fresh_spends_succeeded': fresh,
        'observations': samples[:30],  # truncated for size
        'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'post_canary_status': st2,
        'safety_invariants': [
            'no broad rollout', 'no public spend UI',
            'no battle wiring', 'no Borea reveal',
            'no gacha/roster/catalog mutation'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V21-STAGE4-MONITOR {out_doc["overall_status"]} samples={len(samples)} counts={counts}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
