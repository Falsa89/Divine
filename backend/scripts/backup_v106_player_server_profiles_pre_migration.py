#!/usr/bin/env python3
"""v106 — Backup script (pre-migration).

Default: NO BACKUP EXECUTED. Solo se TUTTI questi flag env sono presenti:
  V106_PLAYER_SERVER_PROFILES_APPLY=YES
  V106_USER_EXPLICIT_DB_WRITE_APPROVAL=YES
  V106_STAGING_DB_CONFIRMED=YES

In assenza dei flag, lo script emette un manifest di skip e exit 0.
Non vengono mai serializzati password_hash, oauth token o provider secrets.
"""
import os, sys, json, hashlib, gzip
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_TARGET = ROOT / 'data' / 'design' / 'server_scope' / 'v106_backup_manifest_v1.json'

REQUIRED_FLAGS = {
    'V106_PLAYER_SERVER_PROFILES_APPLY': 'YES',
    'V106_USER_EXPLICIT_DB_WRITE_APPROVAL': 'YES',
    'V106_STAGING_DB_CONFIRMED': 'YES',
}

COLLECTIONS_TO_BACKUP = [
    'users','user_heroes','teams','inventory','currencies',
    'story_progress','tower_progress','arena_profile','guild_membership',
    'chat_messages','live_event_state','server_actors_bots',
    'gacha_history','reward_claims','battle_pass','vip','shop_purchases',
]

MASK_FIELDS = {
    'password_hash':'REDACTED_BCRYPT_HASH',
    'password':'REDACTED',
    'oauth_access_token':'REDACTED',
    'oauth_refresh_token':'REDACTED',
    'access_token':'REDACTED',
    'refresh_token':'REDACTED',
    'raw_iap_receipt_token':'REDACTED',
    'provider_client_secret':'REDACTED',
}

def flags_ok():
    return all(os.getenv(k) == v for k, v in REQUIRED_FLAGS.items())

def mask_doc(d):
    if not isinstance(d, dict): return d
    out = {}
    for k, v in d.items():
        if k in MASK_FIELDS: out[k] = MASK_FIELDS[k]
        elif isinstance(v, dict): out[k] = mask_doc(v)
        else: out[k] = v
    return out

def main():
    if not flags_ok():
        print('BACKUP SKIPPED \u2014 required env flags not all set:')
        for k, v in REQUIRED_FLAGS.items():
            print(f'  {k}={os.getenv(k, "<unset>")} (required {v})')
        print('Default outcome v106: DRY_RUN_READY_APPLY_GATED_NOT_EXECUTED. Backup not needed.')
        sys.exit(0)
    # Real backup path (would run only if flags set + staging confirmed)
    try:
        from pymongo import MongoClient
    except ImportError:
        print('FAIL \u2014 pymongo not installed; install and retry'); sys.exit(2)
    mongo_url = os.getenv('MONGO_URL')
    if not mongo_url: print('FAIL \u2014 MONGO_URL missing'); sys.exit(2)
    if 'prod' in (os.getenv('DB_TARGET','') or '').lower(): print('FAIL \u2014 production target forbidden'); sys.exit(2)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_dir = ROOT / 'data' / 'backups' / 'v106' / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    client = MongoClient(mongo_url)
    db = client.get_default_database()
    files = []
    for coll_name in COLLECTIONS_TO_BACKUP:
        coll = db[coll_name]
        path = backup_dir / f'{coll_name}.jsonl.gz'
        count = 0
        with gzip.open(path, 'wt', encoding='utf-8') as gz:
            for doc in coll.find({}):
                doc.pop('_id', None)
                gz.write(json.dumps(mask_doc(doc), default=str) + '\n')
                count += 1
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({'collection':coll_name,'path':str(path.relative_to(ROOT)),'sha256':sha,'record_count':count})
    manifest = {
        'backup_id': ts,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'pack':'v106',
        'db_target': os.getenv('DB_TARGET','staging'),
        'files': files,
        'safety_flags': {'masked_password_hash':True,'masked_oauth_tokens':True,'no_provider_secrets':True},
        'restore_instructions': 'see docs/divine/106_ROLLBACK_PLAYER_SERVER_PROFILES.md'
    }
    out = backup_dir / 'manifest.json'
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Backup OK: {len(files)} collections \u2192 {out}')
    sys.exit(0)

if __name__ == '__main__':
    main()
