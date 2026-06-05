#!/usr/bin/env python3
"""v101 — Backup snapshot script. Dry-run safe.

Apply solo se V101_LEGACY_CLEANUP_APPLY=YES e V101_BACKUP_MANIFEST_CONFIRMED=YES.
Non contiene secrets, no raw OAuth tokens, no provider secrets.
"""
import os, sys, json, hashlib
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, 'data', 'design', 'legacy_cleanup', 'v101_backup_manifest_v1.json')
OUT_DIR = os.path.join(ROOT, 'data', 'design', 'legacy_cleanup', 'backups_v101')
COLLECTIONS = ['users','inventories','server_actors','formations','story_state','pvp_state','tower_state','event_state','gacha_history','summon_history','config']

def main():
    apply_flag = os.environ.get('V101_LEGACY_CLEANUP_APPLY','NO') == 'YES'
    confirm_flag = os.environ.get('V101_BACKUP_MANIFEST_CONFIRMED','NO') == 'YES'
    if not (apply_flag and confirm_flag):
        print('[DRY-RUN] backup_v101_legacy_cleanup_snapshot.py: gating flags not set, running in dry-run mode')
        print(f'[DRY-RUN] target collections: {COLLECTIONS}')
        print(f'[DRY-RUN] output dir: {OUT_DIR}')
        print('[DRY-RUN] SAFETY: no raw_oauth_tokens, no provider_secrets, no auth.password fields')
        return 0
    # Real apply path: would connect to MongoDB and dump collections.
    # Container Emergent: MongoDB available via MONGO_URL env.
    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            print('[FAIL] MONGO_URL not set'); return 1
        client = MongoClient(mongo_url)
        db = client.get_default_database()
        os.makedirs(OUT_DIR, exist_ok=True)
        manifest = {'pack':'v101','generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'collections':{}}
        for c in COLLECTIONS:
            try:
                docs = list(db[c].find({}, {'password':0, 'refresh_token':0, 'oauth_raw':0, 'provider_secret':0}))
                # Convert ObjectId/dates to strings safely
                def _sanitize(o):
                    if isinstance(o, dict): return {k:_sanitize(v) for k,v in o.items()}
                    if isinstance(o, list): return [_sanitize(x) for x in o]
                    if hasattr(o,'isoformat'): return o.isoformat()
                    return str(o) if not isinstance(o,(str,int,float,bool,type(None))) else o
                docs = _sanitize(docs)
                blob = json.dumps(docs, ensure_ascii=False, indent=2)
                out_path = os.path.join(OUT_DIR, f'{c}.json')
                with open(out_path,'w',encoding='utf-8') as f: f.write(blob)
                manifest['collections'][c] = {'count': len(docs), 'md5': hashlib.md5(blob.encode()).hexdigest(), 'path': out_path}
                print(f'[OK] dumped {c}: {len(docs)} docs -> {out_path}')
            except Exception as e:
                manifest['collections'][c] = {'error': str(e)}
                print(f'[WARN] {c}: {e}')
        with open(os.path.join(OUT_DIR,'manifest.json'),'w',encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f'[OK] manifest written: {OUT_DIR}/manifest.json')
        return 0
    except ImportError:
        print('[FAIL] pymongo not installed'); return 1

if __name__ == '__main__': sys.exit(main())
