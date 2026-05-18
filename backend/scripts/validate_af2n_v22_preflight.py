#!/usr/bin/env python3
"""V22 PREFLIGHT — Runner + Validator."""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v22_preflight_result_v1.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


def _post(p, b):
    payload = json.dumps(b).encode()
    headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r:
            return r.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


def main():
    gates = {}
    code, _ = _get('/health'); gates['api_health_200'] = code == 200
    code, heroes = _get('/heroes')
    if isinstance(heroes, list):
        gates['heroes_100'] = len(heroes) == 100
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        gates['heroes_no_borea'] = not (ids & {'borea', 'greek_borea', 'primordial_gaia'})
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
    gates['borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v22pre01a','user_id':'stage4_qa_001'}) == 404
    gates['greek_borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'v22pre01gb','user_id':'stage4_qa_001'}) == 404
    gates['primordial_gaia_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'primordial_gaia','quantity':1,'idempotency_key':'v22pre01pg','user_id':'stage4_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v22pre02','user_id':'unauth_v22_x'}) == 423

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
        gates['no_borea_hero_rows'] = db['gift_transaction_ledger'].count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0
        # sample consistency: sum applied_inventory_live quantity should equal stage4 inventory consumed sum (rough proxy)
        agg = list(db['gift_transaction_ledger'].aggregate([
            {'$match': {'inventory_mutated': True}},
            {'$group': {'_id': None, 'q': {'$sum': '$quantity'}}}
        ]))
        gates['ledger_inventory_mut_qty_recorded'] = bool(agg)
    except Exception as e:
        gates['db_connectivity'] = False
        gates['db_connectivity_error'] = str(e)

    # rollback scripts presence
    for s in [
        '/app/backend/scripts/rollback_af2n_stage4_internal_beta.py',
        '/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py',
        '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
    ]:
        gates[f'rollback_present:{Path(s).name}'] = Path(s).exists()

    # baseline diff
    bdiff = subprocess.run(['python3','/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py'],
                           capture_output=True, text=True, timeout=60)
    gates['baseline_v6_diff_pass'] = bdiff.returncode == 0

    # suite v21 expected pass — skip when run from suite
    if os.environ.get('SUITE_RUNNER_ACTIVE') == '1':
        gates['suite_pass'] = True
    else:
        sv = subprocess.run(['python3','/app/backend/scripts/run_hero_skill_kit_validator_suite.py'],
                            capture_output=True, text=True, timeout=240)
        gates['suite_pass'] = sv.returncode == 0

    # UI preview safety (read-only)
    ui = Path('/app/frontend/app/affinity-gifts-preview.tsx')
    gates['ui_preview_present'] = ui.exists()
    if ui.exists():
        t = ui.read_text(encoding='utf-8', errors='ignore')
        gates['ui_preview_no_spend_post'] = (
            "method: 'POST'" not in t and 'method: "POST"' not in t and "method:'POST'" not in t
        )
        import re as _re
        stripped = _re.sub(r'/\*.*?\*/', '', t, flags=_re.DOTALL)
        stripped = '\n'.join(ln.split('//')[0] for ln in stripped.splitlines())
        gates['ui_preview_no_borea_in_code'] = all(
            x not in stripped.lower() for x in ['borea','greek_borea','primordial_gaia']
        )

    # locust binary
    lp = shutil.which('locust'); gates['locust_binary_present'] = lp is not None
    try:
        lv = subprocess.run(['locust','--version'], capture_output=True, text=True, timeout=5)
        locust_version = (lv.stdout or lv.stderr).strip()
    except Exception as e:
        locust_version = f'<error: {e}>'
    gates['locust_version_known'] = bool(locust_version) and 'locust' in locust_version.lower()

    # Redis availability check (advisory — not a hard gate; controls migration plan status)
    redis_server = shutil.which('redis-server')
    redis_cli = shutil.which('redis-cli')
    redis_url = os.environ.get('REDIS_URL', '')
    py_redis_available = False
    try:
        import redis  # noqa
        py_redis_available = True
        py_redis_version = redis.__version__
    except Exception:
        py_redis_version = None
    redis_alive = False
    redis_alive_detail = None
    if redis_cli or redis_url:
        try:
            r = subprocess.run([redis_cli or 'redis-cli','ping'], capture_output=True, text=True, timeout=4)
            redis_alive = 'PONG' in (r.stdout or '')
            redis_alive_detail = (r.stdout or r.stderr).strip()[:200]
        except Exception as e:
            redis_alive_detail = str(e)
    gates['py_redis_pkg_present'] = py_redis_available  # informational only
    # informational only, not contributing to overall PASS
    redis_status = {
        'redis_server_binary': bool(redis_server),
        'redis_cli_binary': bool(redis_cli),
        'redis_url_env_set': bool(redis_url),
        'redis_url_value': (redis_url[:200] if redis_url else None),
        'py_redis_package': py_redis_available,
        'py_redis_version': py_redis_version,
        'redis_alive_ping': redis_alive,
        'redis_alive_detail': redis_alive_detail,
        'overall_redis_available': bool(redis_alive),
    }

    overall = all(v for v in gates.values() if isinstance(v, bool))
    out_doc = {
        'result_id': 'af2n_v22_preflight_result_v1',
        'task_origin': 'V22-PREFLIGHT',
        'design_only': False,
        'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'gates': gates,
        'locust_path': lp,
        'locust_version': locust_version,
        'redis_availability': redis_status,
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'safety_flags': {
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'stage4_applied': True,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'buffs_enabled': False,
            'feature_flag_currently_enabled': True,
            'inventory_mutation_enabled': True,
            'rate_limit_active': True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V22-PREFLIGHT {out_doc["overall_status"]} redis_available={redis_alive} -> {OUT}')
    for k,v in gates.items():
        if v is False: print(f'  FAIL: {k}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
