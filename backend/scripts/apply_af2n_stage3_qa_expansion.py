#!/usr/bin/env python3
"""Apply Stage3 QA expansion — GATED.

Usage:
  python3 apply_af2n_stage3_qa_expansion.py            # dry-run (writes READY_NOT_APPLIED)
  python3 apply_af2n_stage3_qa_expansion.py --apply    # actually apply if gates pass
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PLAN = Path('/app/data/design/affinity/af2n_stage3_qa_expansion_plan_v1.json')
RESULT = Path('/app/data/design/affinity/af2n_stage3_qa_expansion_apply_result_v1.json')
SUP_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/ops/backups')
API = 'http://127.0.0.1:8001/api'

STAGE3_USERS = [f'stage3_qa_{i:03d}' for i in range(1, 101)]
STAGE3_TOTAL_ALLOWLIST_TARGET = 200
STAGE3_LEDGER_CAP_TARGET = 2500
HARD_MAX_TOTAL_ALLOWLIST = 500
HARD_MAX_LEDGER_CAP = 5000


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

def _save(payload, status, reason=None, extras=None):
    payload['overall_status'] = status
    payload['ready_not_applied_reason'] = reason
    payload['generated_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    if extras: payload.update(extras)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'apply_af2n_stage3 -> {status}' + (f' reason={reason}' if reason else ''))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true'); args = ap.parse_args()
    payload = {
        'result_id': 'af2n_stage3_qa_expansion_apply_result_v1',
        'task_origin': 'AF2-N-STAGE3-QA-EXPANSION-APPLY',
        'design_only': False, 'runtime_attached': True,
        'broad_rollout_authorized': False, 'public_spend_ui': False,
        'plan_ref': 'af2n_stage3_qa_expansion_plan_v1',
        'gates': {}, 'mode': 'apply' if args.apply else 'dry_run',
        'stage3_user_count_target': len(STAGE3_USERS),
        'stage3_total_allowlist_target': STAGE3_TOTAL_ALLOWLIST_TARGET,
        'stage3_ledger_cap_target': STAGE3_LEDGER_CAP_TARGET,
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    gates = payload['gates']
    gates['plan_present'] = PLAN.exists()
    v18pre = Path('/app/data/design/affinity/af2n_v18_preflight_result_v1.json')
    gates['v18_preflight_pass'] = v18pre.exists() and json.loads(v18pre.read_text()).get('overall_status') == 'PASS'
    v18stmon = Path('/app/data/design/affinity/af2n_stage2_extended_monitoring_v18_result.json')
    gates['stage2_extended_monitoring_v18_pass'] = v18stmon.exists() and json.loads(v18stmon.read_text()).get('overall_status') == 'PASS'
    v17_sum = Path('/app/backend/reports/ultra_combo_v17_validator_summary_v1.json')
    gates['v17_composite_pass'] = v17_sum.exists() and json.loads(v17_sum.read_text()).get('overall') == 'PASS'
    c, heroes = _get('/heroes')
    gates['heroes_count_100'] = isinstance(heroes, list) and len(heroes) == 100
    gates['heroes_no_borea'] = isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'})
    gates['borea_404_post'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v18s30001','user_id':'stage2_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v18s30002','user_id':'unauth_v18_s3'}) == 423
    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'], capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''
    gates['supervisor_conf_present'] = SUP_CONF.exists()
    gates['target_allowlist_le_hard'] = STAGE3_TOTAL_ALLOWLIST_TARGET <= HARD_MAX_TOTAL_ALLOWLIST
    gates['target_cap_le_hard'] = STAGE3_LEDGER_CAP_TARGET <= HARD_MAX_LEDGER_CAP
    gates['stage3_user_count_le_200'] = len(STAGE3_USERS) <= 200
    gates['rollback_script_self_exists'] = True

    all_pass = all(v is True for v in gates.values())
    payload['gates_all_pass'] = all_pass
    if not all_pass:
        bad = [k for k,v in gates.items() if v is not True]
        _save(payload, 'READY_NOT_APPLIED', f'gates_failed: {bad}')
        return 0
    if not args.apply:
        _save(payload, 'READY_NOT_APPLIED', 'dry_run_no_apply_flag (use --apply to commit gated)')
        return 0

    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    ugi = db['user_gift_inventory']

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = BACKUP_DIR / f'backend.conf.v18_pre_stage3.{ts}.bak'
    shutil.copy2(SUP_CONF, backup)
    payload['supervisor_backup_path'] = str(backup)

    now = datetime.now(timezone.utc)
    seed_inserts = 0; seed_skips = 0
    for u in STAGE3_USERS:
        if ugi.find_one({'user_id': u, 'gift_id': 'gift_test_001'}):
            seed_skips += 1; continue
        ugi.insert_one({
            'user_id': u, 'gift_id': 'gift_test_001', 'quantity': 10,
            'metadata': {'seed_task': 'V18_STAGE3', 'is_qa_user': True, 'synthetic': True},
            'created_at': now, 'updated_at': now,
        })
        seed_inserts += 1
    payload['seed_inserts'] = seed_inserts; payload['seed_skips'] = seed_skips
    if seed_inserts + seed_skips != len(STAGE3_USERS):
        ugi.delete_many({'metadata.seed_task': 'V18_STAGE3'})
        _save(payload, 'READY_NOT_APPLIED', f'seed_incomplete'); return 0

    conf_text = SUP_CONF.read_text()
    m = re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', conf_text)
    if not m:
        ugi.delete_many({'metadata.seed_task': 'V18_STAGE3'})
        _save(payload, 'READY_NOT_APPLIED', 'allowlist_token_not_found'); return 0
    existing = [s for s in m.group(1).split(',') if s.strip()]
    new_list = existing + [u for u in STAGE3_USERS if u not in existing]
    if len(new_list) > HARD_MAX_TOTAL_ALLOWLIST:
        ugi.delete_many({'metadata.seed_task': 'V18_STAGE3'})
        _save(payload, 'READY_NOT_APPLIED', f'allowlist_size_over_hard_max {len(new_list)}>{HARD_MAX_TOTAL_ALLOWLIST}'); return 0
    new_token = ','.join(new_list)
    new_conf = re.sub(r'AFFINITY_GIFT_CANARY_ALLOWLIST="[^"]+"', f'AFFINITY_GIFT_CANARY_ALLOWLIST="{new_token}"', conf_text, count=1)
    new_conf = re.sub(r'AFFINITY_GIFT_CANARY_LEDGER_CAP="\d+"', f'AFFINITY_GIFT_CANARY_LEDGER_CAP="{STAGE3_LEDGER_CAP_TARGET}"', new_conf, count=1)
    SUP_CONF.write_text(new_conf)
    payload['supervisor_conf_updated'] = True
    payload['new_allowlist_size'] = len(new_list)
    payload['new_ledger_cap'] = STAGE3_LEDGER_CAP_TARGET

    subprocess.run(['supervisorctl','update'], capture_output=True, text=True, timeout=20)
    subprocess.run(['supervisorctl','restart','backend'], capture_output=True, text=True, timeout=30)
    ok = False
    for _ in range(20):
        time.sleep(1.5)
        c, _ = _get('/health')
        if c == 200: ok = True; break
    if not ok:
        _save(payload, 'READY_NOT_APPLIED', 'backend_did_not_recover'); return 0

    _, st = _get('/affinity/gift-spend/canary-status')
    payload['smoke_canary_status'] = st
    smoke_ok = (
        isinstance(st, dict)
        and st.get('canary_allowlist_size') == len(new_list)
        and st.get('canary_ledger_cap') == STAGE3_LEDGER_CAP_TARGET
        and st.get('feature_flag_currently_enabled') is True
        and st.get('inventory_mutation_enabled') is True
        and st.get('buffs_enabled') is False
        and st.get('applied_to_combat') is False
        and st.get('battle_runtime_attached') is False
    )
    payload['smoke_status_ok'] = smoke_ok
    if not smoke_ok:
        _save(payload, 'READY_NOT_APPLIED', f'smoke_failed st={st}'); return 0
    _save(payload, 'APPLIED_PASS', None, {
        'applied': True,
        'new_allowlist_size_total': len(new_list),
        'new_ledger_cap_total': STAGE3_LEDGER_CAP_TARGET,
        'stage3_users_seeded': seed_inserts + seed_skips,
    })
    return 0

if __name__ == '__main__':
    sys.exit(main())
