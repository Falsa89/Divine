#!/usr/bin/env python3
"""v97 — Validator: Contextual bot chat policy + fixtures."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p1 = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_contextual_bot_chat_policy_v1.json')
p2 = os.path.join(ROOT, 'data', 'design', 'server_actors', 'v97_bot_chat_intent_response_fixtures_v1.json')
for p in (p1,p2):
    if not os.path.isfile(p): print(f'FAIL — file missing: {p}'); sys.exit(1)
with open(p1,'r',encoding='utf-8') as f: d1 = json.load(f)
with open(p2,'r',encoding='utf-8') as f: d2 = json.load(f)
cr = d1.get('core_rules') or {}
for k in ('answer_direct_questions','detect_mentioned_hero','small_talk_allowed_if_natural','out_of_context_response_forbidden'):
    if not cr.get(k): print(f'FAIL — core_rules.{k}'); sys.exit(1)
fr = d1.get('forbidden_response_topics') or []
if 'manual_ultimate_usage_suggestion' not in fr: print('FAIL — manual_ultimate_usage_suggestion missing'); sys.exit(1)
if 'real_PII_exposure' not in fr: print('FAIL — real_PII_exposure not forbidden'); sys.exit(1)
# fixtures must include borea
fixtures = d2.get('fixtures') or []
ids = [f.get('id') for f in fixtures]
if 'hero_question_borea' not in ids: print('FAIL — hero_question_borea fixture missing'); sys.exit(1)
borea = next(f for f in fixtures if f['id']=='hero_question_borea')
if borea.get('mentioned_hero') != 'Borea': print('FAIL — borea mentioned_hero'); sys.exit(1)
if not borea.get('valid_responses') or not borea.get('invalid_responses'): print('FAIL — borea responses missing'); sys.exit(1)
# Must reject "Sono le 8 di sera" out-of-context
invalid_str = ' '.join(borea.get('invalid_responses', []))
if 'Sono le 8 di sera' not in invalid_str: print('FAIL — borea invalid must reject out-of-context'); sys.exit(1)
# Must NOT mention manual ultimate in valid responses
for r in borea.get('valid_responses', []):
    if any(bad in r.lower() for bad in ['ultimate manuale','tieni l\'ultimate','attiva ultimate manualmente','premi ultimate']): print(f'FAIL — borea valid response mentions manual ultimate: {r}'); sys.exit(1)
global_rules = d2.get('global_validation_rules') or {}
if not global_rules.get('manual_ultimate_usage_topic_forbidden'): print('FAIL — manual_ultimate_usage_topic_forbidden'); sys.exit(1)
print(f'PASS — v97 contextual bot chat ({len(fixtures)} fixtures, Borea covered)')
sys.exit(0)
