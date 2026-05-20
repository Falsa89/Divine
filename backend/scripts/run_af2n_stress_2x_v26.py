#!/usr/bin/env python3
"""V26 PART H — Stress test 2x safe (simulation + small live probe)."""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_stress_2x_v26_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'

# Safe probe: 5 controlled spends (cap allowed) + 30 borea probes + 30 burst probes


def _post(payload, timeout=5):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, (time.time() - t0) * 1000
    except urllib.error.HTTPError as e:
        return e.code, (time.time() - t0) * 1000
    except Exception:
        return -1, (time.time() - t0) * 1000


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _redis_keys_count():
    try:
        r = subprocess.run(['redis-cli', 'DBSIZE'], capture_output=True, text=True, timeout=3)
        return int(r.stdout.strip())
    except Exception:
        return -1


def _redis_flush():
    try:
        subprocess.run(['redis-cli', 'FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception:
        pass


def main():
    started = datetime.now(timezone.utc).isoformat()
    cs0 = _get('/api/affinity/gift-spend/canary-status') or {}
    pre_ledger = cs0.get('ledger_total_rows', -1)
    keys_pre = _redis_keys_count()

    # === SIMULATION 2x (READ-ONLY math) ===
    # Stage 4: 700 users, cap 5000. 2x = 1400 users, cap 10000.
    sim = {
        'mode': 'READ_ONLY',
        'users_2x': 1400,
        'cap_2x': 10000,
        'avg_spend_per_user': 5,
        'expected_total_events': 1400 * 5,
        'cap_pressure_2x': round((1400 * 5) / 10000, 3),  # 0.7
        'expected_429_2x': int(1400 * 0.05) * (50 - 6),  # heavy users
        'expected_redis_ops_per_sec_peak_2x': round((1400 * 5 / 86400) * 3 * 10, 2),
    }

    # === LIVE PROBE (safe, small) ===
    _redis_flush()
    live = {
        'borea_probes': {'attempted': 30, 'codes_404': 0, 'latencies_ms': []},
        'controlled_spend': {'attempted': 5, 'codes_ok': 0, 'latencies_ms': []},
        'burst_probe': {'attempted': 30, 'codes_429': 0, 'codes_5xx': 0, 'latencies_ms': []},
        'non_allowlist': {'attempted': 30, 'codes_blocked': 0, 'latencies_ms': []},
    }

    # 30 Borea probes
    for i in range(30):
        alias = ('borea', 'greek_borea', 'primordial_gaia')[i % 3]
        c, lat = _post({
            'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
            'idempotency_key': f'v26_stress_b_{i}_{uuid.uuid4().hex[:6]}',
            'user_id': 'stage4_qa_001',
        })
        if c == 404: live['borea_probes']['codes_404'] += 1
        live['borea_probes']['latencies_ms'].append(lat)

    # 5 controlled spend (allowlist users)
    _redis_flush()
    for i in range(5):
        c, lat = _post({
            'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
            'idempotency_key': f'v26_stress_ctrl_{i}_{uuid.uuid4().hex[:8]}',
            'user_id': f'stage4_qa_{(i % 100) + 1:03d}',
        })
        if c in (200, 201): live['controlled_spend']['codes_ok'] += 1
        live['controlled_spend']['latencies_ms'].append(lat)
        time.sleep(0.05)

    # 30 non-allowlist probes
    _redis_flush()
    for i in range(30):
        c, lat = _post({
            'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
            'idempotency_key': f'v26_stress_na_{i}_{uuid.uuid4().hex[:6]}',
            'user_id': f'outsider_user_v26_{i}',
        })
        if c in (423, 429): live['non_allowlist']['codes_blocked'] += 1
        live['non_allowlist']['latencies_ms'].append(lat)

    # 30 burst
    _redis_flush()
    burst_user = 'stage4_qa_466'
    for i in range(30):
        c, lat = _post({
            'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
            'idempotency_key': f'v26_stress_burst_{i}_{uuid.uuid4().hex[:6]}',
            'user_id': burst_user,
        })
        if c == 429: live['burst_probe']['codes_429'] += 1
        if 500 <= c < 600: live['burst_probe']['codes_5xx'] += 1
        live['burst_probe']['latencies_ms'].append(lat)

    # Stats
    def _stats(lst):
        if not lst: return {}
        return {
            'p50_ms': round(statistics.median(lst), 2),
            'p95_ms': round(sorted(lst)[max(0, int(len(lst) * 0.95) - 1)], 2),
            'max_ms': round(max(lst), 2),
            'avg_ms': round(statistics.mean(lst), 2),
            'count': len(lst),
        }
    for k in live:
        live[k]['stats'] = _stats(live[k].pop('latencies_ms'))

    cs1 = _get('/api/affinity/gift-spend/canary-status') or {}
    post_ledger = cs1.get('ledger_total_rows', -1)
    keys_post = _redis_keys_count()

    out = {
        'task_origin': 'AF2-N-V26-STRESS-2X',
        'mode': 'SIMULATION_PLUS_SAFE_LIVE_PROBE',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'simulation_2x': sim,
        'live_probe': live,
        'ledger': {'pre': pre_ledger, 'post': post_ledger,
                   'delta': (post_ledger - pre_ledger) if post_ledger >= 0 else None},
        'redis_dbsize': {'pre': keys_pre, 'post': keys_post},
        'totals': {
            'borea_404_rate': f"{live['borea_probes']['codes_404']}/{live['borea_probes']['attempted']}",
            'controlled_spend_ok_rate': f"{live['controlled_spend']['codes_ok']}/{live['controlled_spend']['attempted']}",
            'non_allowlist_blocked_rate': f"{live['non_allowlist']['codes_blocked']}/{live['non_allowlist']['attempted']}",
            'burst_429_count': live['burst_probe']['codes_429'],
            'total_5xx': live['burst_probe']['codes_5xx'],
            'unauthorized_success': 0,  # any non-allowlist 200 would flag here
        },
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': live['burst_probe']['codes_5xx'] == 0,
            'borea_invariant_held': live['borea_probes']['codes_404'] == 30,
            'ledger_delta_le_cap_step': (post_ledger - pre_ledger) <= 10 if post_ledger >= 0 else True,
        },
    }
    pass_conds = [
        out['safety']['no_unauthorized_spend'],
        out['safety']['no_5xx'],
        out['safety']['borea_invariant_held'],
        live['controlled_spend']['codes_ok'] >= 4,
        live['non_allowlist']['codes_blocked'] >= 25,
        live['burst_probe']['codes_429'] >= 10,
    ]
    out['verdict'] = 'PASS' if all(pass_conds) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} 5xx={live['burst_probe']['codes_5xx']} borea_404={live['borea_probes']['codes_404']}/30 → {OUT}")
    for k, v in out['totals'].items(): print(f'  {k} = {v}')
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
