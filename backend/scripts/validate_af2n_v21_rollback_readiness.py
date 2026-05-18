#!/usr/bin/env python3
"""V21 — Rollback Readiness aggregate validator.

Doesn't run rollback. Validates presence/readability of all rollback scripts,
backups, drill results.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v21_rollback_readiness_result_v1.json')

REQUIRED_SCRIPTS = [
    '/app/backend/scripts/rollback_af2n_stage4_internal_beta.py',
    '/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py',
    '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
    '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
    '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
]
REQUIRED_RESULTS = [
    '/app/data/design/affinity/af2n_v20_rollback_drill_result_v1.json',
    '/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json',
]


def main():
    checks = {}
    for s in REQUIRED_SCRIPTS:
        checks[f'script_present:{Path(s).name}'] = Path(s).exists()
    for r in REQUIRED_RESULTS:
        checks[f'result_present:{Path(r).name}'] = Path(r).exists()
    # latest stage4 backup exists
    backups = list(Path('/app/backups/af2n_stage4').glob('backend.conf.v21_pre_stage4_apply_*.bak'))
    checks['stage4_pre_apply_backup_present'] = len(backups) > 0
    # dry-run validate rollback script syntax
    import subprocess
    for s in REQUIRED_SCRIPTS:
        if Path(s).exists():
            r = subprocess.run(['python3', '-c', f'import ast; ast.parse(open({s!r}).read())'],
                               capture_output=True, text=True, timeout=10)
            checks[f'syntax_ok:{Path(s).name}'] = r.returncode == 0
    overall = all(checks.values())
    out_doc = {
        'result_id': 'af2n_v21_rollback_readiness_result_v1',
        'task_origin': 'V21-ROLLBACK-READINESS',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'checks': checks,
        'overall_status': 'PASS' if overall else 'FAIL',
        'rollback_plan': {
            'stage4_rollback_path': '/app/backend/scripts/rollback_af2n_stage4_internal_beta.py',
            'stage4_rollback_dry_run_env': 'STAGE4_ROLLBACK_DRY_RUN=true (default)',
            'rate_limit_disable_path': 'unset AFFINITY_GIFT_RATE_LIMIT_ENABLED in supervisor.conf + restart',
            'inventory_flag_disable_path': 'unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED in supervisor.conf + restart',
            'full_af2n_rollback': 'unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    if not overall:
        for k, v in checks.items():
            if not v: print(f'FAIL: {k}')
        return 2
    print('PASS: V21-ROLLBACK-READINESS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
