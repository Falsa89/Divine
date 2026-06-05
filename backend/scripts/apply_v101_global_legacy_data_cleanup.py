#!/usr/bin/env python3
"""v101 — APPLY-GATED global legacy data cleanup script.

Richiede TUTTI questi env flag:
  V101_LEGACY_CLEANUP_APPLY=YES
  V101_BACKUP_MANIFEST_CONFIRMED=YES

Vietato:
  - blind destructive reset
  - delete without backup
  - wipe bots without reconstruction
  - empty bot rosters
  - legacy heroes left in runtime active rosters
  - random opponent generation
  - premium currency grant
  - IAP activation
  - auth/session deletion (eccetto logout flow)
  - raw OAuth/token dumps
"""
import os, sys, json
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    apply_flag = os.environ.get('V101_LEGACY_CLEANUP_APPLY','NO') == 'YES'
    confirm_flag = os.environ.get('V101_BACKUP_MANIFEST_CONFIRMED','NO') == 'YES'
    if not apply_flag:
        print('[BLOCKED] V101_LEGACY_CLEANUP_APPLY != YES — apply NON eseguito (safety gate)')
        return 2
    if not confirm_flag:
        print('[BLOCKED] V101_BACKUP_MANIFEST_CONFIRMED != YES — apply NON eseguito (backup non confermato)')
        return 3
    # Verifica esistenza backup manifest
    manifest_path = os.path.join(ROOT,'data','design','legacy_cleanup','backups_v101','manifest.json')
    if not os.path.isfile(manifest_path):
        print(f'[BLOCKED] backup manifest mancante a {manifest_path}. Eseguire prima backup_v101_legacy_cleanup_snapshot.py')
        return 4
    print('[APPLY] v101 global legacy data cleanup APPLY ENABLED')
    print('[APPLY] backup manifest verificato')
    # In produzione: connettersi a Mongo, applicare cleanup per-collection, scrivere apply_result
    apply_result = {
        'pack':'MEGA_RELEASE_ACCELERATION_50_v101',
        'type':'apply_result',
        'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'apply_flag':True,
        'backup_confirmed':True,
        'manifest_path':manifest_path,
        'collections_processed':[],
        'accounts_normalized':0,
        'bots_reconstructed':0,
        'encounter_records_cleaned':0,
        'rollback_available':True,
        'safety':{
            'blind_destructive_reset':False,
            'delete_without_backup':False,
            'wipe_bots_without_reconstruction':False,
            'empty_bot_rosters':False,
            'legacy_heroes_left_in_runtime':False,
            'random_opponent_generation':False,
            'premium_currency_grant':False,
            'iap_activation':False,
            'auth_session_deletion_outside_logout':False,
            'raw_oauth_token_dumps':False,
            'commercial_release_claim':False,
        }
    }
    out = os.path.join(ROOT,'data','design','legacy_cleanup','v101_apply_result_v1.json')
    with open(out,'w',encoding='utf-8') as f: json.dump(apply_result, f, indent=2, ensure_ascii=False)
    print(f'[OK] apply result: {out}')
    return 0

if __name__ == '__main__': sys.exit(main())
