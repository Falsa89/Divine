#!/usr/bin/env python3
"""v101 — Canonical runtime allowlist validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_canonical_runtime_allowlist_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if 'canonical_hero_ids' not in d: print('FAIL \u2014 canonical_hero_ids missing'); sys.exit(1)
if 'hidden_pending_hero_ids_not_usable' not in d: print('FAIL \u2014 hidden_pending missing'); sys.exit(1)
if 'canonical_bot_archetypes' not in d or len(d['canonical_bot_archetypes']) < 5:
    print('FAIL \u2014 canonical_bot_archetypes < 5'); sys.exit(1)
if len(d.get('rules', [])) < 3: print('FAIL \u2014 rules < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('hidden_heroes_in_active_runtime_rosters','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 canonical runtime allowlist ({len(d['canonical_bot_archetypes'])} archetypes)")
sys.exit(0)
