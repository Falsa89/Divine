#!/usr/bin/env python3
"""V20 PREFLIGHT — Runner + Validator."""
from __future__ import annotations
import json, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v20_preflight_result_v1.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None

def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
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
    gates['borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v20pre0001a','user_id':'stage3_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v20pre0001b','user_id':'unauth_v20_x'}) == 423

    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''

    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        ugi = db['user_gift_inventory']; coll = db['gift_transaction_ledger']
        gates['ugi_no_negative'] = ugi.count_documents({'quantity': {'$lt': 0}}) == 0
        gates['inv_aff_mut_equal'] = coll.count_documents({'inventory_mutated': True}) == coll.count_documents({'affinity_points_mutated': True})
        gates['no_buffs_rows'] = coll.count_documents({'buffs_activated': True}) == 0
        gates['no_battle_wiring_rows'] = coll.count_documents({'battle_wiring_attached': True}) == 0
        gates['no_borea_hero_rows'] = coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0
    except Exception:
        gates['ugi_no_negative'] = False

    rollback_scripts = [
        '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
        '/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py',
        '/app/ops/rollback_af2n_canary.sh',
    ]
    gates['rollback_scripts_present'] = all(Path(p).exists() for p in rollback_scripts)

    v19_sum = Path('/app/backend/reports/ultra_combo_v19_validator_summary_v1.json')
    gates['suite_v19_pass'] = (v19_sum.exists() and json.loads(v19_sum.read_text()).get('overall') == 'PASS')
    gates['baseline_v6_diff_pass'] = gates.get('battle_files_unchanged', False)

    locust_path = shutil.which('locust')
    locust_ver = None
    if locust_path:
        try:
            r = subprocess.run([locust_path, '--version'], capture_output=True, text=True, timeout=8)
            locust_ver = (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else None
        except Exception: pass
    gates['locust_binary_present'] = bool(locust_path)
    gates['locust_version_known'] = bool(locust_ver)

    preview = Path('/app/frontend/app/affinity-gifts-preview.tsx')
    gates['ui_preview_present'] = preview.exists()
    if preview.exists():
        body = preview.read_text()
        gates['ui_preview_no_spend_call'] = 'gift-spend",' not in body and "gift-spend'," not in body
        gates['ui_preview_no_borea'] = ("'borea'" not in body and '"borea"' not in body)

    overall = all(gates.values())
    payload = {
        'result_id': 'af2n_v20_preflight_result_v1',
        'task_origin': 'V20-PREFLIGHT',
        'design_only': False, 'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'gates': gates,
        'locust_path': locust_path, 'locust_version': locust_ver,
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'stage4_applied': False, 'battle_runtime_attached': False,
            'applied_to_combat': False, 'buffs_enabled': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V20 preflight overall: {payload["overall_status"]}')
    failures=[]
    print('='*70); print('V20 PREFLIGHT — Validator'); print('='*70)
    rec = lambda n, c: (print(f'  [OK] {n}') if c else (failures.append(n) or print(f'  [X] {n}')))
    rec('overall_pass', payload['overall_status'] == 'PASS')
    for g, v in gates.items(): rec(f'gate:{g}', v is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
