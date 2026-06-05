#!/usr/bin/env python3
"""v106 — player_server_profiles schema validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'player_server_profiles_schema_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('collection') != 'player_server_profiles': print('FAIL \u2014 collection name wrong'); sys.exit(1)
if d.get('primary_key') != ['account_id','server_id']: print('FAIL \u2014 primary_key must be [account_id, server_id]'); sys.exit(1)
shape = d.get('document_shape') or {}
required_fields = {'profile_id','account_id','server_id','display_name','account_level','account_exp','created_at','last_played_at','starter_profile','roster','team_formation','currencies','story_progress','tower_progress','arena_profile','guild_profile','live_event_state','flags','migration_metadata'}
missing = required_fields - set(shape.keys())
if missing: print(f'FAIL \u2014 document_shape missing {missing}'); sys.exit(1)
flags = shape.get('flags') or {}
for k in ('server_scoped','migrated_from_account_wide','legacy_quarantine_present'):
    if k not in flags: print(f'FAIL \u2014 flags.{k} missing'); sys.exit(1)
idx = d.get('indexes') or []
if len(idx) < 5: print(f'FAIL \u2014 indexes < 5 (got {len(idx)})'); sys.exit(1)
unique_psp = [i for i in idx if i.get('unique') and i.get('fields') == ['account_id','server_id']]
if not unique_psp: print('FAIL \u2014 compound unique (account_id,server_id) index missing'); sys.exit(1)
forbidden = set(d.get('forbidden_fields') or [])
for f in ('password_hash','oauth_access_token','oauth_refresh_token','provider_client_secret'):
    if f not in forbidden: print(f'FAIL \u2014 forbidden_fields missing {f}'); sys.exit(1)
sep = d.get('separation_rules') or {}
for k in ('users_remains_account_global','player_server_profiles_holds_game_state','no_password_hash_duplicated','no_oauth_raw_token_duplicated','no_provider_secrets'):
    if not sep.get(k, False): print(f'FAIL \u2014 separation_rules.{k} must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('premium_currency_in_starter','random_starter_heroes','legacy_heroes_in_starter','reward_grant_on_create'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 player_server_profiles schema (PK=(account_id,server_id), {len(idx)} indexes)")
sys.exit(0)
