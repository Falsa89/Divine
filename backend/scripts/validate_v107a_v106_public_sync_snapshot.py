#!/usr/bin/env python3
"""v107A — v106 public sync snapshot validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_acceleration', 'v107a_v106_public_sync_snapshot_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
art = d.get('v106_artifacts_present') or {}
if len(art) < 14: print(f'FAIL \u2014 v106 artifacts < 14 (got {len(art)})'); sys.exit(1)
for f, present in art.items():
    full = os.path.join(ROOT, f)
    if present and not os.path.exists(full): print(f'FAIL \u2014 declared present but missing: {f}'); sys.exit(1)
if d.get('v106_psp_apply_executed', True): print('FAIL \u2014 v106_psp_apply_executed must be false'); sys.exit(1)
if d.get('v106_db_writes_performed', -1) != 0: print('FAIL \u2014 v106_db_writes_performed must be 0'); sys.exit(1)
if d.get('backend_isolation_live', True): print('FAIL \u2014 backend_isolation_live must be false'); sys.exit(1)
saf = d.get('safety') or {}
if saf.get('claim_isolation_live', True): print('FAIL \u2014 safety.claim_isolation_live must be false'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v107A v106 public sync snapshot ({len(art)} artifacts verified)")
sys.exit(0)
