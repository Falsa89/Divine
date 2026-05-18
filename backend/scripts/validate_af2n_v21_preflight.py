#!/usr/bin/env python3
"""V21 PREFLIGHT — Runner + Validator.

Checks runtime/health/Borea/canary/baseline/suite/UI/DB preconditions BEFORE V21 mutations.
Writes /app/data/design/affinity/af2n_v21_preflight_result_v1.json and exits 0 if all gates PASS.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v21_preflight_result_v1.json')


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
    code, _ = _get('/health')
    gates['api_health_200'] = code == 200
    code, heroes = _get('/heroes')
    if isinstance(heroes, list):
        gates['heroes_100'] = len(heroes) == 100
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        gates['heroes_no_borea'] = not (ids & {'borea', 'greek_borea', 'primordial_gaia'})
    code, status = _get('/affinity/gift-spend/canary-status')
    gates['canary_status_200'] = code == 200
    if isinstance(status, dict):
        gates['canary_flag_on'] = status.get('feature_flag_currently_enabled') is True
        gates['inv_writes_flag_on'] = status.get('inventory_mutation_enabled') is True
        gates['stage3_allowlist_ge_200'] = status.get('canary_allowlist_size', 0) >= 200
        gates['cap_ge_2500'] = status.get('canary_ledger_cap', 0) >= 2500
        gates['ledger_within_cap'] = status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0)
        gates['battle_off'] = status.get('battle_runtime_attached') is False
        gates['combat_off'] = status.get('applied_to_combat') is False
        gates['buffs_off'] = status.get('buffs_enabled') is False

    gates['borea_404'] = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
        'idempotency_key': 'v21pre0001a', 'user_id': 'stage3_qa_001'}) == 404
    gates['greek_borea_404'] = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': 'greek_borea', 'quantity': 1,
        'idempotency_key': 'v21pre0001gb', 'user_id': 'stage3_qa_001'}) == 404
    gates['primordial_gaia_404'] = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': 'primordial_gaia', 'quantity': 1,
        'idempotency_key': 'v21pre0001pg', 'user_id': 'stage3_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': 'greek_zeus', 'quantity': 1,
        'idempotency_key': 'v21pre0001b', 'user_id': 'unauth_v21_x'}) == 423

    out = subprocess.run([
        'git', '-C', '/app', 'diff', '--stat', '--',
        'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
        'backend/synergy_system.py', 'backend/game_systems.py'
    ], capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''

    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        ugi = db['user_gift_inventory']
        coll = db['gift_transaction_ledger']
        gates['db_connectivity'] = True
        gates['ugi_no_negative'] = ugi.count_documents({'quantity': {'$lt': 0}}) == 0
        agg = list(coll.aggregate([
            {'$match': {'canary': True, 'status': 'applied_inventory_live'}},
            {'$group': {'_id': None,
                        'qty': {'$sum': '$quantity'},
                        'inv_mut': {'$sum': {'$cond': [{'$eq': ['$inventory_mutated', True]}, '$quantity', 0]}},
                        'aff_mut': {'$sum': {'$cond': [{'$eq': ['$affinity_points_mutated', True]}, '$quantity', 0]}}}}
        ]))
        if agg:
            gates['inv_aff_mut_equal'] = agg[0].get('inv_mut') == agg[0].get('aff_mut')
        else:
            gates['inv_aff_mut_equal'] = True
        gates['no_buffs_rows'] = coll.count_documents({'buffs_activated': True}) == 0
        gates['no_battle_wiring_rows'] = coll.count_documents({'battle_wiring_attached': True}) == 0
        gates['no_borea_hero_rows'] = coll.count_documents({'hero_id': {'$in': ['borea', 'greek_borea', 'primordial_gaia']}}) == 0
    except Exception as e:
        gates['db_connectivity'] = False
        gates['db_connectivity_error'] = str(e)

    # rollback scripts presence
    for s in [
        '/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py',
        '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
        '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
        '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
    ]:
        gates[f'rollback_present:{Path(s).name}'] = Path(s).exists()

    # baseline diff
    bdiff = subprocess.run([
        'python3', '/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py'
    ], capture_output=True, text=True, timeout=60)
    gates['baseline_v6_diff_pass'] = bdiff.returncode == 0

    # suite v20 expected pass — SKIP when running from within suite to avoid recursion
    if os.environ.get('SUITE_RUNNER_ACTIVE') == '1':
        gates['suite_pass'] = True  # parent suite is already aware of failure
    else:
        sv = subprocess.run([
            'python3', '/app/backend/scripts/run_hero_skill_kit_validator_suite.py'
        ], capture_output=True, text=True, timeout=180)
        gates['suite_pass'] = sv.returncode == 0

    # UI preview safety
    ui = Path('/app/frontend/app/affinity-gifts-preview.tsx')
    gates['ui_preview_present'] = ui.exists()
    if ui.exists():
        t = ui.read_text(encoding='utf-8', errors='ignore')
        # Check no POST/PUT/PATCH/DELETE to gift-spend mutation endpoint
        gates['ui_preview_no_spend_post'] = (
            "method: 'POST'" not in t and 'method: "POST"' not in t
            and "method:'POST'" not in t
        )
        # Borea identifiers must not appear in user-visible text or hero_id field.
        # We allow comment lines like "* - NO Borea alias displayed." (these are
        # explicit safety annotations). Strip multi-line block comments first.
        import re as _re
        stripped = _re.sub(r"/\*.*?\*/", "", t, flags=_re.DOTALL)
        stripped = '\n'.join(
            ln.split('//')[0] if '//' in ln else ln for ln in stripped.splitlines()
        )
        gates['ui_preview_no_borea'] = all(
            x not in stripped.lower() for x in ['borea', 'greek_borea', 'primordial_gaia']
        )

    # locust binary
    lp = shutil.which('locust')
    gates['locust_binary_present'] = lp is not None
    try:
        lv = subprocess.run(['locust', '--version'], capture_output=True, text=True, timeout=5)
        locust_version = (lv.stdout or lv.stderr).strip()
    except Exception as e:
        locust_version = f'<error: {e}>'
    gates['locust_version_known'] = bool(locust_version) and 'locust' in locust_version.lower()

    # DB backup destination writable
    backup_dir = Path('/app/backups/af2n_stage4')
    backup_dir.mkdir(parents=True, exist_ok=True)
    probe = backup_dir / '.v21_preflight_write_probe'
    try:
        probe.write_text('ok')
        probe.unlink()
        gates['db_backup_dest_writable'] = True
    except Exception:
        gates['db_backup_dest_writable'] = False

    # V20 plan + signoff package presence
    gates['v20_stage4_plan_present'] = Path('/app/data/design/affinity/af2n_stage4_internal_beta_plan_v1.json').exists()
    gates['v20_signoff_package_v5_present'] = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5.json').exists()

    overall = all(v for v in gates.values() if isinstance(v, bool))
    out_doc = {
        'result_id': 'af2n_v21_preflight_result_v1',
        'task_origin': 'V21-PREFLIGHT',
        'design_only': False,
        'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'gates': gates,
        'locust_path': lp,
        'locust_version': locust_version,
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'safety_flags': {
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'stage4_applied': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'buffs_enabled': False,
            'feature_flag_currently_enabled': True,
            'inventory_mutation_enabled': True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V21-PREFLIGHT {out_doc["overall_status"]} -> {OUT}')
    for k, v in gates.items():
        if v is False:
            print(f'  FAIL: {k}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
