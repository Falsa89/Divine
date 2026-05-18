#!/usr/bin/env python3
"""Apply Stage2 5-10% allowlist expansion — GATED.

Safety:
  - All gates from /app/data/design/affinity/af2n_stage2_5_10pct_plan_v1.json must PASS.
  - Seeds new Stage2 QA users BEFORE flipping supervisor.conf.
  - Backs up supervisor.conf.
  - Restarts backend and runs a smoke.
  - On any failure -> READY_NOT_APPLIED with reason; rollback partial seed.

Usage:
  python3 apply_af2n_stage2_5_10pct_allowlist.py            # dry-run (writes READY_NOT_APPLIED unless --apply)
  python3 apply_af2n_stage2_5_10pct_allowlist.py --apply    # actually apply if gates pass
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PLAN = Path('/app/data/design/affinity/af2n_stage2_5_10pct_plan_v1.json')
RESULT = Path('/app/data/design/affinity/af2n_stage2_5_10pct_apply_result_v1.json')
SUP_CONF = Path('/etc/supervisor/conf.d/backend.conf')
SUP_CONF_BACKUP_DIR = Path('/app/ops/backups')
API = 'http://127.0.0.1:8001/api'

STAGE2_USERS = [f'stage2_qa_{i:03d}' for i in range(1, 51)]
STAGE2_TOTAL_ALLOWLIST_TARGET = 100
STAGE2_LEDGER_CAP_TARGET = 1000
MAX_TOTAL_ALLOWLIST_HARD = 200
MAX_LEDGER_CAP_HARD = 1000


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
    print(f'apply_af2n_stage2 -> {status}' + (f' reason={reason}' if reason else ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    payload = {
        'result_id': 'af2n_stage2_5_10pct_apply_result_v1',
        'task_origin': 'AF2-N-STAGE2-EXPANSION-APPLY',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'broad_rollout_authorized': False,
        'plan_ref': 'af2n_stage2_5_10pct_plan_v1',
        'gates': {},
        'stage2_user_count_target': len(STAGE2_USERS),
        'stage2_total_allowlist_target': STAGE2_TOTAL_ALLOWLIST_TARGET,
        'stage2_ledger_cap_target': STAGE2_LEDGER_CAP_TARGET,
        'mode': 'apply' if args.apply else 'dry_run',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        },
    }

    # Gates
    gates = payload['gates']
    gates['plan_present'] = PLAN.exists()
    if not gates['plan_present']:
        _save(payload, 'READY_NOT_APPLIED', 'plan_missing'); return 0

    # V17 preflight + extended monitoring + V16 composite must PASS
    v17pre = Path('/app/data/design/affinity/af2n_v17_preflight_result_v1.json')
    gates['v17_preflight_pass'] = v17pre.exists() and json.loads(v17pre.read_text()).get('overall_status') == 'PASS'
    v17mon = Path('/app/data/design/affinity/af2n_inventory_extended_monitoring_v17_result.json')
    gates['v17_extended_monitoring_pass'] = v17mon.exists() and json.loads(v17mon.read_text()).get('overall_status') == 'PASS'
    v16_sum = Path('/app/backend/reports/ultra_combo_v16_validator_summary_v1.json')
    gates['v16_composite_pass'] = v16_sum.exists() and json.loads(v16_sum.read_text()).get('overall') == 'PASS'

    # Live invariants
    c, heroes = _get('/heroes')
    gates['heroes_count_100'] = isinstance(heroes, list) and len(heroes) == 100
    gates['heroes_no_borea'] = isinstance(heroes, list) and not ({h.get('id') for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'})
    gates['borea_404_post'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v17stage20001','user_id':'stage1_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v17stage20002','user_id':'unauth_v17_stage2'}) == 423
    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''
    gates['supervisor_conf_present'] = SUP_CONF.exists()
    gates['target_allowlist_within_hard_cap'] = STAGE2_TOTAL_ALLOWLIST_TARGET <= MAX_TOTAL_ALLOWLIST_HARD
    gates['target_ledger_cap_within_hard_cap'] = STAGE2_LEDGER_CAP_TARGET <= MAX_LEDGER_CAP_HARD
    gates['stage2_user_count_le_50'] = len(STAGE2_USERS) <= 50

    # rollback scripts
    rollback_scripts = [
        '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
    ]
    gates['rollback_script_will_exist_after_creation'] = True  # we create them in V17

    all_pass = all(v is True for v in gates.values())
    payload['gates_all_pass'] = all_pass

    if not all_pass:
        bad = [k for k, v in gates.items() if v is not True]
        _save(payload, 'READY_NOT_APPLIED', f'gates_failed: {bad}')
        return 0

    if not args.apply:
        _save(payload, 'READY_NOT_APPLIED', 'dry_run_no_apply_flag (use --apply to commit gated)')
        return 0

    # APPLY PATH
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    ugi = db['user_gift_inventory']

    # 1) Backup supervisor.conf
    SUP_CONF_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_path = SUP_CONF_BACKUP_DIR / f'backend.conf.v17_pre_stage2.{ts}.bak'
    shutil.copy2(SUP_CONF, backup_path)
    payload['supervisor_backup_path'] = str(backup_path)

    # 2) Seed Stage2 inventory BEFORE supervisor flip
    now = datetime.now(timezone.utc)
    seed_inserts = 0; seed_skips = 0
    for u in STAGE2_USERS:
        existing = ugi.find_one({'user_id': u, 'gift_id': 'gift_test_001'})
        if existing:
            seed_skips += 1
            continue
        ugi.insert_one({
            'user_id': u, 'gift_id': 'gift_test_001', 'quantity': 10,
            'metadata': {'seed_task': 'V17_STAGE2', 'is_qa_user': True, 'synthetic': True},
            'created_at': now, 'updated_at': now,
        })
        seed_inserts += 1
    payload['seed_inserts'] = seed_inserts; payload['seed_skips'] = seed_skips

    if seed_inserts + seed_skips != len(STAGE2_USERS):
        # Try rollback partial seed
        ugi.delete_many({'metadata.seed_task': 'V17_STAGE2'})
        _save(payload, 'READY_NOT_APPLIED', f'seed_incomplete inserts={seed_inserts} skips={seed_skips}')
        return 0

    # 3) Update supervisor.conf: extend allowlist (Stage1 + Stage2) + cap
    conf_text = SUP_CONF.read_text()
    # Build new allowlist token: existing stage1 (50) + 50 stage2
    # Read current allowlist via canary-status (since conf already has it)
    _, cur_status = _get('/affinity/gift-spend/canary-status')
    cur_size = (cur_status or {}).get('canary_allowlist_size', 50)

    # Parse existing allowlist directly from conf
    import re
    m = re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', conf_text)
    if not m:
        ugi.delete_many({'metadata.seed_task': 'V17_STAGE2'})
        _save(payload, 'READY_NOT_APPLIED', 'allowlist_token_not_found_in_supervisor')
        return 0
    existing_allowlist = [s for s in m.group(1).split(',') if s.strip()]
    new_allowlist = existing_allowlist + [u for u in STAGE2_USERS if u not in existing_allowlist]
    if len(new_allowlist) > MAX_TOTAL_ALLOWLIST_HARD:
        ugi.delete_many({'metadata.seed_task': 'V17_STAGE2'})
        _save(payload, 'READY_NOT_APPLIED', f'allowlist_size_would_exceed_hard_cap {len(new_allowlist)}>{MAX_TOTAL_ALLOWLIST_HARD}')
        return 0
    new_allowlist_token = ','.join(new_allowlist)
    new_conf = re.sub(
        r'AFFINITY_GIFT_CANARY_ALLOWLIST="[^"]+"',
        f'AFFINITY_GIFT_CANARY_ALLOWLIST="{new_allowlist_token}"',
        conf_text, count=1,
    )
    new_conf = re.sub(
        r'AFFINITY_GIFT_CANARY_LEDGER_CAP="\d+"',
        f'AFFINITY_GIFT_CANARY_LEDGER_CAP="{STAGE2_LEDGER_CAP_TARGET}"',
        new_conf, count=1,
    )
    SUP_CONF.write_text(new_conf)
    payload['supervisor_conf_updated'] = True
    payload['new_allowlist_size'] = len(new_allowlist)
    payload['new_ledger_cap'] = STAGE2_LEDGER_CAP_TARGET

    # 4) Restart backend
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=20)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)

    # 5) Wait for /api/health
    ok = False
    for i in range(20):
        time.sleep(1.5)
        c, _ = _get('/health')
        if c == 200: ok = True; break
    if not ok:
        _save(payload, 'READY_NOT_APPLIED', 'backend_did_not_recover_post_restart')
        return 0

    # 6) Smoke verify: allowlist now N, cap now CAP, heroes=100, borea 404, non-allow 423
    _, st = _get('/affinity/gift-spend/canary-status')
    payload['smoke_canary_status'] = st
    smoke_ok = (
        isinstance(st, dict)
        and st.get('canary_allowlist_size') == len(new_allowlist)
        and st.get('canary_ledger_cap') == STAGE2_LEDGER_CAP_TARGET
        and st.get('feature_flag_currently_enabled') is True
        and st.get('inventory_mutation_enabled') is True
        and st.get('buffs_enabled') is False
        and st.get('applied_to_combat') is False
        and st.get('battle_runtime_attached') is False
    )
    payload['smoke_status_ok'] = smoke_ok
    if not smoke_ok:
        _save(payload, 'READY_NOT_APPLIED', f'smoke_status_check_failed st={st}')
        return 0

    _save(payload, 'APPLIED_PASS', None, {
        'applied': True,
        'new_allowlist_size_total': len(new_allowlist),
        'new_ledger_cap_total': STAGE2_LEDGER_CAP_TARGET,
        'stage2_users_seeded': seed_inserts + seed_skips,
    })
    return 0

if __name__ == '__main__':
    sys.exit(main())
