#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK F
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_frontend_lock_preview_recommendation_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_SERVER_PROFILES_FRONTEND_LOCK_OR_PREVIEW_RECOMMENDATION_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_F_SERVER_PROFILES_FRONTEND_LOCK_PREVIEW_RECOMMENDATION_APPROVAL'] == 'true'
    opts = d['options_considered']
    assert isinstance(opts, list) and len(opts) >= 4
    recommended_count = sum(1 for o in opts if o.get('recommended') is True)
    assert recommended_count == 1, f'must recommend exactly one option, found {recommended_count}'
    recommended = next(o for o in opts if o.get('recommended'))
    assert d['recommended_option'] == recommended['option_id']
    assert d['recommended_pack_name']
    rc = d['recommended_copy']
    assert rc['action_buttons'] == [], 'must NOT recommend any action buttons (locked preview)'
    print(f"[PASS] SP Track F lock/preview recommendation READY \u2014 option={d['recommended_option']}, next_pack={d['recommended_pack_name']}")
    return 0
if __name__ == '__main__': sys.exit(main())
