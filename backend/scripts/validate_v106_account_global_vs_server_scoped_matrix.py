#!/usr/bin/env python3
"""v106 — Account-global vs server-scoped matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_account_global_vs_server_scoped_matrix_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
ag = d.get('account_global') or []
ss = d.get('server_scoped') or []
mx = d.get('mixed_needs_decision') or []
if len(ag) < 6: print(f'FAIL \u2014 account_global < 6 (got {len(ag)})'); sys.exit(1)
if len(ss) < 10: print(f'FAIL \u2014 server_scoped < 10 (got {len(ss)})'); sys.exit(1)
if len(mx) < 4: print(f'FAIL \u2014 mixed_needs_decision < 4 (got {len(mx)})'); sys.exit(1)
required_global = {'auth_identity','vip_status'}
required_scoped = {'roster_user_heroes','team_formation','story_progress','arena_mmr_rank','guild_membership','chat_messages'}
ag_names = {x.get('system') for x in ag}
ss_names = {x.get('system') for x in ss}
missing_g = required_global - ag_names
missing_s = required_scoped - ss_names
if missing_g: print(f'FAIL \u2014 account_global missing required {missing_g}'); sys.exit(1)
if missing_s: print(f'FAIL \u2014 server_scoped missing required {missing_s}'); sys.exit(1)
for m in mx:
    if not m.get('recommended'): print(f'FAIL \u2014 mixed system {m.get("system")} missing recommended'); sys.exit(1)
    if not m.get('options'): print(f'FAIL \u2014 mixed system {m.get("system")} missing options'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','reward_grant','premium_currency_grant','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 account-global vs server-scoped matrix ({len(ag)} global, {len(ss)} scoped, {len(mx)} mixed)")
sys.exit(0)
