#!/usr/bin/env python3
"""v98 — Bot chat runtime intent classifier + fixtures."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p1=os.path.join(ROOT,'data','design','server_actors','v98_bot_chat_runtime_intent_classifier_v1.json')
p2=os.path.join(ROOT,'data','design','server_actors','v98_bot_chat_runtime_fixture_result_v1.json')
for p in (p1,p2):
    if not os.path.isfile(p): print(f'FAIL — missing: {p}'); sys.exit(1)
with open(p1,'r',encoding='utf-8') as f: d1=json.load(f)
with open(p2,'r',encoding='utf-8') as f: d2=json.load(f)
feat=d1.get('classifier_features') or {}
for k in ('mentioned_hero_detection','direct_question_detection','out_of_context_response_forbidden','manual_ultimate_advice_forbidden'):
    if not feat.get(k): print(f'FAIL — feature {k}'); sys.exit(1)
fix=d2.get('fixtures_executed') or []
if len(fix)<7: print(f'FAIL — fixtures count {len(fix)}<7'); sys.exit(1)
ids=[f['id'] for f in fix]
if 'borea_question' not in ids: print('FAIL — borea_question missing'); sys.exit(1)
borea=next(f for f in fix if f['id']=='borea_question')
if borea.get('acceptance')!='PASS': print('FAIL — borea fixture not PASS'); sys.exit(1)
resp=borea.get('chosen_response','').lower()
for bad in ['tieni l\'ultimate','ultimate per dopo','sono le 8','attiva ultimate','premi ultimate']:
    if bad in resp: print(f'FAIL — borea response contains forbidden: {bad}'); sys.exit(1)
for f in fix:
    if f.get('acceptance','').startswith('PASS')==False: print(f'FAIL — fixture not PASS: {f["id"]}'); sys.exit(1)
print(f'PASS — v98 bot chat runtime intent classifier ({len(fix)} fixtures)')
sys.exit(0)
