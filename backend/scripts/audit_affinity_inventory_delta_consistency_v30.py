#!/usr/bin/env python3
"""V30 PART H — Delta audit V30 (READ-ONLY)."""
import asyncio, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
OUT = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v30_report.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


async def main_async():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    try:
        allowlist=set()
        try:
            conf=Path('/etc/supervisor/conf.d/backend.conf').read_text()
            m=re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"',conf)
            if m: allowlist={s.strip() for s in m.group(1).split(',') if s.strip()}
        except Exception: pass
        inv_all = await db.user_gift_inventory.find({}).to_list(5000)
        aff_all = await db.user_affinity_state.find({}).to_list(5000)
        ledger_all = await db.gift_transaction_ledger.find({}).to_list(60000)
        neg=[]
        for d in inv_all:
            q=d.get('quantity')
            if isinstance(q,(int,float)) and q<0:
                neg.append({'user_id':d.get('user_id'),'gift_id':d.get('gift_id'),'quantity':q})
        borea_lg=[]; unauth=[]; dup=[]; seen={}
        for r in ledger_all:
            hid=(r.get('hero_id') or '').lower()
            if hid in ('borea','greek_borea','primordial_gaia'):
                borea_lg.append({'tx_id':r.get('tx_id'),'hero_id':hid})
            uid=r.get('user_id'); st=r.get('status','')
            if uid and uid not in allowlist and 'applied' in st:
                unauth.append({'tx_id':r.get('tx_id'),'user_id':uid,'status':st})
            idem=r.get('idempotency_key')
            if idem and uid:
                k=(uid,idem)
                if k in seen and 'applied' in st and 'applied' in seen[k]:
                    dup.append({'user_id':uid,'idempotency_key':idem})
                seen[k]=st
        marker_inv=await db.user_gift_inventory.count_documents({'meta.v28_scope_s1':True})
        marker_aff=await db.user_affinity_state.count_documents({'meta.v28_scope_s1':True})
        nested_v28=await db.user_gift_inventory.count_documents({'meta.v28_scope_s1':True,'balances':{'$exists':True}})
        flat_v28=await db.user_gift_inventory.count_documents({'meta.v28_scope_s1':True,'gift_id':{'$exists':True},'quantity':{'$exists':True}})
        borea_in_marker=await db.user_affinity_state.count_documents({'meta.v28_scope_s1':True,'hero_id':{'$in':['borea','greek_borea','primordial_gaia']}})
        applied=sum(1 for r in ledger_all if 'applied' in (r.get('status') or ''))
        report={
            'task_origin':'AF2-N-V30-INVENTORY-DELTA-AUDIT',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'mode':'READ_ONLY_FULL',
            'production_db_touched': False,
            'allowlist_size_from_conf': len(allowlist),
            'sample_sizes':{'inventory':len(inv_all),'affinity_state':len(aff_all),'ledger':len(ledger_all)},
            'negative_inventory_count': len(neg),
            'borea_in_ledger_count': len(borea_lg),
            'borea_in_marker_aff_count': borea_in_marker,
            'non_allowlist_success_count': len(unauth),
            'non_allowlist_success_samples': unauth[:5],
            'idempotency_dup_mutation_count': len(dup),
            'applied_ledger_rows': applied,
            'v28_scope_marker_inventory_count': marker_inv,
            'v28_scope_marker_affinity_count': marker_aff,
            'v28_scope_marker_nested_count': nested_v28,
            'v28_scope_marker_flat_count': flat_v28,
        }
        report['verdict']='PASS' if all([
            report['negative_inventory_count']==0,
            report['borea_in_ledger_count']==0,
            report['borea_in_marker_aff_count']==0,
            report['non_allowlist_success_count']==0,
            report['idempotency_dup_mutation_count']==0,
            nested_v28==0, flat_v28>=1800,
        ]) else 'FAIL'
        OUT.write_text(json.dumps(report, indent=2, default=str))
        print(f"verdict={report['verdict']} neg={len(neg)} borea_lg={len(borea_lg)} unauth={len(unauth)} dup={len(dup)} marker_inv={marker_inv} flat={flat_v28} nested={nested_v28}")
        return 0 if report['verdict']=='PASS' else 2
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main_async()))
