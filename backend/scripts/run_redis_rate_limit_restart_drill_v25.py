#!/usr/bin/env python3
"""V25 PART C — Redis rate-limit restart drill (safe).

Non-destructive: bounces redis via supervisor and verifies:
  - PONG returns within retry window
  - backend canary-status backend=redis (Redis recovers without backend restart)
  - burst 429 still works post-restart
  - Borea aliases still 404
  - no 5xx during the drill
"""
import json, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/redis_rate_limit_restart_drill_v25_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return -1, str(e)


def _post(p, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + p, data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def _redis_status():
    r = subprocess.run(['supervisorctl', 'status', 'redis'],
                        capture_output=True, text=True, timeout=5)
    return r.stdout.strip()


def _redis_ping():
    r = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=3)
    return r.stdout.strip()


def main():
    report = {
        'task_origin': 'AF2-N-V25-REDIS-RESTART-DRILL',
        'mode': 'SAFE_LIVE_RESTART',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'steps': [],
    }

    # Step 1: pre-state
    pre_status = _redis_status()
    pre_ping = _redis_ping()
    pre_code, pre_cs = _get('/api/affinity/gift-spend/canary-status')
    report['steps'].append({
        'step': '1_pre_state',
        'redis_status': pre_status,
        'redis_ping': pre_ping,
        'canary_http': pre_code,
        'canary_backend': pre_cs.get('rate_limit_backend') if isinstance(pre_cs, dict) else None,
    })

    # Step 2: restart via supervisor
    r = subprocess.run(['supervisorctl', 'restart', 'redis'],
                        capture_output=True, text=True, timeout=20)
    report['steps'].append({
        'step': '2_supervisor_restart',
        'cmd_rc': r.returncode,
        'stdout': r.stdout.strip(),
    })

    # Step 3: wait for PONG (max 10s)
    pong_attempts = []
    for i in range(10):
        time.sleep(0.5)
        p = _redis_ping()
        pong_attempts.append(p)
        if p == 'PONG':
            break
    report['steps'].append({
        'step': '3_post_restart_pong',
        'attempts': pong_attempts,
        'recovered': 'PONG' in pong_attempts,
    })

    # Step 4: backend canary-status backend=redis still
    post_code, post_cs = _get('/api/affinity/gift-spend/canary-status')
    report['steps'].append({
        'step': '4_backend_canary_post',
        'http': post_code,
        'rate_limit_backend': post_cs.get('rate_limit_backend') if isinstance(post_cs, dict) else None,
        'still_redis': isinstance(post_cs, dict) and post_cs.get('rate_limit_backend') == 'redis',
    })

    # Step 5: induce burst 429 to confirm rate-limit still functional
    burst_user = 'stage4_qa_499'
    burst_codes = []
    for i in range(10):
        c = _post('/api/affinity/gift-spend', {
            'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
            'idempotency_key': f'v25_drill_burst_{i}_{uuid.uuid4().hex[:6]}',
            'user_id': burst_user,
        })
        burst_codes.append(c)
    report['steps'].append({
        'step': '5_burst_post_restart',
        'sequence': burst_codes,
        'at_least_one_429': 429 in burst_codes,
        'no_5xx': all(c < 500 and c > 0 for c in burst_codes),
    })

    # Step 6: Borea still 404 after drill
    borea_codes = {}
    for h in ('borea', 'greek_borea', 'primordial_gaia'):
        borea_codes[h] = _post('/api/affinity/gift-spend', {
            'gift_id': 'x', 'hero_id': h, 'quantity': 1,
            'idempotency_key': f'v25_drill_borea_{h}', 'user_id': 'stage4_qa_001',
        })
    report['steps'].append({
        'step': '6_borea_post_restart',
        'codes': borea_codes,
        'all_404': all(c == 404 for c in borea_codes.values()),
    })

    # Verdict
    pass_conds = [
        report['steps'][2]['recovered'],
        report['steps'][3]['still_redis'],
        report['steps'][4]['at_least_one_429'],
        report['steps'][4]['no_5xx'],
        report['steps'][5]['all_404'],
    ]
    report['verdict'] = 'PASS' if all(pass_conds) else 'FAIL'
    OUT.write_text(json.dumps(report, indent=2, default=str))
    print(f"verdict={report['verdict']} → {OUT}")
    for s in report['steps']:
        print(f"  • {s['step']}")
    return 0 if report['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
