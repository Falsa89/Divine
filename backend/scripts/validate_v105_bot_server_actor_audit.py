#!/usr/bin/env python3
"""v105 — Bot/server actor audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_bot_server_actor_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
appr = d.get('approved_design') or {}
for k in ('start_level','credible_progression','event_access_same_as_players','low_population_participation','archetypes','chat_contextual_not_spam','bot_rosters_valid_non_empty'):
    if k not in appr: print(f'FAIL \u2014 approved_design.{k} missing'); sys.exit(1)
if len(appr.get('archetypes') or []) < 5: print('FAIL \u2014 archetypes < 5'); sys.exit(1)
if appr.get('start_level') != 1: print('FAIL \u2014 start_level must be 1'); sys.exit(1)
matrix = d.get('compliance_matrix') or []
if len(matrix) < 8: print('FAIL \u2014 compliance_matrix < 8'); sys.exit(1)
if d.get('verdict') != 'DESIGN_OK_RUNTIME_PENDING': print('FAIL \u2014 verdict wrong'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('bot_runtime_modified','db_writes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print('PASS \u2014 v105 bot/server actor audit (DESIGN_OK_RUNTIME_PENDING)')
sys.exit(0)
