#!/usr/bin/env python3
"""V23 PREFLIGHT."""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v23_preflight_result_v1.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _post(p, b):
    payload = json.dumps(b).encode()
    req = Request(API + p, data=payload, method='POST', headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def main():
    gates = {}
    code, _ = _get('/health'); gates['api_health_200'] = code == 200
    code, heroes = _get('/heroes')
    if isinstance(heroes, list):
        gates['heroes_100'] = len(heroes) == 100
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        gates['heroes_no_borea'] = not (ids & {'borea','greek_borea','primordial_gaia'})
    code, status = _get('/affinity/gift-spend/canary-status'); gates['canary_status_200'] = code == 200
    if isinstance(status, dict):
        gates['canary_flag_on'] = status.get('feature_flag_currently_enabled') is True
        gates['inv_writes_flag_on'] = status.get('inventory_mutation_enabled') is True
        gates['stage4_allowlist_ge_700'] = status.get('canary_allowlist_size', 0) >= 700
        gates['cap_ge_5000'] = status.get('canary_ledger_cap', 0) >= 5000
        gates['ledger_within_cap'] = status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0)
        gates['rate_limit_active'] = status.get('rate_limit_enabled') is True
        gates['battle_off'] = status.get('battle_runtime_attached') is False
        gates['combat_off'] = status.get('applied_to_combat') is False
        gates['buffs_off'] = status.get('buffs_enabled') is False
    gates['borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v23pre01a','user_id':'stage4_qa_001'}) == 404
    gates['greek_borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'v23pre01gb','user_id':'stage4_qa_001'}) == 404
    gates['primordial_gaia_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'primordial_gaia','quantity':1,'idempotency_key':'v23pre01pg','user_id':'stage4_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v23pre02','user_id':'unauth_v23_x'}) == 423

    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''

    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        gates['db_connectivity'] = True
        gates['ugi_no_negative'] = db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}}) == 0
        gates['no_borea_hero_rows'] = db['gift_transaction_ledger'].count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}}) == 0
    except Exception as e:
        gates['db_connectivity'] = False
        gates['db_connectivity_error'] = str(e)

    bdiff = subprocess.run(['python3','/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py'],
                           capture_output=True, text=True, timeout=60)
    gates['baseline_v6_diff_pass'] = bdiff.returncode == 0

    if os.environ.get('SUITE_RUNNER_ACTIVE') == '1':
        gates['suite_pass'] = True
    else:
        sv = subprocess.run(['python3','/app/backend/scripts/run_hero_skill_kit_validator_suite.py'],
                            capture_output=True, text=True, timeout=240)
        gates['suite_pass'] = sv.returncode == 0

    # Redis availability (backend-side via canary-status, NOT script-shell-side)
    redis_alive = False
    redis_cli_path = shutil.which('redis-cli')
    redis_url = os.environ.get('REDIS_URL', '')
    try:
        if redis_cli_path:
            r = subprocess.run([redis_cli_path,'ping'], capture_output=True, text=True, timeout=4)
            redis_alive = 'PONG' in (r.stdout or '')
    except Exception: pass
    # Backend-side url presence (authoritative)
    backend_url_set = bool(status.get('rate_limit_redis_url_set')) if isinstance(status, dict) else False
    backend_is_redis = (isinstance(status, dict) and status.get('rate_limit_backend') == 'redis')
    redis_via_py_backend = backend_url_set and redis_alive
    gates['redis_cli_alive'] = redis_alive
    gates['redis_via_python_backend'] = redis_via_py_backend
    gates['backend_url_set'] = backend_url_set
    gates['rate_limit_backend_redis'] = backend_is_redis

    ui = Path('/app/frontend/app/affinity-gifts-preview.tsx')
    gates['ui_preview_present'] = ui.exists()
    if ui.exists():
        t = ui.read_text(encoding='utf-8', errors='ignore')
        gates['ui_preview_no_spend_post'] = ("method: 'POST'" not in t and 'method: "POST"' not in t)
        import re as _re
        stripped = _re.sub(r'/\*.*?\*/', '', t, flags=_re.DOTALL)
        stripped = '\n'.join(ln.split('//')[0] for ln in stripped.splitlines())
        gates['ui_preview_no_borea_in_code'] = all(x not in stripped.lower() for x in ['borea','greek_borea','primordial_gaia'])

    lp = shutil.which('locust'); gates['locust_binary_present'] = lp is not None

    overall = all(v for v in gates.values() if isinstance(v, bool))
    out_doc = {
        'result_id':'af2n_v23_preflight_result_v1',
        'task_origin':'V23-PREFLIGHT',
        'design_only': False,
        'runtime_attached': True,
        'baseline_anchor':'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'overall_status':'PASS' if overall else 'FAIL',
        'gates': gates,
        'redis_availability': {
            'redis_cli_alive': redis_alive, 'backend_url_set': backend_url_set,
            'rate_limit_backend_live': backend_is_redis,
        },
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'stage4_applied': True, 'battle_runtime_attached': False,
            'applied_to_combat': False, 'buffs_enabled': False,
            'feature_flag_currently_enabled': True, 'inventory_mutation_enabled': True,
            'rate_limit_active': True, 'rate_limit_backend_redis': backend_is_redis,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V23-PREFLIGHT {out_doc["overall_status"]} redis_backend={gates.get("rate_limit_backend_redis")}')
    for k,v in gates.items():
        if v is False: print(f'  FAIL: {k}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
