#!/usr/bin/env python3
"""V21 — APPLY Stage4 Internal Beta (gated).

Applies ONLY if signoff_v5_applied says stage4_apply_allowed=true AND all V21
artifacts (preflight, rate-limit probe, db backup drill) PASS.

Mutations:
  1. backup current /etc/supervisor/conf.d/backend.conf to /app/backups/af2n_stage4/
  2. seed user_gift_inventory documents for 500 stage4 internal users
  3. seed user_affinity_state (lazy, optional — done on first gift)
  4. rewrite backend.conf with extended allowlist and cap=5000
  5. supervisorctl update + restart backend
  6. emit af2n_stage4_internal_beta_apply_result_v1.json with stage4_applied=true

If any gate fails, writes apply_result with stage4_applied=false and exits 2.
NEVER touches battle_engine.py / combat.tsx / gacha / roster / catalog.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

SIGNOFF = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5_applied.json')
PREFLIGHT = Path('/app/data/design/affinity/af2n_v21_preflight_result_v1.json')
RL_PROBE = Path('/app/data/design/affinity/affinity_gift_spend_rate_limit_probe_result_v1.json')
DB_BACKUP = Path('/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json')
SUPERVISOR_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backups/af2n_stage4')
OUT = Path('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')
NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime('%Y%m%dT%H%M%SZ')

STAGE4_USER_COUNT = 500
STAGE4_USER_PREFIX = 'stage4_qa_'  # stage4_qa_001 ... stage4_qa_500
TARGET_CAP = 5000
SEED_GIFT_ID = 'gift_test_001'
SEED_QTY = 10


def _gen_stage4_users():
    return [f'{STAGE4_USER_PREFIX}{i:03d}' for i in range(1, STAGE4_USER_COUNT + 1)]


def _check_gates():
    """Return (ok, reasons[])."""
    reasons = []
    if not SIGNOFF.exists():
        reasons.append('signoff_v5_applied_missing'); return False, reasons
    s = json.loads(SIGNOFF.read_text())
    if s.get('stage4_apply_allowed') is not True:
        reasons.append('stage4_apply_allowed_false')
    if s.get('final_user_stage4_apply_approval') is not True:
        reasons.append('final_user_approval_false')
    if s.get('broad_rollout_authorized') is not False:
        reasons.append('broad_rollout_authorized_true')
    if s.get('public_spend_ui') is not False:
        reasons.append('public_spend_ui_true')
    if s.get('battle_wiring') is not False:
        reasons.append('battle_wiring_true')
    for f in (PREFLIGHT, RL_PROBE, DB_BACKUP):
        if not f.exists():
            reasons.append(f'missing:{f.name}'); continue
        d = json.loads(f.read_text())
        if d.get('overall_status') != 'PASS':
            reasons.append(f'gate_fail:{f.name}:{d.get("overall_status")}')
    # final invariant probes
    out = subprocess.run([
        'git', '-C', '/app', 'diff', '--stat', '--',
        'backend/battle_engine.py', 'backend/battle_core.py', 'frontend/app/combat.tsx',
        'backend/synergy_system.py', 'backend/game_systems.py'
    ], capture_output=True, text=True, timeout=10)
    if out.stdout.strip() != '':
        reasons.append('battle_files_changed')
    return (len(reasons) == 0), reasons


def _seed_inventory(db):
    ugi = db['user_gift_inventory']
    seeded = 0
    skipped = 0
    for uid in _gen_stage4_users():
        existing = ugi.find_one({'user_id': uid, 'gift_id': SEED_GIFT_ID})
        if existing:
            skipped += 1
            continue
        ugi.insert_one({
            'user_id': uid,
            'gift_id': SEED_GIFT_ID,
            'quantity': SEED_QTY,
            'updated_at': NOW,
            'metadata': {
                'seed_task': 'V21_STAGE4',
                'is_internal_user': True,
                'synthetic': True,
            },
            'created_at': NOW,
        })
        seeded += 1
    return seeded, skipped


def _patch_supervisor_conf():
    text = SUPERVISOR_CONF.read_text()
    # backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bk = BACKUP_DIR / f'backend.conf.v21_pre_stage4_apply_{STAMP}.bak'
    bk.write_text(text)
    # extract current allowlist value and append stage4 users
    import re
    m = re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', text)
    if not m:
        raise RuntimeError('could not locate AFFINITY_GIFT_CANARY_ALLOWLIST in supervisor conf')
    current = m.group(1)
    existing_users = [u.strip() for u in current.split(',') if u.strip()]
    stage4_users = _gen_stage4_users()
    new_users = existing_users + [u for u in stage4_users if u not in existing_users]
    new_allowlist = ','.join(new_users)
    new_text = text.replace(
        f'AFFINITY_GIFT_CANARY_ALLOWLIST="{current}"',
        f'AFFINITY_GIFT_CANARY_ALLOWLIST="{new_allowlist}"',
    )
    # patch cap
    mc = re.search(r'AFFINITY_GIFT_CANARY_LEDGER_CAP="(\d+)"', new_text)
    if not mc:
        raise RuntimeError('could not locate AFFINITY_GIFT_CANARY_LEDGER_CAP in supervisor conf')
    old_cap = mc.group(1)
    new_text = new_text.replace(
        f'AFFINITY_GIFT_CANARY_LEDGER_CAP="{old_cap}"',
        f'AFFINITY_GIFT_CANARY_LEDGER_CAP="{TARGET_CAP}"',
    )
    SUPERVISOR_CONF.write_text(new_text)
    return {
        'backup_path': str(bk),
        'old_allowlist_size': len(existing_users),
        'new_allowlist_size': len(new_users),
        'old_cap': int(old_cap),
        'new_cap': TARGET_CAP,
        'stage4_users_added': sum(1 for u in stage4_users if u not in existing_users),
    }


def main():
    ok, reasons = _check_gates()
    apply_result = {
        'result_id': 'af2n_stage4_internal_beta_apply_result_v1',
        'task_origin': 'V21-AF2N-STAGE4-INTERNAL-BETA-APPLY',
        'started_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'stage4_applied': False,
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring': False,
        'gate_reasons_for_block': reasons,
        'safety_invariants': [
            'no broad rollout',
            'no public spend UI',
            'no battle wiring',
            'no Borea reveal',
            'no gacha/roster/catalog mutation',
            'battle_engine.py / battle_core.py / combat.tsx unchanged'
        ],
    }
    if not ok:
        apply_result['overall_status'] = 'READY_NOT_APPLIED'
        apply_result['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(apply_result, indent=2))
        print(f'V21-STAGE4-APPLY BLOCKED reasons={reasons}')
        return 2

    # Seed inventory
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_waifus')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    seeded, skipped = _seed_inventory(db)

    # Patch supervisor.conf
    patch_info = _patch_supervisor_conf()

    # supervisorctl restart
    upd = subprocess.run(['sudo', 'supervisorctl', 'update'], capture_output=True, text=True, timeout=30)
    rst = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)

    # Wait + smoke verify
    import time
    time.sleep(4)
    from urllib.request import urlopen
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=6) as r:
            st = json.loads(r.read().decode())
    except Exception as e:
        st = {'error': str(e)}

    apply_result.update({
        'stage4_applied': True,
        'overall_status': 'APPLIED',
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'inventory_seed': {
            'stage4_user_count_target': STAGE4_USER_COUNT,
            'seeded': seeded, 'skipped_existing': skipped,
            'gift_id': SEED_GIFT_ID, 'qty_per_user': SEED_QTY,
        },
        'supervisor_patch': patch_info,
        'supervisorctl_update_stderr_tail': (upd.stderr or '')[-200:],
        'supervisorctl_restart_stdout_tail': (rst.stdout or '')[-200:],
        'post_apply_canary_status': st,
        'target_allowlist_size': patch_info['new_allowlist_size'],
        'target_cap': TARGET_CAP,
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(apply_result, indent=2, default=str))
    print(f'V21-STAGE4-APPLY APPLIED seeded={seeded} allowlist={patch_info["new_allowlist_size"]} cap={TARGET_CAP}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
