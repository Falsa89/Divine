#!/usr/bin/env python3
"""Run Locust low-impact load test (V19) + DB invariant probes.

If Locust binary missing, fall back to a Python concurrent probe that
emulates the same read-only / reject mix at higher RPS than V18 fallback.
"""
from __future__ import annotations
import json, shutil, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed

LOCUSTFILE = Path('/app/loadtests/af2n_stage3_locustfile.py')
OUT = Path('/app/data/design/affinity/af2n_stage3_locust_low_impact_result_v1.json')
API = 'http://127.0.0.1:8001'


def _gather_db_snapshot():
    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        coll = db['gift_transaction_ledger']
        return {
            'ledger_total': coll.count_documents({}),
            'inventory_mutated': coll.count_documents({'inventory_mutated': True}),
            'affinity_points_mutated': coll.count_documents({'affinity_points_mutated': True}),
            'buffs': coll.count_documents({'buffs_activated': True}),
            'battle_wiring': coll.count_documents({'battle_wiring_attached': True}),
            'borea_hero': coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}),
            'negative_inventory': db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}}),
        }
    except Exception as e:
        return {'error': repr(e)}


def _python_fallback():
    """Concurrent Python fallback if Locust unavailable."""
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
    counters = {'reqs':0,'http_5xx':0,'health_200':0,'status_200':0,'heroes_200':0,'gifts_200':0,
                'na_423':0,'na_bad':0,'borea_404':0,'borea_bad':0,'replay_ok':0,'replay_bad':0}
    def work_health(i): return ('health', _get('/api/health'))
    def work_status(i): return ('status', _get('/api/affinity/gift-spend/canary-status'))
    def work_heroes(i): return ('heroes', _get('/api/heroes'))
    def work_gifts(i): return ('gifts', _get('/api/affinity/gifts'))
    def work_na(i):
        return ('na', _post('/api/affinity/gift-spend', {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v19fbn'+uuid.uuid4().hex[:8],'user_id':f'unauth_v19fb_{i}'}))
    def work_borea(i):
        return ('borea', _post('/api/affinity/gift-spend', {'gift_id':'gift_test_001','hero_id':'borea','quantity':1,'idempotency_key':'v19fbb'+uuid.uuid4().hex[:8],'user_id':'stage3_qa_001'}))
    def work_replay(i):
        return ('replay', _post('/api/affinity/gift-spend', {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':2,'idempotency_key':'v16live001ai','user_id':'stage1_qa_001'}))
    tasks = ([work_health]*400 + [work_status]*150 + [work_heroes]*100 + [work_gifts]*100
             + [work_na]*200 + [work_borea]*150 + [work_replay]*50)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(fn, i) for i, fn in enumerate(tasks)]
        for f in as_completed(futures):
            kind, code = f.result()
            counters['reqs'] += 1
            if 500 <= code < 600: counters['http_5xx'] += 1
            if kind == 'health' and code == 200: counters['health_200'] += 1
            elif kind == 'status' and code == 200: counters['status_200'] += 1
            elif kind == 'heroes' and code == 200: counters['heroes_200'] += 1
            elif kind == 'gifts' and code == 200: counters['gifts_200'] += 1
            elif kind == 'na':
                if code == 423: counters['na_423'] += 1
                else: counters['na_bad'] += 1
            elif kind == 'borea':
                if code == 404: counters['borea_404'] += 1
                else: counters['borea_bad'] += 1
            elif kind == 'replay':
                if code == 200: counters['replay_ok'] += 1
                else: counters['replay_bad'] += 1
    dur = round(time.time() - t0, 2)
    return {'mode': 'python_fallback_concurrent', 'duration_s': dur,
            'rps': round(counters['reqs']/max(dur,0.01), 1),
            'counters': counters}


def main():
    pre_snap = _gather_db_snapshot()
    payload = {
        'result_id': 'af2n_stage3_locust_low_impact_result_v1',
        'task_origin': 'AF2-L-LOCUST-LOW-IMPACT-V19',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'pre_snapshot': pre_snap,
    }
    locust = shutil.which('locust')
    payload['locust_binary_present'] = bool(locust); payload['locust_binary_path'] = locust
    if locust and LOCUSTFILE.exists():
        # Low-impact: 8 users, ramp-up 4/s, run 20s, headless
        try:
            t0 = time.time()
            r = subprocess.run([locust, '-f', str(LOCUSTFILE), '--headless',
                                '-u', '8', '-r', '4', '-t', '20s',
                                '--host', API, '--only-summary',
                                '--csv', '/tmp/v19_locust_csv', '--csv-full-history'],
                               capture_output=True, text=True, timeout=60)
            tail = (r.stdout or r.stderr).strip().splitlines()[-25:]
            payload['locust_run'] = {
                'exit_code': r.returncode,
                'duration_s': round(time.time()-t0, 2),
                'tail': tail,
                'cmd': 'locust -f /app/loadtests/af2n_stage3_locustfile.py --headless -u 8 -r 4 -t 20s --host http://127.0.0.1:8001',
            }
        except Exception as e:
            payload['locust_run'] = {'exit_code': -1, 'error': repr(e)}
    else:
        payload['locust_run'] = {'exit_code': None, 'reason': 'locust_or_locustfile_missing'}

    payload['python_fallback'] = _python_fallback()
    post_snap = _gather_db_snapshot()
    payload['post_snapshot'] = post_snap
    delta = {}
    if isinstance(pre_snap, dict) and isinstance(post_snap, dict) and 'error' not in pre_snap and 'error' not in post_snap:
        for k in pre_snap:
            if isinstance(pre_snap[k], int): delta[k] = post_snap.get(k,0) - pre_snap.get(k,0)
    payload['delta'] = delta

    # Safety thresholds: NO uncontrolled growth. The Locust scenarios use
    # idempotent replay (key already exists → no new ledger row) and pure
    # reject paths, so ledger delta MUST be 0 from Locust + fallback.
    triggers = []
    locust_ok = (payload['locust_run'].get('exit_code') in (0, None))
    fb = payload.get('python_fallback', {}).get('counters', {})
    if delta.get('ledger_total', 0) > 0: triggers.append(('ledger_growth', delta.get('ledger_total')))
    if delta.get('borea_hero', 0) > 0: triggers.append(('borea_hero_growth', delta.get('borea_hero')))
    if delta.get('buffs', 0) > 0: triggers.append(('buffs_growth', delta.get('buffs')))
    if delta.get('battle_wiring', 0) > 0: triggers.append(('battle_wiring_growth', delta.get('battle_wiring')))
    if delta.get('negative_inventory', 0) > 0: triggers.append(('negative_inventory_growth', delta.get('negative_inventory')))
    if fb.get('http_5xx', 0) > 0: triggers.append(('fb_http_5xx', fb.get('http_5xx')))
    if fb.get('borea_bad', 0) > 0: triggers.append(('fb_borea_bad', fb.get('borea_bad')))
    if fb.get('na_bad', 0) > 0: triggers.append(('fb_na_bad', fb.get('na_bad')))
    if fb.get('replay_bad', 0) > 0: triggers.append(('fb_replay_bad', fb.get('replay_bad')))

    payload['triggers_fired'] = [{'trigger': t, 'detail': d} for t, d in triggers]
    payload['triggers_total'] = len(triggers)
    payload['overall_status'] = 'PASS' if (locust_ok and not triggers) else 'FAIL'
    payload['safety_flags'] = {
        'no_fresh_spend_attempted_in_locust': True,
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_runtime_attached': False,
        'buffs_enabled': False,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V19 Locust low-impact: {payload["overall_status"]} locust_exit={payload["locust_run"].get("exit_code")} fb_reqs={fb.get("reqs")} delta_ledger={delta.get("ledger_total",0)} triggers={len(triggers)}')
    return 0 if payload['overall_status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
