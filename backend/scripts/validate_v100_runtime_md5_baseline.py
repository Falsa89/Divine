#!/usr/bin/env python3
"""v100 — Runtime MD5 baseline validator."""
import os, sys, json, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_runtime_md5_baseline_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
files = d.get('files') or {}
if 'backend/battle_engine.py' not in files: print('FAIL \u2014 battle_engine.py missing'); sys.exit(1)
if 'backend/server.py' not in files: print('FAIL \u2014 server.py missing'); sys.exit(1)
# Verify current MD5 matches
for relpath, info in files.items():
    full = os.path.join(ROOT, relpath)
    if not os.path.isfile(full): continue
    with open(full,'rb') as fh: actual = hashlib.md5(fh.read()).hexdigest()
    if info.get('current_md5') != actual:
        print(f'FAIL \u2014 {relpath} current_md5 mismatch (actual={actual}, baseline={info.get("current_md5")})'); sys.exit(1)
# Verify historical references present for battle_engine
be = files['backend/battle_engine.py']
if not be.get('historical_references'): print('FAIL \u2014 historical_references missing for battle_engine'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_overwrite'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
if not saf.get('old_hash_preserved_as_historical_reference', False):
    print('FAIL \u2014 old_hash_preserved_as_historical_reference must be true'); sys.exit(1)
print(f"PASS \u2014 v100 runtime md5 baseline (battle_engine current={be['current_md5']}, historical={len(be['historical_references'])})")
sys.exit(0)
