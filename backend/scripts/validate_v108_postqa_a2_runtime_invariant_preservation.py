#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_runtime_invariant_preservation_v1.json'),encoding='utf-8'))
runner=open(os.path.join(R,'backend','scripts','run_hero_skill_kit_validator_suite.py'),encoding='utf-8').read()
required=d.get('required_invariant_validators') or []
if len(required)<10: print('FAIL too few invariants'); sys.exit(1)
for v in required:
    p=os.path.join(R,'backend','scripts',v)
    if not os.path.isfile(p): print(f'FAIL missing {v}'); sys.exit(1)
    if v not in runner: print(f'FAIL not registered: {v}'); sys.exit(1)
for flag in ('all_present_and_registered','all_passing'):
    if not d.get(flag,False): print(f'FAIL flag {flag}'); sys.exit(1)
for flag in ('any_invariant_deleted','any_invariant_downgraded','rollup_marker_claims_ready_falsely'):
    if d.get(flag,True): print(f'FAIL flag {flag}=true'); sys.exit(1)
if 'CONDITIONAL_BLOCKERS' not in (d.get('rollup_marker_verdict') or ''):
    print('FAIL rollup_marker_verdict not CONDITIONAL_BLOCKERS'); sys.exit(1)
print('PASS — v108_POSTQA_A2 runtime invariant preservation (10/10 invariants + rollup, no drift)'); sys.exit(0)
