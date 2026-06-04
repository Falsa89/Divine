#!/usr/bin/env python3
"""v95 — Validator: Reward/Score Canary Sandbox."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'reward_runtime', 'v95_reward_score_canary_sandbox_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
safety = d.get('safety') or {}
for k in ('db_writes',):
    if safety.get(k) != 0:
        print(f'FAIL — safety.{k} != 0'); sys.exit(1)
for k in ('reward_live', 'non_canary_reward', 'ranking_live', 'event_currency_live',
         'guild_score_mutation', 'arena_mmr_live', 'story_progress_commit',
         'tower_completion_commit', 'boss_fragment_grant', 'inventory_grant',
         'cosmetic_unlock', 'monetization', 'production_broadcast',
         'push_notification_live', 'random_opponents', 'character_bible_mutation',
         'hero_roster_mutation', 'final_asset_import', 'final_numbers_balance_lock'):
    if safety.get(k, True):
        print(f'FAIL — safety.{k} not false'); sys.exit(1)
if not d.get('dry_run_by_default'):
    print('FAIL — dry_run_by_default false'); sys.exit(1)
if d.get('sandbox_isolation', {}).get('touches_real_accounts'):
    print('FAIL — sandbox touches real accounts'); sys.exit(1)
if not d.get('rollback_drill', {}).get('verified'):
    print('FAIL — rollback drill not verified'); sys.exit(1)
allow = d.get('allowlist') or []
if not allow or any(not str(a).startswith('qa_alias_') for a in allow):
    print('FAIL — allowlist invalid'); sys.exit(1)
print('PASS — v95 reward/score canary sandbox')
sys.exit(0)
