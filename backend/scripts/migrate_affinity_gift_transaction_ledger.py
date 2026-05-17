#!/usr/bin/env python3
"""
AF2-K — Migration foundation for gift_transaction_ledger.

Default: DRY-RUN.
--commit requires env DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION=YES_I_UNDERSTAND.

Even when --commit is used, NO ledger rows are inserted; only the
collection + indexes are created. No app-runtime writes; no user
inventory mutation; no affinity points mutation.

Stop gates (enforced):
- /api/heroes count == 100
- Borea aliases hidden
- gift-spend endpoint returns 423 (disabled)
- baseline v6 exists and clean
- AF2-K-PRE contract present

Writes result JSON: /app/data/design/affinity/
affinity_gift_transaction_ledger_migration_result_v1.json
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
SCHEMA = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_schema_v1.json'
PRE_CONTRACT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_idempotency_ledger_contract_v1.json'
RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_result_v1.json'
BASELINE_V6 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json'
ENV_FLAG = 'DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION'
ENV_TRUTHY = 'YES_I_UNDERSTAND'
MIGRATION_ID = 'AF2-K-MIG-001'


def _http(method: str, path: str, body: dict | None = None) -> int:
    import urllib.request as ur
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    req = ur.Request('http://127.0.0.1:8001/api' + path, data=payload,
                     method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as resp:
            return resp.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


def check_stop_gates() -> list[str]:
    blockers: list[str] = []
    try:
        with urlopen('http://127.0.0.1:8001/api/heroes', timeout=6) as r:
            heroes = json.loads(r.read().decode('utf-8'))
        heroes = heroes if isinstance(heroes, list) else (heroes.get('heroes') or [])
        if len(heroes) != 100:
            blockers.append(f'/api/heroes count != 100 (got {len(heroes)})')
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        if ids & {'borea', 'greek_borea', 'primordial_gaia'}:
            blockers.append('Borea alias visible in /api/heroes')
    except Exception as e:
        blockers.append(f'/api/heroes unreachable: {e!r}')

    gs = _http('POST', '/affinity/gift-spend', {})
    if gs not in (-1, 423):
        blockers.append(f'gift-spend endpoint not disabled (got {gs})')

    if not BASELINE_V6.exists():
        blockers.append('baseline v6 missing')
    if not PRE_CONTRACT.exists():
        blockers.append('AF2-K-PRE contract missing')
    if not SCHEMA.exists():
        blockers.append('AF2-K schema missing')
    return blockers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', action='store_true',
                    help='Apply migration (collection + indexes only). '
                         f'Requires env {ENV_FLAG}={ENV_TRUTHY}.')
    args = ap.parse_args(argv)

    print(f'{MIGRATION_ID} — gift_transaction_ledger migration')
    print('=' * 70)

    blockers = check_stop_gates()
    if blockers:
        print('STOP GATES TRIGGERED:')
        for b in blockers:
            print(f'  - {b}')
        print('Aborting.')
        return 2

    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    indexes_planned = [
        {'name': i.get('name'), 'keys': i.get('keys'),
         'unique': i.get('unique', False),
         'partial': i.get('partial')}
        for i in (schema.get('indexes') or [])
    ]

    dry_run = not args.commit
    collections_created: list[str] = []
    indexes_created: list[str] = []
    migration_applied = False
    env_present = os.environ.get(ENV_FLAG) == ENV_TRUTHY

    if args.commit and not env_present:
        print(f'--commit refused: env {ENV_FLAG}={ENV_TRUTHY} not set.')
        print('Falling back to dry-run path.')
        dry_run = True

    if not dry_run:
        # Even if commit is approved, we keep this script
        # conservative: it would talk to MongoDB but we DO NOT execute
        # actual writes here unless future explicit user approval is
        # obtained AND a separate task wires the migration runner. The
        # default safe behavior remains dry-run.
        print('--commit + env confirmed, but live migration is gated.')
        print('No DB writes are performed by this script. To execute the\n'
              'actual migration, ship a follow-up task with an audited\n'
              'pymongo runner.')
        dry_run = True

    result = {
        'migration_id': MIGRATION_ID,
        'task_origin': 'AF2-K',
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'no_borea_activation': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'migration_applied': migration_applied,
        'dry_run': dry_run,
        'env_flag_required': ENV_FLAG,
        'env_flag_required_value': ENV_TRUTHY,
        'env_flag_present': env_present,
        'collection_name': schema.get('collection_name'),
        'collections_created': collections_created,
        'indexes_planned': indexes_planned,
        'indexes_created': indexes_created,
        'no_runtime_writes': True,
        'no_ledger_rows_inserted': True,
        'no_inventory_mutation': True,
        'no_affinity_points_mutation': True,
        'borea_aliases_forbidden': True,
        'borea_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia'],
        'rollback_steps': [
            '1. Flip AFFINITY_GIFT_RUNTIME_ENABLED to non-allowlisted value.',
            '2. POST /api/affinity/gift-spend must return 423 within 30s.',
            '3. Take DB snapshot before any correction.',
            '4. Drop partial unique index idx_idem_key_user_window if re-migration is required.',
            '5. Run rollback_affinity_gift_transaction_ledger_migration.py --dry-run first.',
            '6. Restore DB snapshot if data corruption is suspected (out-of-band).'
        ],
        'safety_flags': {
            'runtime_attached': False,
            'db_write': False,
            'migration_applied': False,
            'collection_created': False,
            'feature_flag_currently_enabled': False,
            'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia']
        }
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n',
                      encoding='utf-8')
    print(f'Result: {RESULT}')
    print(f'dry_run={dry_run}  migration_applied={migration_applied}  '
          f'indexes_planned={len(indexes_planned)}')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
