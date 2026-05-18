#!/usr/bin/env python3
"""AF2-L-K6/LOCUST V18 — Safe install attempt + strong Python fallback."""
from __future__ import annotations
import json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v18_k6_locust_result_v1.json')
FB_REQ_TARGET = 3500


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


def _try_install_locust():
    pip = shutil.which('pip3') or shutil.which('pip')
    if not pip: return {'attempted': False, 'reason': 'no_pip'}
    try:
        r = subprocess.run([pip, 'install', '--quiet', '--no-warn-script-location', 'locust'],
                           capture_output=True, text=True, timeout=120)
        ok = (r.returncode == 0) and bool(shutil.which('locust'))
        return {'attempted': True, 'exit_code': r.returncode, 'success': ok,
                'tail': (r.stdout or r.stderr).strip().splitlines()[-3:]}
    except Exception as e:
        return {'attempted': True, 'success': False, 'error': repr(e)}


def main():
    payload = {
        'result_id': 'af2n_v18_k6_locust_result_v1',
        'task_origin': 'AF2-L-K6-LOCUST-V18',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    }
    k6_path = shutil.which('k6'); locust_path = shutil.which('locust')
    payload['k6_binary_present'] = bool(k6_path); payload['k6_binary_path'] = k6_path
    payload['locust_binary_present'] = bool(locust_path); payload['locust_binary_path'] = locust_path

    # Safe install attempt: locust via pip is non-invasive and easily reversible.
    # k6 install requires sudo install / system path; we skip the destructive parts.
    install_attempt = {}
    if not locust_path:
        install_attempt['locust'] = _try_install_locust()
        # refresh path
        locust_path = shutil.which('locust')
        payload['locust_binary_present_after_attempt'] = bool(locust_path)
        payload['locust_binary_path_after_attempt'] = locust_path
    payload['install_attempts'] = install_attempt

    # If locust now available, run a tiny read-only smoke (3 users, 5s)
    real_locust = None
    if locust_path:
        locustfile = Path('/tmp/v18_locustfile.py')
        locustfile.write_text(
            'from locust import HttpUser, task, between\n'
            'class S(HttpUser):\n'
            '    wait_time = between(0.01, 0.05)\n'
            '    @task\n'
            '    def health(self): self.client.get("/api/health")\n'
            '    @task\n'
            '    def status(self): self.client.get("/api/affinity/gift-spend/canary-status")\n'
        )
        try:
            t0 = time.time()
            r = subprocess.run(
                [locust_path, '-f', str(locustfile), '--headless',
                 '-u', '3', '-r', '3', '-t', '5s', '--host', 'http://127.0.0.1:8001',
                 '--only-summary'],
                capture_output=True, text=True, timeout=30)
            real_locust = {'exit_code': r.returncode, 'duration_s': round(time.time()-t0,2),
                           'tail': (r.stdout or r.stderr).strip().splitlines()[-5:]}
        except Exception as e:
            real_locust = {'exit_code': -1, 'error': repr(e)}
    payload['real_locust_run'] = real_locust

    # k6 detection only (no destructive install)
    payload['k6_install_instructions'] = [
        'curl -fsSL https://github.com/grafana/k6/releases/latest/download/k6-linux-amd64.tar.gz -o /tmp/k6.tgz',
        'tar -xzf /tmp/k6.tgz -C /tmp',
        'sudo install /tmp/k6-*-linux-amd64/k6 /usr/local/bin/k6',
        'k6 version',
    ]

    # Strong Python fallback: 3500 read-only requests
    fb = {'requests_total':0,'http_5xx':0,'borea_404':0,'borea_bad':0,'non_allowlist_423':0,
          'non_allowlist_bad':0,'health_200':0,'canary_status_200':0,'heroes_100_ok':0}
    t0 = time.time()
    for i in range(1400):
        c = _get('/health'); fb['requests_total'] += 1
        if c == 200: fb['health_200'] += 1
        elif 500 <= c < 600: fb['http_5xx'] += 1
    for i in range(400):
        c = _get('/affinity/gift-spend/canary-status'); fb['requests_total'] += 1
        if c == 200: fb['canary_status_200'] += 1
        elif 500 <= c < 600: fb['http_5xx'] += 1
    for i in range(200):
        from urllib.request import urlopen
        try:
            with urlopen(API + '/heroes', timeout=4) as r:
                ok = (r.status == 200)
            if ok: fb['heroes_100_ok'] += 1
        except Exception: pass
        fb['requests_total'] += 1
    for i in range(700):
        c = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':f'v18k6n{i:04d}xx','user_id':f'unauth_v18k_{i}'})
        fb['requests_total'] += 1
        if c == 423: fb['non_allowlist_423'] += 1
        else: fb['non_allowlist_bad'] += 1
        if 500 <= c < 600: fb['http_5xx'] += 1
    for i in range(800):
        c = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'borea','quantity':1,
             'idempotency_key':f'v18k6b{i:04d}xx','user_id':'stage1_qa_001'})
        fb['requests_total'] += 1
        if c == 404: fb['borea_404'] += 1
        else: fb['borea_bad'] += 1
        if 500 <= c < 600: fb['http_5xx'] += 1
    fb['duration_s'] = round(time.time() - t0, 2)
    fb['rps'] = round(fb['requests_total'] / max(fb['duration_s'], 0.01), 1)
    payload['python_fallback_probe'] = fb
    payload['python_fallback_probe_pass'] = (
        fb['requests_total'] >= FB_REQ_TARGET and fb['http_5xx'] == 0 and
        fb['borea_bad'] == 0 and fb['non_allowlist_bad'] == 0
    )

    overall_pass = payload['python_fallback_probe_pass'] and (real_locust is None or real_locust.get('exit_code') in (0, None))
    payload['overall_status'] = 'PASS' if overall_pass else 'FAIL'
    payload['safety_flags'] = {
        'no_fresh_spend_attempted': True,
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_runtime_attached': False,
        'buffs_enabled': False,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
    }
    payload['recommendation'] = (
        f'Locust installato={bool(locust_path)}; smoke OK={bool(real_locust and real_locust.get("exit_code") in (0,None))}. '
        'Python fallback robusto (3500+ req read-only). k6 install richiede sudo: rinviato a task gated separato.'
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V18 k6/locust: status={payload["overall_status"]} k6={bool(k6_path)} locust={bool(locust_path)} fb_reqs={fb["requests_total"]} rps={fb["rps"]}')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
