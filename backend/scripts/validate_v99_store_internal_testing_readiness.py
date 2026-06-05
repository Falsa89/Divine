#!/usr/bin/env python3
"""v99 — Store internal testing readiness matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v99_store_internal_testing_readiness_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
for section in ('google_play_internal_testing', 'apple_testflight', 'expo_eas_build'):
    if section not in d:
        print(f'FAIL \u2014 section {section} missing'); sys.exit(1)
for section in ('google_play_internal_testing', 'apple_testflight'):
    s = d[section]
    if s.get('iap_status') != 'DISABLED':
        print(f'FAIL \u2014 {section}.iap_status not DISABLED'); sys.exit(1)
    if s.get('push_notifications_status') != 'DISABLED':
        print(f'FAIL \u2014 {section}.push_notifications_status not DISABLED'); sys.exit(1)
    if s.get('ads_status') != 'DISABLED':
        print(f'FAIL \u2014 {section}.ads_status not DISABLED'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('iap_active', 'push_active', 'ads_active', 'commercial_release_claim', 'fake_store_readiness'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v99 store internal testing readiness (verdict={d.get('verdict')})")
sys.exit(0)
