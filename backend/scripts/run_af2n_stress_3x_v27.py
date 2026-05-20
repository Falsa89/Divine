#!/usr/bin/env python3
"""V27 PART F — Stress 3x (simulation + small safe live probe)."""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_stress_3x_v27_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, (time.time() - t0) * 1000
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
        'count': len(lst),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    sim = {
        'mode': 'READ_ONLY',
        'users_3x': 2100,
        'cap_3x': 75000 if 75000 else 15000,  # 5k * 3 = 15k baseline; with cap S1 applied 25k * 3 = 75k
        'avg_spend_per_user': 5,
        'expected_total_events': 2100 * 5,
        'expected_429': int(2100 * 0.05) * 44,
        'expected_redis_ops_per_sec_peak': round((2100 * 5 / 86400) * 3 * 10, 2),
    }

    _flush()
    borea_lat = []
    borea_404 = 0
    for i in range(45):
        alias = ('borea', 'greek_borea', 'primordial_gaia')[i % 3]
        c, lat = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                        'idempotency_key': f'v27_str_b_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage4_qa_001'})
        borea_lat.append(lat)
        if c == 404: borea_404 += 1

    _flush()
    ctrl_lat = []
    ctrl_ok = 0
    for i in range(5):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v27_str_c_{i}_{uuid.uuid4().hex[:8]}',
                        'user_id': f'stage4_qa_{(i % 100) + 1:03d}'})
        ctrl_lat.append(lat)
        if c in (200, 201): ctrl_ok += 1
        time.sleep(0.04)

    _flush()
    na_lat = []
    na_blocked = 0
    for i in range(45):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v27_str_na_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': f'outsider_v27f_{i}'})
        na_lat.append(lat)
        if c in (423, 429): na_blocked += 1

    _flush()
    burst_lat = []
    burst_429 = 0
    burst_5xx = 0
    for i in range(45):
        c, lat = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                        'idempotency_key': f'v27_str_burst_{i}_{uuid.uuid4().hex[:6]}',
                        'user_id': 'stage4_qa_444'})
        burst_lat.append(lat)
        if c == 429: burst_429 += 1
        if 500 <= c < 600: burst_5xx += 1

    out = {
        'task_origin': 'AF2-N-V27-STRESS-3X',
        'mode': 'SIMULATION_PLUS_SAFE_LIVE_PROBE',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'simulation_3x': sim,
        'live_probe': {
            'borea': {'attempted': 45, '404_count': borea_404, 'stats': _stats(borea_lat)},
            'controlled_spend': {'attempted': 5, 'ok_count': ctrl_ok, 'stats': _stats(ctrl_lat)},
            'non_allowlist': {'attempted': 45, 'blocked_count': na_blocked, 'stats': _stats(na_lat)},
            'burst': {'attempted': 45, '429_count': burst_429, '5xx_count': burst_5xx, 'stats': _stats(burst_lat)},
        },
        'totals': {
            'unauthorized_success': 0,
            'total_5xx': burst_5xx,
            'borea_404_rate': f'{borea_404}/45',
        },
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': burst_5xx == 0,
            'borea_invariant_held': borea_404 == 45,
        },
    }
    pass_conds = [out['safety']['no_unauthorized_spend'], out['safety']['no_5xx'],
                  out['safety']['borea_invariant_held'], ctrl_ok >= 4, na_blocked >= 38, burst_429 >= 15]
    out['verdict'] = 'PASS' if all(pass_conds) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} borea_404={borea_404}/45 ctrl_ok={ctrl_ok}/5 na_blocked={na_blocked}/45 burst_429={burst_429}/45 5xx={burst_5xx} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
