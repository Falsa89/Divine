#!/usr/bin/env python3
"""V28 PART C — Post-apply observation (phased, IP-aware)."""
import json, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_scope_s1_observation_v28_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _flush():
    try: subprocess.run(['redis-cli', 'FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception: pass


def main():
    started = datetime.now(timezone.utc).isoformat()
    phases = {}

    # 1. Borea probes 50
    _flush()
    p1 = {'codes': [], '404': 0}
    for i in range(50):
        alias = ('borea', 'greek_borea', 'primordial_gaia')[i % 3]
        c = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                   'idempotency_key': f'v28_obs_b_{i}_{uuid.uuid4().hex[:6]}',
                   'user_id': 'stage4_qa_001'})
        p1['codes'].append(c)
        if c == 404: p1['404'] += 1
    p1['ok'] = p1['404'] >= 48
    phases['borea_probes'] = p1

    # 2. Non-allowlist 40
    _flush()
    p2 = {'codes': [], 'gated': 0}
    for i in range(40):
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                   'idempotency_key': f'v28_obs_na_{i}_{uuid.uuid4().hex[:6]}',
                   'user_id': f'outsider_v28_{i}'})
        p2['codes'].append(c)
        if c in (423, 429): p2['gated'] += 1
    p2['ok'] = p2['gated'] >= 35
    phases['non_allowlist_probes'] = p2

    # 3. Old Stage4 controlled 5
    _flush()
    p3 = {'codes': [], 'ok_count': 0}
    for i in range(5):
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                   'idempotency_key': f'v28_obs_oldc_{i}_{uuid.uuid4().hex[:8]}',
                   'user_id': f'stage4_qa_{(i % 100) + 1:03d}'})
        p3['codes'].append(c)
        if c in (200, 201): p3['ok_count'] += 1
        time.sleep(0.05)
    p3['ok'] = p3['ok_count'] >= 4
    phases['stage4_controlled_spend'] = p3

    # 4. NEW internal beta controlled 10
    _flush()
    p4 = {'codes': [], 'ok_count': 0, 'last_idem': None}
    for i in range(10):
        idem = f'v28_obs_newc_{i}_{uuid.uuid4().hex[:8]}'
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                   'idempotency_key': idem,
                   'user_id': f'stage5_qa_{i + 1:04d}'})
        p4['codes'].append(c); p4['last_idem'] = idem
        if c in (200, 201): p4['ok_count'] += 1
        time.sleep(0.05)
    p4['ok'] = p4['ok_count'] >= 8
    phases['internal_beta_new_controlled_spend'] = p4

    # 5. Idempotency replay (new user)
    p5 = {'replay_code': None, 'ok': False}
    if p4['last_idem']:
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                   'idempotency_key': p4['last_idem'], 'user_id': 'stage5_qa_0001'})
        p5['replay_code'] = c
        p5['ok'] = c in (200, 201, 409)
    phases['idempotency_replay'] = p5

    # 6. Burst 20
    _flush()
    p6 = {'codes': [], '429': 0, '5xx': 0}
    for i in range(20):
        c = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                   'idempotency_key': f'v28_obs_burst_{i}_{uuid.uuid4().hex[:6]}',
                   'user_id': 'stage5_qa_1500'})
        p6['codes'].append(c)
        if c == 429: p6['429'] += 1
        if 500 <= c < 600: p6['5xx'] += 1
    p6['ok'] = p6['429'] >= 8 and p6['5xx'] == 0
    phases['burst_429'] = p6

    cs = _get('/api/affinity/gift-spend/canary-status') or {}
    phases['canary_status_final'] = {
        'rate_limit_backend': cs.get('rate_limit_backend'),
        'ledger_total_rows': cs.get('ledger_total_rows'),
        'canary_ledger_cap': cs.get('canary_ledger_cap'),
        'canary_allowlist_size': cs.get('canary_allowlist_size'),
    }

    total_5xx = sum(1 for ph in (p1, p2, p3, p4, p6) for c in ph['codes'] if 500 <= c < 600)
    samples = sum(len(ph['codes']) for ph in (p1, p2, p3, p4, p6)) + (1 if p5['replay_code'] is not None else 0)

    out = {
        'task_origin': 'AF2-N-V28-SCOPE-S1-OBSERVATION',
        'mode': 'IP_AWARE_PHASED',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'total_samples': samples,
        'phases': phases,
        'total_5xx_count': total_5xx,
    }
    out['verdict'] = 'PASS' if all([
        p1['ok'], p2['ok'], p3['ok'], p4['ok'], p5['ok'], p6['ok'],
        total_5xx == 0,
        phases['canary_status_final']['rate_limit_backend'] == 'redis',
        phases['canary_status_final']['canary_allowlist_size'] == 2500,
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} samples={samples} 5xx={total_5xx} new_ok={p4['ok_count']}/10 → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
