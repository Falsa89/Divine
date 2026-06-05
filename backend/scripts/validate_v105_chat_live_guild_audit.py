#!/usr/bin/env python3
"""v105 — Chat/live/guild audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_chat_live_guild_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
for section in ('chat','live','guild'):
    s = d.get(section) or {}
    if not s.get('surface_present'): print(f'FAIL \u2014 section {section} surface_present must be true'); sys.exit(1)
    if s.get('server_scoped', True): print(f'FAIL \u2014 section {section}.server_scoped must be false (honest)'); sys.exit(1)
summ = d.get('summary') or {}
for k in ('chat_server_scoped','live_server_scoped','guild_server_scoped'):
    if summ.get(k, True): print(f'FAIL \u2014 summary.{k} must be false (honest)'); sys.exit(1)
if summ.get('data_leak_risk_overall') != 'critical': print('FAIL \u2014 data_leak_risk_overall must be critical'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('chat_mutated','db_writes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print('PASS \u2014 v105 chat/live/guild audit (3 sections, all server_scoped=false honest)')
sys.exit(0)
