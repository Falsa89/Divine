#!/usr/bin/env python3
"""AF2-L-FULL — rollback rehearsal (FULL). Dry-run unless
DIVINE_ALLOW_AFFINITY_LEDGER_ROLLBACK=YES_I_UNDERSTAND.
In dry-run NO destructive op; records plan with all 5 indexes."""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

RESULT = Path('/app/data/design/affinity/affinity_gift_transaction_ledger_rollback_rehearsal_full_result_v1.json')
COMMIT = Path('/app/data/design/affinity/affinity_gift_transaction_ledger_migration_commit_result_v1.json')
ENV_FLAG = 'DIVINE_ALLOW_AFFINITY_LEDGER_ROLLBACK'
ENV_TRUTHY = 'YES_I_UNDERSTAND'

STEPS = [
    '1. Verify AFFINITY_GIFT_RUNTIME_ENABLED is OFF.',
    '2. Verify POST /api/affinity/gift-spend returns 423.',
    '3. Take DB snapshot.',
    '4. Drop partial unique idx_idem_key_user_window.',
    '5. Drop idx_tx_id_unique.',
    '6. Drop idx_user_created_desc.',
    '7. Drop idx_gift_hero.',
    '8. Drop idx_status_created.',
    '9. Drop collection gift_transaction_ledger only if explicitly approved.',
    '10. Restore DB snapshot if data corruption suspected (out-of-band).',
    '11. Smoke-test: /api/heroes==100, Borea hidden, gift-spend 423.'
]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', action='store_true')
    args = ap.parse_args(argv)
    env_present = os.environ.get(ENV_FLAG) == ENV_TRUTHY
    dry_run = not (args.commit and env_present)
    if args.commit and not env_present:
        print(f'--commit refused: env {ENV_FLAG}={ENV_TRUTHY} not set; dry-run only.')

    commit_state = {}
    if COMMIT.exists():
        cd = json.loads(COMMIT.read_text())
        commit_state = {'migration_applied': cd.get('migration_applied'),
                        'collections_created': cd.get('collections_created'),
                        'indexes_created': cd.get('indexes_created'),
                        'blocked_by_missing_env': cd.get('blocked_by_missing_env')}

    result = {
        'rehearsal_id': 'AF2-L-FULL-REHEARSAL-001',
        'task_origin': 'AF2-L-FULL',
        'design_only': True, 'runtime_attached': False, 'db_write': False,
        'destructive_actions_performed': False, 'dry_run': dry_run,
        'env_flag_required': ENV_FLAG, 'env_flag_required_value': ENV_TRUTHY,
        'env_flag_present': env_present,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'rollback_steps_count': len(STEPS), 'rollback_steps': STEPS,
        'commit_state_referenced': commit_state,
        'timings_expected_seconds': {'flag_flip_to_off': 5, 'index_drop': 60,
                                     'collection_drop': 30, 'full_smoke_after': 300},
        'operator_sign_off_required': True,
        'safety_flags': {'runtime_attached': False, 'db_write': False,
                         'feature_flag_currently_enabled': False,
                         'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia']}
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-L-FULL rehearsal: dry_run={dry_run} destructive=False')
    return 0

if __name__ == '__main__':
    sys.exit(main())
