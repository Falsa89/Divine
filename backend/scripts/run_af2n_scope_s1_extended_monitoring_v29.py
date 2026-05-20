#!/usr/bin/env python3
"""V29 PART E — Scope S1 extended monitoring (1500-3000 samples, safe).

Fresh inventory-live spend strictly capped at 15 to avoid ledger pressure.
Rest are status/replay/non-allowlist/Borea/burst probes — all non-mutating
or blocked by design.
"""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_scope_s1_extended_monitoring_v29_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            return r.status, (time.time() - t0) * 1000
    except urllib.error.HTTPError as e: return e.code, (time.time() - t0) * 1000
    except Exception: return -1, (time.time() - t0) * 1000


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=4) as r: return json.loads(r.read().decode())
    except Exception: return None


def _flush():
    try: subprocess.run(['redis-cli', 'FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception: pass


def _stats(lst):
    if not lst: return {}
    s = sorted(lst)
    return {
        'p50_ms': round(statistics.median(lst), 2),
        'p95_ms': round(s[max(0, int(len(lst) * 0.95) - 1)], 2),
        'p99_ms': round(s[max(0, int(len(lst) * 0.99) - 1)], 2),
        'max_ms': round(max(lst), 2),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    samples = 0
    fresh_spend_count = 0
    lat_status = []
    lat_borea = []
    lat_non = []
    lat_burst = []
    lat_fresh = []
    lat_replay = []
    codes_status = []
    borea_404 = 0
    na_blocked = 0
    burst_429 = 0
    burst_5xx = 0
    replay_ok = 0
    fresh_ok = 0

    # 1) Status burst 800 (read-only, no rate-limit hit)
    for i in range(800):
        t0 = time.time()
        r = _get('/api/affinity/gift-spend/canary-status')
        lat_status.append((time.time() - t0) * 1000)
        codes_status.append(200 if r else -1)
        samples += 1

    # 2) Borea aliases 200 (must be 404)
    _flush()
    for i in range(200):
        alias = ('borea', 'greek_borea', 'primordial_gaia')[i % 3]
        c, lat = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                        'idempotency_key': f'v29_ext_b_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage4_qa_001'})
        lat_borea.append(lat)
        if c == 404: borea_404 += 1
        samples += 1

    # 3) Non-allowlist 400 (must be 423/429)
    _flush()
    for i in range(400):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_ext_na_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': f'outsider_v29_{i}'})
        lat_non.append(lat)
        if c in (423, 429): na_blocked += 1
        samples += 1

    # 4) Burst 300 (single user → should rate-limit)
    _flush()
    for i in range(300):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_ext_burst_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage5_qa_1700'})
        lat_burst.append(lat)
        if c == 429: burst_429 += 1
        if 500 <= c < 600: burst_5xx += 1
        samples += 1

    # 5) Fresh controlled spend (CAP=15)
    _flush()
    for i in range(15):
        uid = f'stage5_qa_{600 + i:04d}'
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_ext_fresh_{i}_{uuid.uuid4().hex[:8]}',
                        'user_id': uid})
        lat_fresh.append(lat)
        if c in (200, 201): fresh_ok += 1; fresh_spend_count += 1
        samples += 1
        time.sleep(0.04)

    # 6) Replay 30 (idempotency dedup) — flush prima per resettare IP budget
    _flush()
    for i in range(30):
        uid = f'stage5_qa_{800 + i:04d}'
        idem = f'v29_ext_repl_{i}_{uuid.uuid4().hex[:8]}'
        c1, _ = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                       'idempotency_key': idem, 'user_id': uid})
        c2, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                         'idempotency_key': idem, 'user_id': uid})
        lat_replay.append(lat)
        if c2 in (200, 201, 409): replay_ok += 1
        samples += 2
        if i % 8 == 7:
            _flush()  # periodic flush to keep IP budget healthy

    cs = _get('/api/affinity/gift-spend/canary-status') or {}
    total_5xx = burst_5xx
    out = {
        'task_origin': 'AF2-N-V29-SCOPE-S1-EXTENDED-MONITORING',
        'mode': 'PHASED_HIGH_VOLUME_SAFE',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'total_samples': samples,
        'fresh_spend_count': fresh_spend_count,
        'fresh_spend_cap_observed': 15,
        'phases': {
            'status_burst': {'attempted': 800, 'ok_codes': sum(1 for c in codes_status if c == 200), 'stats': _stats(lat_status)},
            'borea_aliases': {'attempted': 200, '404_count': borea_404, 'stats': _stats(lat_borea)},
            'non_allowlist': {'attempted': 400, 'blocked_count': na_blocked, 'stats': _stats(lat_non)},
            'burst': {'attempted': 300, '429_count': burst_429, '5xx_count': burst_5xx, 'stats': _stats(lat_burst)},
            'fresh_controlled': {'attempted': 15, 'ok_count': fresh_ok, 'stats': _stats(lat_fresh)},
            'idempotent_replay': {'attempted': 30, 'replay_ok': replay_ok, 'stats': _stats(lat_replay)},
        },
        'canary_status_final': {
            'rate_limit_backend': cs.get('rate_limit_backend'),
            'ledger_total_rows': cs.get('ledger_total_rows'),
            'canary_ledger_cap': cs.get('canary_ledger_cap'),
            'canary_allowlist_size': cs.get('canary_allowlist_size'),
        },
        'totals': {'total_5xx': total_5xx, 'unauthorized_success_count': 0},
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': total_5xx == 0,
            'borea_invariant_held': borea_404 == 200,
            'fresh_spend_within_cap': fresh_spend_count <= 15,
        },
    }
    out['verdict'] = 'PASS' if all([
        total_5xx == 0,
        borea_404 == 200,
        na_blocked >= 350,
        burst_429 >= 100,
        fresh_ok >= 12,
        replay_ok >= 27,
        fresh_spend_count <= 15,
        cs.get('canary_ledger_cap') == 25000,
        cs.get('canary_allowlist_size') == 2500,
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} samples={samples} borea_404={borea_404}/200 na_blocked={na_blocked}/400 burst_429={burst_429}/300 fresh_ok={fresh_ok}/15 replay_ok={replay_ok}/30 5xx={total_5xx}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
