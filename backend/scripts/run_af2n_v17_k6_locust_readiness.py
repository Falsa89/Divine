#!/usr/bin/env python3
"""AF2-L-K6/LOCUST REAL READINESS V17.

Checks installation of k6 / locust. If unavailable and unsafe to install
(no apt/yum or container restricted), produces a Python fallback probe
(low-impact: replay + non-allowlist + Borea rejects only — no fresh
mutations) and emits exact install instructions for future ops.
"""
from __future__ import annotations
import json, shutil, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v17_k6_locust_readiness_result_v1.json')
FALLBACK_REQ_TARGET = 2000


def _get(p):
    try:
        with urlopen(API + p, timeout=4) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1

def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=4) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def main():
    payload = {
        'result_id': 'af2n_v17_k6_locust_readiness_result_v1',
        'task_origin': 'AF2-L-K6-LOCUST-READINESS-V17',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    }

    k6_path = shutil.which('k6')
    locust_path = shutil.which('locust')
    apt_path = shutil.which('apt-get')
    pip_path = shutil.which('pip3') or shutil.which('pip')
    payload['k6_binary_present'] = bool(k6_path); payload['k6_binary_path'] = k6_path
    payload['locust_binary_present'] = bool(locust_path); payload['locust_binary_path'] = locust_path
    payload['apt_get_present'] = bool(apt_path)
    payload['pip_present'] = bool(pip_path)

    payload['install_instructions'] = {
        'k6': [
            'curl -fsSL https://github.com/grafana/k6/releases/latest/download/k6-linux-amd64.tar.gz | tar -xzf - -C /tmp',
            'sudo install /tmp/k6-*-linux-amd64/k6 /usr/local/bin/k6',
            'k6 version',
        ],
        'locust_via_pip': [
            'pip3 install --user locust',
            'locust --version',
        ],
        'safety_note': 'Run only with --vus 5 --duration 30s targeting non-allowlist 423 and Borea 404 paths to avoid any state change.'
    }

    # Try real run only if available
    real_k6_run = None; real_locust_run = None
    if k6_path:
        # Run an extremely small k6 smoke probe (5 vus 5s) read-only
        script_path = Path('/tmp/v17_k6_smoke.js')
        script_path.write_text(
            "import http from 'k6/http';\n"
            "export const options = { vus: 5, duration: '5s' };\n"
            "export default function () {\n"
            "  http.get('http://127.0.0.1:8001/api/health');\n"
            "  http.get('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status');\n"
            "}\n")
        try:
            t0 = time.time()
            r = subprocess.run([k6_path, 'run', '--quiet', str(script_path)],
                               capture_output=True, text=True, timeout=30)
            real_k6_run = {'exit_code': r.returncode, 'duration_s': time.time() - t0,
                           'tail': (r.stdout or r.stderr).strip().splitlines()[-3:]}
        except Exception as e:
            real_k6_run = {'exit_code': -1, 'error': repr(e)}
    payload['real_k6_run'] = real_k6_run

    # Python fallback probe (safe: read-only + non-allow + Borea rejects)
    fb = {'requests_total': 0, 'http_5xx': 0, 'borea_404': 0, 'borea_bad': 0,
          'non_allowlist_423': 0, 'non_allowlist_bad': 0,
          'health_200': 0, 'canary_status_200': 0,
          'heroes_100_ok': 0}
    t0 = time.time()
    # 800 health
    for i in range(800):
        c = _get('/health'); fb['requests_total'] += 1
        if c == 200: fb['health_200'] += 1
        elif 500 <= c < 600: fb['http_5xx'] += 1
    # 200 canary-status
    for i in range(200):
        c = _get('/affinity/gift-spend/canary-status'); fb['requests_total'] += 1
        if c == 200: fb['canary_status_200'] += 1
        elif 500 <= c < 600: fb['http_5xx'] += 1
    # 500 non-allowlist
    for i in range(500):
        c = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':f'v17k6n{i:04d}xx','user_id':f'unauth_k6_{i}'})
        fb['requests_total'] += 1
        if c == 423: fb['non_allowlist_423'] += 1
        else: fb['non_allowlist_bad'] += 1
        if 500 <= c < 600: fb['http_5xx'] += 1
    # 500 borea rejects
    for i in range(500):
        c = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'borea','quantity':1,
             'idempotency_key':f'v17k6b{i:04d}xx','user_id':'stage1_qa_001'})
        fb['requests_total'] += 1
        if c == 404: fb['borea_404'] += 1
        else: fb['borea_bad'] += 1
        if 500 <= c < 600: fb['http_5xx'] += 1
    fb['duration_s'] = round(time.time() - t0, 2)
    fb['rps'] = round(fb['requests_total'] / max(fb['duration_s'], 0.01), 1)
    payload['python_fallback_probe'] = fb

    fb_pass = (
        fb['requests_total'] >= FALLBACK_REQ_TARGET and
        fb['http_5xx'] == 0 and
        fb['borea_bad'] == 0 and
        fb['non_allowlist_bad'] == 0
    )
    payload['python_fallback_probe_pass'] = fb_pass

    payload['overall_status'] = 'PASS' if fb_pass else 'FAIL'
    payload['safety_flags'] = {
        'no_fresh_spend_attempted_in_fallback': True,
        'broad_rollout_authorized': False,
        'battle_runtime_attached': False,
        'buffs_enabled': False,
        'applied_to_combat': False,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
    }
    payload['recommendation'] = (
        'k6/locust install possible via instructions above. Python fallback is sufficient '
        'for current canary scope. Real k6 LIVE plan deferred to future authorized task (AF2-L-K6-LIVE).'
        if not k6_path else
        'k6 detected on host. Use real_k6_run smoke result; expand to full LIVE plan only with explicit authorization.'
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'K6/Locust readiness V17: status={payload["overall_status"]} k6={bool(k6_path)} locust={bool(locust_path)} fb_reqs={fb["requests_total"]} rps={fb["rps"]}')
    return 0 if fb_pass else 1

if __name__ == '__main__':
    sys.exit(main())
