#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_watchlist_equipment_equip_added_v1.json')))
if d.get('endpoints_count_after',0)<23: print('FAIL endpoints<23'); sys.exit(1)
ep=d.get('endpoint_added') or {}
if ep.get('endpoint')!='/api/equipment/equip': print('FAIL endpoint mismatch'); sys.exit(1)
if ep.get('priority') not in ('P0','P1'): print('FAIL priority'); sys.exit(1)
if ep.get('status')!='tracked_pending_fix': print('FAIL status'); sys.exit(1)
if not ep.get('target_pack'): print('FAIL target_pack'); sys.exit(1)
if not d.get('all_required_endpoints_present',False): print('FAIL all_required'); sys.exit(1)
if d.get('missing_endpoints'): print('FAIL missing not empty'); sys.exit(1)
if d.get('endpoint_not_resolved',False) is not True: print('FAIL endpoint_not_resolved must be true'); sys.exit(1)
# Verify watchlist file actually contains the endpoint
wf=os.path.join(R,'data','design','postqa','v108_postqa_legacy_mutation_watchlist_v1.json')
w=json.load(open(wf))
eps=[e.get('endpoint') for e in (w.get('endpoints') or [])]
if '/api/equipment/equip' not in eps: print('FAIL not in actual watchlist'); sys.exit(1)
if len(eps)<23: print(f'FAIL watchlist<23 ({len(eps)})'); sys.exit(1)
print(f'PASS — v108_POSTQA_B watchlist /api/equipment/equip added ({len(eps)} endpoints)'); sys.exit(0)
