#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK A
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/mode_feature_wiring_registry_core_modes_v1.json')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
DAILY_HUB = Path('/app/frontend/app/daily-hub.tsx')
REQUIRED_FIELDS = ['mode_id','display_name','category','frontend_entry_points','frontend_status','backend_endpoints_current','backend_endpoints_expected','backend_status','legacy_paths_detected','risk_level','risk_reason','smoke_required','next_action','owner_pack_recommendation']
EXPECTED_MODE_IDS = ['home','heroes','hero_detail','team_formation','combat','post_battle','gacha','shop','battle_pass','daily_hub','mail','achievements','events']

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_CORE_MODE_WIRING_REGISTRY_READY', f"bad verdict: {d['verdict']}"
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    assert d['global_markers']['PROJECT_MODE_WIRING_REGISTRY_AUDIT_APPROVAL'] == 'true'
    assert d['global_markers']['TRACK_A_CORE_MODE_WIRING_REGISTRY_APPROVAL'] == 'true'
    modes = d['modes']
    ids = [m['mode_id'] for m in modes]
    for exp in EXPECTED_MODE_IDS:
        assert exp in ids, f'missing core mode: {exp}'
    for m in modes:
        for f in REQUIRED_FIELDS:
            assert f in m, f"mode {m.get('mode_id')} missing field {f}"
        assert m['risk_level'] in ('LOW','MEDIUM','HIGH','CRITICAL')
        assert m['frontend_status'] in ('WIRED','DEEP_LINK_ONLY','MISSING','LEGACY_UI','DEV_ONLY','LOCKED_PREVIEW','HIDDEN_INTENTIONAL')
    # Sanity: combat references battle_engine invariant
    combat = next(m for m in modes if m['mode_id'] == 'combat')
    assert '151ca35ad3bc35f0a6209cb3744ed440' in combat['risk_reason'], 'combat must reference battle_engine MD5 invariant'
    # Sanity: daily-hub route still exists, menu still references it
    assert DAILY_HUB.exists()
    assert 'daily-hub' in MENU.read_text()
    print(f"[PASS] Track A core mode registry READY \u2014 modes={len(modes)}, hi_risk={sum(1 for m in modes if m['risk_level']=='HIGH')}")
    return 0
if __name__ == '__main__': sys.exit(main())
