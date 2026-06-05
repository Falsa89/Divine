#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_md5_historical_reconciliation_v1.json'),encoding='utf-8'))
if d.get('validators_deleted'): print('FAIL validators_deleted not empty'); sys.exit(1)
if d.get('validators_weakened'): print('FAIL validators_weakened not empty'); sys.exit(1)
if d.get('blanket_supersede_applied',True): print('FAIL blanket_supersede'); sys.exit(1)
if d.get('runtime_p0_classified_as_historical',True): print('FAIL runtime_p0 misclassified'); sys.exit(1)
if not d.get('old_hashes_preserved_as_historical_reference',False): print('FAIL old_hashes_not_preserved'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','cosmetic_supersede'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
if not saf.get('old_hash_preserved_as_historical_reference',False): print('FAIL safety.old_hash_preserved'); sys.exit(1)
# Verify every deferred reconciliation has historical_md5 list and replacement_invariant
for r in d.get('reconciliation_actions_deferred_to_v108_postqa_b') or []:
    if not (r.get('historical_md5') and r.get('replacement_invariant')):
        print(f'FAIL deferred reconciliation incomplete: {r.get("file")}'); sys.exit(1)
print('PASS — v108_POSTQA_A2 MD5 historical reconciliation (deferrals documented, no cosmetic supersede)'); sys.exit(0)
