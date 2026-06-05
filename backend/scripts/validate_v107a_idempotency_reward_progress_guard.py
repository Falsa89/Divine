#!/usr/bin/env python3
"""v107A — Idempotency / reward / progress guard validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_idempotency_reward_progress_guard_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
flags = d.get('feature_flags_default') or {}
for k in ('BATTLE_LAUNCH_AUTHORITATIVE_ENABLED','REWARD_LIVE_ENABLED','PROGRESS_LIVE_ENABLED','SERVER_SCOPED_RUNTIME_ENABLED'):
    if flags.get(k, True): print(f'FAIL \u2014 default flag {k} must be false'); sys.exit(1)
rules = d.get('guard_rules') or []
if len(rules) < 6: print(f'FAIL \u2014 guard_rules < 6 (got {len(rules)})'); sys.exit(1)
must_contain = ['idempotency_key required','HTTP 400 idempotency_key_required_for_live_gated_or_live','reward_policy=live not honored','coerced to preview']
body = ' || '.join(rules)
for token in must_contain:
    if token not in body: print(f'FAIL \u2014 guard_rules missing phrase: {token}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('reward_granted_v107a','progress_written_v107a','currency_mutated_v107a','battle_engine_formula_rewrite','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
if saf.get('db_writes_v107a', -1) != 0: print('FAIL \u2014 safety.db_writes_v107a must be 0'); sys.exit(1)
print(f"PASS \u2014 v107A idempotency/reward/progress guard ({len(rules)} rules, all flags off)")
sys.exit(0)
