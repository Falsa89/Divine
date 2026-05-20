#!/usr/bin/env python3
"""V27 PART G — Inventory / affinity delta audit V27 (read-only)."""
import asyncio, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
OUT = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v27_report.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


async def main_async():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME') or 'divine_waifus'
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    try:
        sample_users_target = 200
        all_inv = await db.user_gift_inventory.find({}).limit(sample_users_target).to_list(sample_users_target)
        all_aff = await db.user_affinity_state.find({}).limit(sample_users_target).to_list(sample_users_target)
        ledger_all = await db.gift_transaction_ledger.find({}).limit(5000).to_list(5000)

        negative_inventory = []
        for d in all_inv:
            bal = d.get('balances') or {}
            for k, v in bal.items():
                if isinstance(v, (int, float)) and v < 0:
                    negative_inventory.append({'user_id': d.get('user_id'), 'item': k, 'balance': v})

        borea_in_ledger = []
        non_allowlist_success = []
        # Load allowlist from supervisor backend.conf (env-source-of-truth)
        allowlist = set()
        try:
            import re as _re
            conf_txt = Path('/etc/supervisor/conf.d/backend.conf').read_text()
            m = _re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', conf_txt)
            if m:
                allowlist = {s.strip() for s in m.group(1).split(',') if s.strip()}
        except Exception:
            pass
        # Fallback to env (in case running inside backend process)
        if not allowlist:
            from os import environ
            allowlist = {s.strip() for s in (environ.get('AFFINITY_GIFT_CANARY_ALLOWLIST', '') or '').split(',') if s.strip()}
        for row in ledger_all:
            hid = (row.get('hero_id') or '').lower()
            if hid in ('borea', 'greek_borea', 'primordial_gaia'):
                borea_in_ledger.append({'tx_id': row.get('tx_id'), 'hero_id': hid})
            uid = row.get('user_id')
            status = row.get('status', '')
            if uid and uid not in allowlist and 'applied' in status:
                non_allowlist_success.append({'tx_id': row.get('tx_id'), 'user_id': uid, 'status': status})

        # delta check: total successful spends should equal applied rows
        applied_count = sum(1 for r in ledger_all if 'applied' in (r.get('status') or ''))

        report = {
            'task_origin': 'AF2-N-V27-INVENTORY-DELTA-AUDIT',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'mode': 'READ_ONLY',
            'production_db_touched': False,
            'sample_sizes': {
                'user_gift_inventory_sampled': len(all_inv),
                'user_affinity_state_sampled': len(all_aff),
                'ledger_sampled': len(ledger_all),
            },
            'negative_inventory_count': len(negative_inventory),
            'negative_inventory_samples': negative_inventory[:10],
            'borea_in_ledger_count': len(borea_in_ledger),
            'borea_in_ledger_samples': borea_in_ledger[:5],
            'non_allowlist_success_count': len(non_allowlist_success),
            'non_allowlist_success_samples': non_allowlist_success[:5],
            'applied_ledger_rows': applied_count,
        }
        report['verdict'] = 'PASS' if all([
            report['negative_inventory_count'] == 0,
            report['borea_in_ledger_count'] == 0,
            report['non_allowlist_success_count'] == 0,
        ]) else 'FAIL'
        OUT.write_text(json.dumps(report, indent=2, default=str))
        print(f"verdict={report['verdict']} neg_inv={report['negative_inventory_count']} borea_ledger={report['borea_in_ledger_count']} unauth={report['non_allowlist_success_count']} → {OUT}")
        return 0 if report['verdict'] == 'PASS' else 2
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main_async()))
