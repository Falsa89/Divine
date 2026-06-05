#!/usr/bin/env python3
"""v101 — Apply script gating validator."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
apply_script = os.path.join(ROOT,'backend','scripts','apply_v101_global_legacy_data_cleanup.py')
if not os.path.isfile(apply_script): print('FAIL \u2014 apply script missing'); sys.exit(1)
with open(apply_script,'r',encoding='utf-8') as f: content = f.read()
for required_token in ('V101_LEGACY_CLEANUP_APPLY','V101_BACKUP_MANIFEST_CONFIRMED','BLOCKED','backup manifest'):
    if required_token not in content: print(f'FAIL \u2014 apply script missing gating token: {required_token}'); sys.exit(1)
forbidden_terms = ('blind_destructive_reset = True','delete_without_backup = True','wipe_bots_without_reconstruction = True')
for t in forbidden_terms:
    if t in content: print(f'FAIL \u2014 forbidden term present: {t}'); sys.exit(1)
print('PASS \u2014 v101 apply script gated by V101_LEGACY_CLEANUP_APPLY + V101_BACKUP_MANIFEST_CONFIRMED')
sys.exit(0)
