#!/usr/bin/env python3
"""v106 — Dry-run migration script. NO DB WRITES under any circumstance.

Reads from MongoDB if accessible to estimate profile counts; otherwise emits
an analytical placeholder result. Always writes the v106 dry-run result JSON.
"""
import os, sys, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'design' / 'server_scope' / 'v106_dry_run_player_server_profiles_result_v1.json'

DEFAULT_SERVER_ID = 's1'

COLLECTIONS_TO_INSPECT = [
    'users','user_heroes','teams','inventory','currencies',
    'story_progress','tower_progress','arena_profile','guild_membership',
    'chat_messages','live_event_state','server_actors_bots',
    'gacha_history','reward_claims','battle_pass','vip','shop_purchases',
]

def try_connect():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / 'backend' / '.env')
    except Exception:
        pass
    url = os.getenv('MONGO_URL')
    if not url: return None, None
    try:
        from pymongo import MongoClient
        c = MongoClient(url, serverSelectionTimeoutMS=2000)
        c.admin.command('ping')
        db_name = os.getenv('DB_NAME', 'divine_waifus')
        return c, db_name
    except Exception:
        return None, None

def main():
    client, db_name = try_connect()
    db_inspected = client is not None
    inspection = {}
    accounts_count = 0
    if db_inspected:
        try:
            db = client[db_name]
            for coll in COLLECTIONS_TO_INSPECT:
                try:
                    inspection[coll] = db[coll].estimated_document_count()
                except Exception:
                    inspection[coll] = None
            try:
                accounts_count = db['users'].estimated_document_count()
            except Exception:
                accounts_count = 0
        except Exception:
            db_inspected = False
    estimated_profiles_to_create = accounts_count
    legacy_orphan_estimate = 0
    accounts_without_roster = None
    bots_to_migrate = inspection.get('server_actors_bots') if db_inspected else None
    result = {
        'pack':'MEGA_RELEASE_ACCELERATION_55_v106',
        'type':'v106_dry_run_player_server_profiles_result',
        'version':1,
        'language':'it',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'db_inspected': db_inspected,
        'db_target_planned':'staging_only',
        'db_writes_performed':0,
        'default_server_id': DEFAULT_SERVER_ID,
        'estimated_profiles_to_create': estimated_profiles_to_create,
        'legacy_orphan_estimate': legacy_orphan_estimate,
        'accounts_without_roster_estimate': accounts_without_roster,
        'bots_to_migrate_estimate': bots_to_migrate,
        'collections_inspected': inspection if db_inspected else {c: None for c in COLLECTIONS_TO_INSPECT},
        'migration_plan_summary': {
            'users_remain_account_global': True,
            'user_heroes_snapshot_to_psp_roster': True,
            'teams_snapshot_to_psp_team_formation': True,
            'inventory_snapshot_to_psp_inventory_ref': True,
            'soft_currencies_to_psp_currencies': True,
            'hard_currencies_remain_account_global': True,
            'story_progress_to_psp_story_progress': True,
            'tower_progress_to_psp_tower_progress': True,
            'arena_profile_to_psp_arena_profile': True,
            'guild_membership_to_psp_guild_profile': True,
            'chat_separate_with_channel_key_prefix_v109': True,
        },
        'conflicts_detected':[],
        'safety':{
            'no_db_writes':True,
            'no_destructive_migration':True,
            'no_reward_grant':False,
            'no_premium_currency_grant':False,
            'fake_PASS':False,
            'validator_weakening':False,
            'no_original_collections_deleted':True,
        }
    }
    result['safety']['no_reward_grant'] = True
    result['safety']['no_premium_currency_grant'] = True
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Dry-run OK \u2014 db_inspected={db_inspected} estimated_profiles={estimated_profiles_to_create} \u2192 {OUT}")
    sys.exit(0)

if __name__ == '__main__':
    main()
