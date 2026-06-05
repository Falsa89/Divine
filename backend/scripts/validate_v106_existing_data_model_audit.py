#!/usr/bin/env python3
"""v106 — Existing data model audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_existing_data_model_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
colls = d.get('collections') or []
if len(colls) < 14: print(f'FAIL \u2014 collections audited < 14 (got {len(colls)})'); sys.exit(1)
required = {'name','current_keys','has_user_id','has_server_id','should_move_to_player_server_profiles','should_remain_account_global','migration_risk','required_index','required_backfill','blocker'}
for c in colls:
    missing = required - set(c.keys())
    if missing: print(f'FAIL \u2014 collection {c.get("name")} missing {missing}'); sys.exit(1)
required_names = {'users','user_heroes','teams','inventory','currencies','story_progress','tower_progress','arena_profile','guild_membership','chat_messages','live_event_state','server_actors_bots'}
present = {c.get('name') for c in colls}
missing = required_names - present
if missing: print(f'FAIL \u2014 required collections missing {missing}'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('db_writes','destructive_migration','reward_grant','premium_currency_grant','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 existing data model audit ({len(colls)} collections)")
sys.exit(0)
