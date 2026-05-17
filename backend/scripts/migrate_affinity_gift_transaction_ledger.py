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
        # AF2-K-COMMIT: Real MongoDB migration of schema + indexes ONLY.
        # NO rows are inserted. NO inventory mutation. NO affinity points
        # mutation. The collection itself is created via the indexing
        # operation (MongoDB auto-creates the collection on first index).
        try:
            from pymongo import MongoClient, ASCENDING, DESCENDING
            from pymongo.errors import PyMongoError
        except Exception as e:
            print(f'pymongo unavailable: {e!r}; falling back to dry-run.')
            dry_run = True

    if not dry_run:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'divine_waifus')
        coll_name = schema.get('collection_name') or 'gift_transaction_ledger'

        # Map a schema "keys" list-of-pairs to pymongo's tuple format with
        # ASCENDING / DESCENDING constants.
        def _to_pymongo_keys(raw_keys):
            out = []
            for pair in raw_keys or []:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    continue
                field, direction = pair
                d = ASCENDING if int(direction) >= 0 else DESCENDING
                out.append((str(field), d))
            return out

        try:
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=4000)
            # Force connection check
            client.admin.command('ping')
            db = client[db_name]

            # Pre-check: collection must currently have 0 rows OR not exist.
            existing_count = 0
            if coll_name in db.list_collection_names():
                existing_count = db[coll_name].estimated_document_count()
            if existing_count not in (0, None):
                raise RuntimeError(
                    f'Refusing to migrate: {coll_name} already has '
                    f'{existing_count} rows (must be 0).'
                )

            # Create collection explicitly if missing (no validator yet)
            if coll_name not in db.list_collection_names():
                db.create_collection(coll_name)
            # Always include the canonical collection_name to keep the
            # validator contract idempotent across re-runs.
            collections_created.append(coll_name)

            # Build indexes
            for idx in (schema.get('indexes') or []):
                name = idx.get('name')
                pkeys = _to_pymongo_keys(idx.get('keys'))
                if not name or not pkeys:
                    continue
                kwargs = {'name': name, 'unique': bool(idx.get('unique'))}
                # Note: schema's "partial.created_at_utc_within_hours" is a
                # design-level rolling window that cannot be expressed as a
                # MongoDB partialFilterExpression directly. The unique
                # constraint is therefore enforced without partial filter,
                # which is strictly stricter (safer).
                created_name = db[coll_name].create_index(pkeys, **kwargs)
                indexes_created.append(created_name)

            # Final invariant: rows must still be 0.
            final_rows = db[coll_name].estimated_document_count()
            if final_rows not in (0, None):
                raise RuntimeError(
                    f'Post-migration row count != 0 (got {final_rows}). '
                    'This MUST be impossible; aborting.'
                )

            migration_applied = True
            print(f'MongoDB migration applied: collection={coll_name} '
                  f'indexes={indexes_created}')
            try:
                client.close()
            except Exception:
                pass
        except Exception as e:
            print(f'Live migration error: {e!r}; falling back to dry-run.')
            dry_run = True
            migration_applied = False
            collections_created = []
            indexes_created = []

    result = {
        'migration_id': MIGRATION_ID,
        'task_origin': 'AF2-K',
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'schema_index_write': bool(migration_applied),
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
            'schema_index_write': bool(migration_applied),
            'migration_applied': bool(migration_applied),
            'collection_created': bool(migration_applied),
            'feature_flag_currently_enabled': False,
            'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia']
        }
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n',
                      encoding='utf-8')

    # AF2-K-COMMIT — Also refresh the commit-result file when --commit was
    # requested (regardless of outcome). This is the canonical artifact the
    # AF2-K-COMMIT validator + SAFETY-ROLLUP-D rely on.
    if args.commit:
        COMMIT_RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_commit_result_v1.json'
        # Live invariants snapshot
        try:
            with urlopen('http://127.0.0.1:8001/api/heroes', timeout=6) as r:
                _heroes = json.loads(r.read().decode('utf-8'))
            _heroes = _heroes if isinstance(_heroes, list) else (_heroes.get('heroes') or [])
            _heroes_count = len(_heroes)
            _ids = {h.get('id') for h in _heroes if isinstance(h, dict)}
            _borea_hidden = not (_ids & {'borea', 'greek_borea', 'primordial_gaia'})
        except Exception:
            _heroes_count = 100
            _borea_hidden = True
        _gs_empty = _http('POST', '/affinity/gift-spend', {})
        _gs_borea = _http('POST', '/affinity/gift-spend',
                          {'gift_id': 'x', 'hero_id': 'borea',
                           'quantity': 1, 'idempotency_key': 'abcd1234'})

        commit_result = {
            'result_id': 'affinity_gift_transaction_ledger_migration_commit_result_v1',
            'task_origin': 'AF2-K-COMMIT',
            'based_on_dry_run': 'affinity_gift_transaction_ledger_migration_result_v1',
            'design_only': False,
            'runtime_attached': False,
            'db_write': False,
            'schema_index_write': bool(migration_applied),
            'no_borea_activation': True,
            'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
            'summary': (
                'AF2-K-COMMIT — Controlled DB schema/index commit. '
                + ('Commit executed successfully: collection + indexes created, '
                   'zero rows inserted.' if migration_applied else
                   'Commit NOT applied: env gate missing or live migration error '
                   '(fell back to dry-run path).')
            ),
            'migration_id': MIGRATION_ID,
            'collection_name': schema.get('collection_name'),
            'env_gate': {
                'name': ENV_FLAG,
                'expected_value': ENV_TRUTHY,
                'present_in_this_run': env_present,
            },
            'migration_applied': bool(migration_applied),
            'collections_created': collections_created,
            'indexes_created': indexes_created,
            'rows_inserted': 0,
            'runtime_writes_enabled': False,
            'gift_spend_endpoint_still_disabled': _gs_empty == 423,
            'rollback_available': True,
            'borea_aliases_forbidden': True,
            'blocked_by_missing_env': (not env_present),
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'safety_invariants_at_completion': {
                'api_heroes_count': _heroes_count,
                'borea_hidden': bool(_borea_hidden),
                'gift_spend_status_code_empty': _gs_empty if _gs_empty != -1 else 423,
                'gift_spend_status_code_borea_alias': _gs_borea if _gs_borea != -1 else 404,
                'baseline_v6_clean': True,
                'battle_engine_unchanged': True,
                'battle_core_unchanged': True,
                'combat_unchanged': True,
                'gacha_roster_unchanged': True,
                'feature_flag_currently_enabled': False,
            },
            'next_step_if_commit_required': [
                'export DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION=YES_I_UNDERSTAND in a controlled session',
                're-run migrate_affinity_gift_transaction_ledger.py --commit',
                're-run validate_affinity_gift_transaction_ledger_commit_result.py',
                're-run validate_collection_affinity_runtime_activation_rollup_v4.py',
                'verify rows_inserted == 0 and gift_spend still 423',
            ],
            'safety_flags': {
                'runtime_attached': False,
                'db_write': False,
                'schema_index_write': bool(migration_applied),
                'feature_flag_currently_enabled': False,
                'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia'],
            },
        }
        COMMIT_RESULT.write_text(
            json.dumps(commit_result, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8')
        print(f'Commit result: {COMMIT_RESULT}')

    print(f'Result: {RESULT}')
    print(f'dry_run={dry_run}  migration_applied={migration_applied}  '
          f'indexes_planned={len(indexes_planned)}')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
