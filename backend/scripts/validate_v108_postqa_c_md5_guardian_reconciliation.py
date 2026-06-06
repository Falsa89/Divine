#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_md5_guardian_reconciliation_v1.json')))
if d.get('total_guardians',0)<3: print('FAIL <3 guardians'); sys.exit(1)
if not d.get('all_guardians_have_replacement_invariant',False): print('FAIL not all have replacement'); sys.exit(1)
if d.get('replacement_invariant_pass_count',0)<d.get('total_guardians',0): print('FAIL not all replacements pass'); sys.exit(1)
if d.get('supersede_applied_in_c',-1)!=0: print('FAIL supersede>0'); sys.exit(1)
if d.get('deletions_applied_in_c',-1)!=0: print('FAIL deletions>0'); sys.exit(1)
for g in d.get('guardians') or []:
    if not g.get('replacement_invariant'): print(f'FAIL no replacement {g.get("validator_id")}'); sys.exit(1)
    if not g.get('historical_references_preserved',False): print(f'FAIL hist not preserved {g.get("validator_id")}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','cosmetic_supersede'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
if not saf.get('old_hash_preserved_as_historical_reference',False): print('FAIL old_hash_preserved'); sys.exit(1)
print(f'PASS — v108_POSTQA_C MD5 guardian reconciliation ({d.get("total_guardians")} guardians with replacement invariant)'); sys.exit(0)
