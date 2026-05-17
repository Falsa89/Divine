#!/usr/bin/env python3
"""
AF2-K — Rollback runner for gift_transaction_ledger migration.

Default: DRY-RUN. --commit requires env
DIVINE_ALLOW_AFFINITY_LEDGER_ROLLBACK=YES_I_UNDERSTAND.
Even with --commit + env, this script does NOT perform destructive DB
operations: it prints the steps and records a dry-run rehearsal result.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ENV_FLAG = 'DIVINE_ALLOW_AFFINITY_LEDGER_ROLLBACK'
ENV_TRUTHY = 'YES_I_UNDERSTAND'
ROOT = Path('/app')
RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_rollback_rehearsal_result_v1.json'
MIGRATION_RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_result_v1.json'

STEPS = [
    '1. Verify AFFINITY_GIFT_RUNTIME_ENABLED is OFF or set to non-allowlisted value.',
    '2. Confirm POST /api/affinity/gift-spend returns 423 on every region.',
    '3. Take DB snapshot before any correction.',
    '4. Drop partial unique index idx_idem_key_user_window if re-migration is required.',
    '5. Drop secondary indexes (idx_tx_id_unique, idx_user_created_desc, idx_gift_hero, idx_status_created) if needed.',
    '6. Drop the gift_transaction_ledger collection ONLY if explicitly approved by operator.',
    '7. Restore DB snapshot if data corruption is suspected (out-of-band).',
    '8. Smoke-test the runtime API: /api/heroes count == 100, Borea hidden, gift-spend disabled.'
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', action='store_true')
    args = ap.parse_args(argv)

    env_present = os.environ.get(ENV_FLAG) == ENV_TRUTHY
    dry_run = not (args.commit and env_present)

    if args.commit and not env_present:
        print(f'--commit refused: env {ENV_FLAG}={ENV_TRUTHY} not set; dry-run only.')

    print('AF2-K-ROLLBACK — gift_transaction_ledger rollback rehearsal')
    print('=' * 70)
    for s in STEPS:
        print(f'  {s}')

    timings = {
        'flag_flip_to_off_seconds_max': 5,
        'gift_spend_423_propagation_seconds_max': 30,
        'db_snapshot_minutes_max': 10,
        'index_drop_seconds_max': 60,
        'collection_drop_seconds_max': 30,
        'full_smoke_after_rollback_minutes_max': 5
    }

    result = {
        'rehearsal_id': 'AF2-L-REHEARSAL-001',
        'task_origin': 'AF2-L',
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'destructive_actions_performed': False,
        'dry_run': dry_run,
        'env_flag_required': ENV_FLAG,
        'env_flag_required_value': ENV_TRUTHY,
        'env_flag_present': env_present,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'rollback_steps_count': len(STEPS),
        'rollback_steps': STEPS,
        'timings_expected_seconds': timings,
        'operator_sign_off_required': True,
        'migration_result_referenced': str(MIGRATION_RESULT),
        'safety_flags': {
            'runtime_attached': False,
            'db_write': False,
            'feature_flag_currently_enabled': False,
            'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia']
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n',
                      encoding='utf-8')
    print(f'Result: {RESULT}')
    print(f'dry_run={dry_run}  destructive_actions_performed=False')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
