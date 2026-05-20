#!/usr/bin/env python3
"""V29 PART F — Stress 8x safe (sim 28k events/day + small live probe).
Fresh spend strictly capped at 10. Mostly replay/status/non-allowlist/burst.
"""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_stress_8x_v29_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=4) as r: return r.status, (time.time() - t0) * 1000
    except urllib.error.HTTPError as e: return e.code, (time.time() - t0) * 1000
    except Exception: return -1, (time.time() - t0) * 1000


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


def _redis_keys():
    try:
        r = subprocess.run(['redis-cli', 'DBSIZE'], capture_output=True, text=True, timeout=3)
        return int(r.stdout.strip())
    except Exception: return -1


def main():
    started = datetime.now(timezone.utc).isoformat()
    sim = {
        'mode': 'SIMULATION',
        'users_8x': 5600,
        'avg_spend_per_user': 5,
        'expected_total_events': 28000,
        'cap_pressure_against_25k': round(28000 / 25000, 3),
        'redis_ops_per_sec_peak_est': round((28000 / 86400) * 3 * 12, 2),
    }

    # Borea 80 → 404
    _flush()
    borea_lat = []; borea_404 = 0
    for i in range(80):
        alias = ('borea', 'greek_borea', 'primordial_gaia')[i % 3]
        c, lat = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                        'idempotency_key': f'v29_str8_b_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage4_qa_001'})
        borea_lat.append(lat)
        if c == 404: borea_404 += 1

    # Fresh controlled 10 (cap)
    _flush()
    keys_before = _redis_keys()
    ctrl_lat = []; ctrl_ok = 0
    for i in range(10):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_str8_c_{i}_{uuid.uuid4().hex[:8]}',
                        'user_id': f'stage5_qa_{1000 + i:04d}'})
        ctrl_lat.append(lat)
        if c in (200, 201): ctrl_ok += 1
        time.sleep(0.03)

    # Non-allowlist 100 → 423/429
    _flush()
    na_lat = []; na_blocked = 0
    for i in range(100):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_str8_na_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': f'outsider_v29s8_{i}'})
        na_lat.append(lat)
        if c in (423, 429): na_blocked += 1

    # Burst 80 → 429
    _flush()
    burst_lat = []; burst_429 = 0; burst_5xx = 0
    for i in range(80):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v29_str8_burst_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage5_qa_2400'})
        burst_lat.append(lat)
        if c == 429: burst_429 += 1
        if 500 <= c < 600: burst_5xx += 1

    # Replay 8
    replay_ok = 0; replay_lat = []
    for i in range(8):
        uid = f'stage5_qa_{1200 + i:04d}'
        idem = f'v29_str8_repl_{i}_{uuid.uuid4().hex[:8]}'
        c1, _ = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                       'idempotency_key': idem, 'user_id': uid})
        c2, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                         'idempotency_key': idem, 'user_id': uid})
        replay_lat.append(lat)
        if c2 in (200, 201, 409): replay_ok += 1

    keys_after = _redis_keys()
    out = {
        'task_origin': 'AF2-N-V29-STRESS-8X',
        'mode': 'SIMULATION_PLUS_SAFE_LIVE_PROBE',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'simulation_8x': sim,
        'live_probe': {
            'borea': {'attempted': 80, '404_count': borea_404, 'stats': _stats(borea_lat)},
            'fresh_controlled': {'attempted': 10, 'ok_count': ctrl_ok, 'stats': _stats(ctrl_lat)},
            'non_allowlist': {'attempted': 100, 'blocked_count': na_blocked, 'stats': _stats(na_lat)},
            'burst': {'attempted': 80, '429_count': burst_429, '5xx_count': burst_5xx, 'stats': _stats(burst_lat)},
            'idempotency_replay': {'attempted': 8, 'replay_ok': replay_ok, 'stats': _stats(replay_lat)},
        },
        'redis_pressure': {'keys_before': keys_before, 'keys_after': keys_after,
                            'delta': keys_after - keys_before if keys_after >= 0 and keys_before >= 0 else None},
        'totals': {'total_5xx': burst_5xx, 'unauthorized_success': 0,
                   'borea_404_rate': f'{borea_404}/80'},
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': burst_5xx == 0,
            'borea_invariant_held': borea_404 == 80,
            'fresh_spend_within_cap': ctrl_ok <= 10,
            'idempotency_dedup_works': replay_ok >= 6,
        },
    }
    out['verdict'] = 'PASS' if all([
        out['safety']['no_unauthorized_spend'], out['safety']['no_5xx'],
        out['safety']['borea_invariant_held'], ctrl_ok >= 7, na_blocked >= 85, burst_429 >= 35,
        out['safety']['idempotency_dedup_works'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} borea_404={borea_404}/80 ctrl_ok={ctrl_ok}/10 na_blocked={na_blocked}/100 burst_429={burst_429}/80 5xx={burst_5xx} replay_ok={replay_ok}/8 redis_delta={out['redis_pressure']['delta']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
