#!/usr/bin/env python3
"""V20 Rollback drills — dry-run only. No actual state change.

Drills covered:
  1) Stage3 rollback dry-run
  2) Stage2 rollback dry-run (since Stage3 implies Stage2 was applied)
  3) Inventory flag rollback dry-run (ops shell, simulated)
  4) Full AF2-N canary rollback dry-run (ops shell, simulated)
  5) UI preview rollback plan (delete file)
  6) Locust stop/abort plan
  7) DB backup/restore plan for inventory/affinity/ledger (commands only)
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v20_rollback_drill_result_v1.json')


def _dry_run(script_path, args=None):
    p = Path(script_path)
    entry = {'script': str(script_path), 'present': p.exists()}
    if not p.exists(): entry['exit_code'] = -2; return entry
    cmd = ['python3', str(p)] + list(args or [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        entry['exit_code'] = r.returncode
        entry['cmd'] = ' '.join(cmd)
        entry['tail'] = (r.stdout or r.stderr).strip().splitlines()[-3:]
    except Exception as e:
        entry['exit_code'] = -1; entry['error'] = repr(e)
    return entry


def main():
    payload = {
        'result_id': 'af2n_v20_rollback_drill_result_v1',
        'task_origin': 'AF2-N-V20-ROLLBACK-DRILLS',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'mode': 'dry_run_only',
        'no_actual_state_change': True,
        'drills': {},
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'stage4_applied': False, 'battle_runtime_attached': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    # 1) Stage3 rollback dry-run
    payload['drills']['stage3_rollback_dry_run'] = _dry_run('/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py')
    # 2) Stage2 rollback dry-run
    payload['drills']['stage2_rollback_dry_run'] = _dry_run('/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py')
    # 3) Inventory flag rollback dry-run (plan-only — ops shell)
    ops_sh = Path('/app/ops/rollback_af2n_canary.sh')
    payload['drills']['inventory_flag_rollback_plan'] = {
        'script': str(ops_sh), 'present': ops_sh.exists(),
        'plan_steps': [
            'set AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="" in /etc/supervisor/conf.d/backend.conf',
            'supervisorctl reread; supervisorctl update; supervisorctl restart backend',
            'verify canary-status inventory_mutation_enabled==False',
        ],
        'dry_run_only': True,
    }
    # 4) Full AF2-N canary rollback dry-run (plan-only)
    payload['drills']['full_af2n_canary_rollback_plan'] = {
        'script': str(ops_sh), 'present': ops_sh.exists(),
        'plan_steps': [
            'set AFFINITY_GIFT_RUNTIME_ENABLED="" + AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="" in supervisor.conf',
            'set AFFINITY_GIFT_CANARY_ALLOWLIST="" and CANARY_LEDGER_CAP="0"',
            'supervisorctl reread; supervisorctl update; supervisorctl restart backend',
            'verify canary-status feature_flag_currently_enabled==False',
        ],
        'dry_run_only': True,
    }
    # 5) UI preview rollback plan
    preview = Path('/app/frontend/app/affinity-gifts-preview.tsx')
    payload['drills']['ui_preview_rollback_plan'] = {
        'preview_present': preview.exists(),
        'rollback_command': f'rm {preview} && cd /app/frontend && yarn build (or expo rebuild)',
        'dry_run_only': True,
    }
    # 6) Locust stop/abort plan
    locust = shutil.which('locust')
    payload['drills']['locust_stop_abort_plan'] = {
        'locust_path': locust,
        'stop_command': 'pkill -f "locust -f /app/loadtests" || true',
        'verify_command': 'pgrep -f locust && echo still-running || echo stopped',
        'no_lingering_processes_check': 'pgrep -f locust returns empty',
        'dry_run_only': True,
    }
    # 7) DB backup/restore plan
    payload['drills']['db_backup_restore_plan'] = {
        'backup_command_inventory': 'mongodump --uri mongodb://localhost:27017 --db divine_waifus --collection user_gift_inventory --out /app/ops/backups/dbdump_$(date -u +%Y%m%dT%H%M%SZ)',
        'backup_command_affinity_state': 'mongodump --uri mongodb://localhost:27017 --db divine_waifus --collection user_affinity_state --out /app/ops/backups/dbdump_$(date -u +%Y%m%dT%H%M%SZ)',
        'backup_command_ledger': 'mongodump --uri mongodb://localhost:27017 --db divine_waifus --collection gift_transaction_ledger --out /app/ops/backups/dbdump_$(date -u +%Y%m%dT%H%M%SZ)',
        'restore_command_pattern': 'mongorestore --uri mongodb://localhost:27017 --db divine_waifus <dump-path>',
        'mongodump_present': bool(shutil.which('mongodump')),
        'mongorestore_present': bool(shutil.which('mongorestore')),
        'dry_run_only': True,
    }

    # Aggregate pass
    failures = []
    for k, d in payload['drills'].items():
        if 'exit_code' in d and d['exit_code'] not in (0, None):
            failures.append((k, d.get('exit_code')))
        if 'present' in d and not d['present']:
            failures.append((k, 'script_missing'))
        if 'preview_present' in d and not d['preview_present']:
            failures.append((k, 'preview_missing'))
    payload['failures'] = failures
    payload['overall_status'] = 'PASS' if not failures else 'FAIL'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V20 rollback drills: {payload["overall_status"]} (drills={len(payload["drills"])} failures={len(failures)})')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
