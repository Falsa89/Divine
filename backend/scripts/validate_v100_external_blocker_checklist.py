#!/usr/bin/env python3
"""v100 — External blocker checklist validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_external_blocker_checklist_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
for section in ('google_apple_credentials','privacy_terms_account_deletion_urls','physical_mobile_qa','full_load_locust_1000','store_internal_testing'):
    if section not in d: print(f'FAIL \u2014 section {section} missing'); sys.exit(1)
gac = d['google_apple_credentials']
if len(gac.get('required_env_vars', [])) < 7: print('FAIL \u2014 google/apple env_vars < 7'); sys.exit(1)
pmqa = d['physical_mobile_qa']
if len(pmqa.get('android_checklist', [])) < 8: print('FAIL \u2014 android_checklist < 8'); sys.exit(1)
if len(pmqa.get('ios_checklist', [])) < 8: print('FAIL \u2014 ios_checklist < 8'); sys.exit(1)
load = d['full_load_locust_1000']
if not load.get('locust_command'): print('FAIL \u2014 locust_command missing'); sys.exit(1)
store = d['store_internal_testing']
if len(store.get('google_play_internal_track', [])) < 5: print('FAIL \u2014 google_play_internal_track < 5'); sys.exit(1)
if len(store.get('apple_testflight_track', [])) < 5: print('FAIL \u2014 apple_testflight_track < 5'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_credentials','fake_mobile_qa','fake_load_result','fake_store_readiness','commercial_release_claim'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v100 external blocker checklist (5 sections, complete)")
sys.exit(0)
