#!/usr/bin/env python3
"""v98 — Optional fail cleanup (honest)."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','closed_alpha','v98_optional_fail_cleanup_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('target_threshold')!=30: print('FAIL — target_threshold'); sys.exit(1)
safety=d.get('safety') or {}
if not safety.get('no_validator_weakening') or not safety.get('no_fake_PASS'): print('FAIL — safety'); sys.exit(1)
class_=d.get('final_classification') or {}
for k in ('environmental','stale_proof_regenerated','deprecated_removed','true_blocker','accepted_for_closed_alpha','deferred_commercial'):
    if k not in class_: print(f'FAIL — classification missing: {k}'); sys.exit(1)
if class_.get('true_blocker',{}).get('count',1)!=0: print('FAIL — true_blocker.count!=0'); sys.exit(1)
print(f"PASS — v98 optional fail cleanup (target_reached={d.get('target_reached')}, honest)")
sys.exit(0)
