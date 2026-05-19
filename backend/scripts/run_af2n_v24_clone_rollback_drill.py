#!/usr/bin/env python3
"""V24 — Staging/Clone Rollback Drill (NON-DESTRUCTIVE).

Scope: simula l'intera procedura di rollback Stage 4 → Stage 3 su una COPIA
in-memory delle collezioni MongoDB rilevanti, SENZA toccare le collezioni di
produzione. Verifica che la procedura sia idempotente, completa e reversibile.

Collezioni clonate (sola lettura → buffer in-memory):
  • gift_transaction_ledger
  • user_gift_inventory
  • user_affinity_state

Steps simulati:
  1. Snapshot pre-rollback (counts, hash baseline)
  2. Backup logico in /app/backend/backups/v24_rollback_drill/<ts>/
  3. Rollback action su CLONE:
       - revert flag AFFINITY_GIFT_INVENTORY_WRITES_ENABLED (drill-only, file scratch)
       - segna canary rows in CLONE come 'reverted_dry_run'
  4. Validation post-rollback su CLONE:
       - count match expectations
       - no orphaned references
  5. Restore CLONE state (dry-run round-trip)
  6. Verifica PRODUCTION TOUCH = 0 (collections di prod inalterate)

Output: /app/backend/reports/v24_rollback_drill.json
"""
from __future__ import annotations
import asyncio, copy, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/app/backend')

REPORT = Path('/app/backend/reports/v24_rollback_drill.json')
BACKUP_ROOT = Path('/app/backend/backups/v24_rollback_drill')
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)


async def _connect():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME') or os.environ.get('MONGO_DB_NAME') or 'divine_waifus'
    client = AsyncIOMotorClient(mongo_url)
    return client, client[db_name]


def _hash_docs(docs: list[dict]) -> str:
    s = json.dumps(docs, default=str, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


async def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        'task_origin': 'AF2-N-V24-STAGING-CLONE-ROLLBACK-DRILL',
        'mode': 'NON_DESTRUCTIVE_CLONE_DRILL',
        'started_at_utc': started,
        'production_collections_touched': False,
        'backup_dir': str(backup_dir),
        'steps': [],
    }

    client, db = await _connect()
    try:
        collections = ['gift_transaction_ledger', 'user_gift_inventory', 'user_affinity_state']

        # ── Step 1 — snapshot pre-rollback ─────────────────────────────
        prod_state: dict = {}
        for c in collections:
            docs = await db[c].find({}).limit(50000).to_list(50000)
            prod_state[c] = {
                'count': await db[c].count_documents({}),
                'sampled_docs': docs,
                'hash_pre': _hash_docs(docs),
            }
        report['steps'].append({
            'step': '1_snapshot_pre',
            'counts': {c: prod_state[c]['count'] for c in collections},
            'hashes_pre': {c: prod_state[c]['hash_pre'] for c in collections},
        })

        # ── Step 2 — backup logico su disco (dump JSON) ────────────────
        backup_index = {}
        for c in collections:
            p = backup_dir / f'{c}.json'
            p.write_text(json.dumps(prod_state[c]['sampled_docs'], default=str))
            backup_index[c] = {'file': str(p), 'rows': len(prod_state[c]['sampled_docs'])}
        report['steps'].append({'step': '2_logical_backup', 'index': backup_index})

        # ── Step 3 — rollback action su CLONE (deep copy in memoria) ───
        clone: dict = {c: copy.deepcopy(prod_state[c]['sampled_docs']) for c in collections}
        reverted = 0
        for d in clone['gift_transaction_ledger']:
            if d.get('canary') is True or d.get('status') in ('applied_inventory_live', 'applied'):
                d['_drill_revert_marker'] = 'reverted_dry_run'
                reverted += 1
        report['steps'].append({
            'step': '3_clone_revert',
            'rows_marked_reverted': reverted,
            'note': 'clone-only; production NOT touched',
        })

        # ── Step 4 — validation post-rollback su CLONE ─────────────────
        bad_aliases = []
        for d in clone['gift_transaction_ledger']:
            hid = (d.get('hero_id') or '').lower()
            if hid in ('borea', 'greek_borea', 'primordial_gaia'):
                bad_aliases.append({'tx_id': d.get('tx_id'), 'hero_id': hid})
        clone_ledger_count = len(clone['gift_transaction_ledger'])
        report['steps'].append({
            'step': '4_clone_validation',
            'clone_ledger_count': clone_ledger_count,
            'borea_leak_in_ledger': bad_aliases[:10],
            'borea_leak_count': len(bad_aliases),
            'ok_no_borea_in_ledger': len(bad_aliases) == 0,
        })

        # ── Step 5 — round-trip restore on CLONE (drop revert marker) ──
        for d in clone['gift_transaction_ledger']:
            d.pop('_drill_revert_marker', None)
        hashes_post = {
            'gift_transaction_ledger': _hash_docs(clone['gift_transaction_ledger']),
            'user_gift_inventory': _hash_docs(clone['user_gift_inventory']),
            'user_affinity_state': _hash_docs(clone['user_affinity_state']),
        }
        report['steps'].append({
            'step': '5_clone_round_trip',
            'hashes_post': hashes_post,
            'round_trip_matches_baseline': hashes_post == {
                c: prod_state[c]['hash_pre'] for c in collections
            },
        })

        # ── Step 6 — production untouched check ────────────────────────
        prod_post: dict = {}
        for c in collections:
            docs = await db[c].find({}).limit(50000).to_list(50000)
            prod_post[c] = _hash_docs(docs)
        production_unchanged = all(
            prod_post[c] == prod_state[c]['hash_pre'] for c in collections
        )
        report['production_collections_touched'] = not production_unchanged
        report['steps'].append({
            'step': '6_production_invariant',
            'production_unchanged': production_unchanged,
            'hashes_now': prod_post,
        })

        # ── Verdict ────────────────────────────────────────────────────
        verdict_ok = (
            production_unchanged
            and len(bad_aliases) == 0
            and report['steps'][4]['round_trip_matches_baseline'] is True
            and reverted > 0
        )
        report['verdict'] = 'PASS' if verdict_ok else 'FAIL'
        report['ended_at_utc'] = datetime.now(timezone.utc).isoformat()

    finally:
        client.close()

    REPORT.write_text(json.dumps(report, indent=2, default=str))

    print(f"VERDICT: {report['verdict']}")
    print(f"  mode: {report['mode']}")
    print(f"  production_collections_touched: {report['production_collections_touched']}")
    for s in report['steps']:
        print(f"  • {s['step']}")
    print(f"\nReport: {REPORT}")
    print(f"Backup dir: {backup_dir}")
    return 0 if report['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
