#!/usr/bin/env python3
"""V28 PART E — Delta audit V28 (READ-ONLY)."""
import asyncio, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
OUT = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v28_report.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


async def main_async():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    try:
        inv_all = await db.user_gift_inventory.find({}).limit(5000).to_list(5000)
        aff_all = await db.user_affinity_state.find({}).limit(5000).to_list(5000)
        ledger_all = await db.gift_transaction_ledger.find({}).limit(10000).to_list(10000)

        # Allowlist from supervisor conf (source of truth)
        allowlist = set()
        try:
            conf_txt = Path('/etc/supervisor/conf.d/backend.conf').read_text()
            m = re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', conf_txt)
            if m:
                allowlist = {s.strip() for s in m.group(1).split(',') if s.strip()}
        except Exception:
            pass

        neg_inv = []
        for d in inv_all:
            bal = d.get('balances') or {}
            for k, v in bal.items():
                if isinstance(v, (int, float)) and v < 0:
                    neg_inv.append({'user_id': d.get('user_id'), 'item': k, 'balance': v})

        borea_in_ledger = []
        non_allowlist_success = []
        idempotency_dup_mut = []
        seen_idems = {}
        for row in ledger_all:
            hid = (row.get('hero_id') or '').lower()
            if hid in ('borea', 'greek_borea', 'primordial_gaia'):
                borea_in_ledger.append({'tx_id': row.get('tx_id'), 'hero_id': hid})
            uid = row.get('user_id')
            status = row.get('status', '')
            if uid and uid not in allowlist and 'applied' in status:
                non_allowlist_success.append({'tx_id': row.get('tx_id'), 'user_id': uid, 'status': status})
            idem = row.get('idempotency_key')
            if idem:
                if idem in seen_idems and 'applied' in status and 'applied' in seen_idems[idem]:
                    idempotency_dup_mut.append({'idempotency_key': idem})
                seen_idems[idem] = status

        # New scope V28 marker counts
        marker_inv = await db.user_gift_inventory.count_documents({'meta.v28_scope_s1': True})
        marker_aff = await db.user_affinity_state.count_documents({'meta.v28_scope_s1': True})
        borea_in_marker_aff = await db.user_affinity_state.count_documents({
            'meta.v28_scope_s1': True,
            'hero_id': {'$in': ['borea', 'greek_borea', 'primordial_gaia']},
        })

        applied_count = sum(1 for r in ledger_all if 'applied' in (r.get('status') or ''))
        report = {
            'task_origin': 'AF2-N-V28-INVENTORY-DELTA-AUDIT',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'mode': 'READ_ONLY',
            'production_db_touched': False,
            'allowlist_size_from_conf': len(allowlist),
            'sample_sizes': {
                'inventory': len(inv_all),
                'affinity_state': len(aff_all),
                'ledger': len(ledger_all),
            },
            'negative_inventory_count': len(neg_inv),
            'negative_inventory_samples': neg_inv[:10],
            'borea_in_ledger_count': len(borea_in_ledger),
            'borea_in_marker_aff_count': borea_in_marker_aff,
            'non_allowlist_success_count': len(non_allowlist_success),
            'non_allowlist_success_samples': non_allowlist_success[:5],
            'idempotency_dup_mutation_count': len(idempotency_dup_mut),
            'applied_ledger_rows': applied_count,
            'v28_scope_marker_inventory_count': marker_inv,
            'v28_scope_marker_affinity_count': marker_aff,
        }
        report['verdict'] = 'PASS' if all([
            report['negative_inventory_count'] == 0,
            report['borea_in_ledger_count'] == 0,
            report['borea_in_marker_aff_count'] == 0,
            report['non_allowlist_success_count'] == 0,
            report['idempotency_dup_mutation_count'] == 0,
        ]) else 'FAIL'
        OUT.write_text(json.dumps(report, indent=2, default=str))
        print(f"verdict={report['verdict']} neg={report['negative_inventory_count']} borea_ledger={report['borea_in_ledger_count']} unauth={report['non_allowlist_success_count']} dup={report['idempotency_dup_mutation_count']} marker_inv={marker_inv} marker_aff={marker_aff} → {OUT}")
        return 0 if report['verdict'] == 'PASS' else 2
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main_async()))
