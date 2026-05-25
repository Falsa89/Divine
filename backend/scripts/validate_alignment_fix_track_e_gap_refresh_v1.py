#!/usr/bin/env python3
# ALIGNMENT_FIX Track E — missing/partial systems gap refresh.
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/missing_partial_systems_gap_refresh_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_MISSING_OR_PARTIAL_SYSTEMS_MASTER_GAP_REFRESH_READY'
    sys_list = d['systems']
    assert len(sys_list) >= 15
    ids = {s['id'] for s in sys_list}
    must = {'ANNOUNCEMENTS_NEWS', 'MAINTENANCE_NOTICE', 'PATCH_NOTES',
            'EVENT_NOTICES', 'GLOBAL_ALERT_BANNER', 'DYNAMIC_LIVE_FEED',
            'MAIL_INBOX_REWARDS', 'RED_DOT_NOTIFICATIONS', 'PUSH_LOCAL_NOTIFICATIONS',
            'IAP', 'SHOP', 'BATTLE_PASS', 'VIP', 'HERO_LEGACY_VISIBILITY',
            'ARTIFACT_BIBLE_CANONICAL', 'SERVER_SELECTION_PRE_HOME',
            'SOUL_FORGE_BACKEND_GUARD_ALIGNMENT'}
    missing = must - ids
    assert not missing, f'gap refresh missing systems: {missing}'
    # Live feed sub-features documentati
    live = next(s for s in sys_list if s['id'] == 'DYNAMIC_LIVE_FEED')
    sub = live.get('sub_features', [])
    assert len(sub) >= 6, f'live feed sub_features incomplete: {sub}'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] ALIGN-FIX Track E gap refresh \u2014 systems={len(sys_list)}")
    return 0
if __name__ == '__main__': sys.exit(main())
