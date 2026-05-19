#!/usr/bin/env python3
"""V23 — Rollback readiness V23."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v23_rollback_readiness_result_v1.json')
REQ_SCRIPTS = [
    '/app/backend/scripts/rollback_af2n_stage4_internal_beta.py',
    '/app/backend/scripts/rollback_af2n_stage3_qa_expansion.py',
    '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
    '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
    '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
]
REQ_DOCS = [
    '/app/data/design/affinity/af2n_v22_rollback_readiness_result_v1.json',
    '/app/data/design/affinity/af2n_v21_rollback_readiness_result_v1.json',
    '/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json',
]


def main():
    checks = {}
    for s in REQ_SCRIPTS:
        p = Path(s); checks[f'script:{p.name}'] = p.exists()
        if p.exists():
            r = subprocess.run(['python3','-c',f'import ast; ast.parse(open({s!r}).read())'],
                               capture_output=True, text=True, timeout=10)
            checks[f'syntax_ok:{p.name}'] = r.returncode == 0
    for d in REQ_DOCS:
        checks[f'doc:{Path(d).name}'] = Path(d).exists()
    # V23-specific: pre-redis-switch supervisor backup
    pre_redis = list(Path('/app/backups/af2n_stage4').glob('backend.conf.v23_pre_redis_switch_*.bak'))
    pre_stage4 = list(Path('/app/backups/af2n_stage4').glob('backend.conf.v21_pre_stage4_apply_*.bak'))
    checks['pre_redis_switch_backup_present'] = len(pre_redis) > 0
    checks['stage4_pre_apply_backup_present'] = len(pre_stage4) > 0
    overall = all(checks.values())
    out_doc = {
        'result_id':'af2n_v23_rollback_readiness_result_v1',
        'task_origin':'V23-ROLLBACK-READINESS',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'checks': checks,
        'rollback_options': {
            'stage4_rollback':'rollback_af2n_stage4_internal_beta.py (DRY_RUN=true default; STAGE4_ROLLBACK_DRY_RUN=false to apply)',
            'redis_switch_rollback':'restore supervisor.conf from backend.conf.v23_pre_redis_switch_*.bak (removes REDIS_URL + sets AFFINITY_RATE_LIMIT_BACKEND=memory) + restart',
            'rate_limit_disable':'unset AFFINITY_GIFT_RATE_LIMIT_ENABLED + restart',
            'inventory_flag_disable':'unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'full_af2n_rollback':'unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
            'db_backup_restore':'/app/backups/af2n_stage4/backup_<STAMP>/ files',
        },
        'overall_status': 'PASS' if overall else 'FAIL',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    if not overall:
        for k,v in checks.items():
            if not v: print(f'FAIL: {k}')
        return 2
    print('PASS: V23-ROLLBACK-READINESS'); return 0


if __name__ == '__main__':
    sys.exit(main())
