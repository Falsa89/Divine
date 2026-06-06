#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_project_preexisting_fail_classification_v1.json')))
if d.get('total_classified',0)<17: print('FAIL <17 classified'); sys.exit(1)
if d.get('supersede_applied_in_b',-1)!=0: print('FAIL supersede applied'); sys.exit(1)
if d.get('deletions_applied_in_b',-1)!=0: print('FAIL deletions applied'); sys.exit(1)
classifications=d.get('classifications') or []
allowed_decisions={'keep_failing','deferred_to_v108_authoritative','deferred_to_v108_POSTQA_C','deferred_to_v109_social_isolation','deferred_to_v110_economy_migration','historical_guardian_to_reconcile_later','obsolete_but_not_removed','closed_by_redis_install'}
for c in classifications:
    if c.get('decision') not in allowed_decisions: print(f'FAIL bad decision {c.get("decision")}'); sys.exit(1)
    if not c.get('root_cause'): print(f'FAIL missing root_cause {c.get("validator_id")}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('supersede_applied','deletions_applied','fake_PASS','validator_weakening','silent_validator_deletion'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print(f'PASS — v108_POSTQA_B 17 PROJECT-* preexisting classified ({len(classifications)})'); sys.exit(0)
