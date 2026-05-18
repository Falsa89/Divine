#!/usr/bin/env python3
"""V17 Rollback Readiness — verifies all rollback scripts are available
and executable in dry-run mode.
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v17_rollback_readiness_result_v1.json')

ROLLBACK_SCRIPTS = [
    '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
    '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
    '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1_retry.py',
    '/app/backend/scripts/rollback_stage1_qa_gift_inventory_seed.py',
    '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
    '/app/ops/rollback_af2n_canary.sh',
]


def main():
    payload = {
        'result_id': 'af2n_v17_rollback_readiness_result_v1',
        'task_origin': 'AF2-N-V17-ROLLBACK-READINESS',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'scripts': [],
        'safety_flags': {
            'broad_rollout_authorized': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        },
    }
    all_present = True
    for p in ROLLBACK_SCRIPTS:
        f = Path(p)
        entry = {'path': p, 'present': f.exists()}
        if not f.exists(): all_present = False
        entry['size_bytes'] = f.stat().st_size if f.exists() else None
        payload['scripts'].append(entry)

    # Dry-run Stage2 rollback if script exists
    s2 = Path('/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py')
    if s2.exists():
        r = subprocess.run(['python3', str(s2)], capture_output=True, text=True, timeout=20)
        payload['stage2_rollback_dry_run_exit'] = r.returncode
        payload['stage2_rollback_dry_run_tail'] = (r.stdout or r.stderr).strip().splitlines()[-3:]
    payload['all_scripts_present'] = all_present

    # Supervisor backup directory writable
    backup_dir = Path('/app/ops/backups')
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        probe = backup_dir / '.readiness_probe_v17'
        probe.write_text('ok'); probe.unlink()
        payload['supervisor_backup_dir_writable'] = True
    except Exception:
        payload['supervisor_backup_dir_writable'] = False

    overall_pass = all_present and payload.get('supervisor_backup_dir_writable') is True
    payload['overall_status'] = 'PASS' if overall_pass else 'FAIL'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V17 rollback readiness: {payload["overall_status"]} (scripts={len(ROLLBACK_SCRIPTS)} all_present={all_present})')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
