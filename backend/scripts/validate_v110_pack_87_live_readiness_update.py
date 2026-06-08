#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_live_readiness_update_v1.json')))
for k in ('server_scoped_starter_flow_backend_ready','server_scoped_starter_flow_frontend_ready','starter_team_initialization_ready','server_ui_stale_copy_cleaned','new_server_psp_ensure_backend_ready','new_server_psp_ensure_frontend_ready','registration_global_starter_guard_active'):
    assert d.get(k) is True, f'{k} must be true'
for k in ('inventory_psp_scoped_loader_ready','currencies_psp_scoped_loader_ready','story_psp_scoped_loader_ready','equipment_psp_scoped_loader_ready','reward_live','progress_live','ledger_live','battle_engine_authoritative_live','legacy_cleanup_executed','release_readiness_claimed'):
    assert d.get(k) is False, f'{k} must be false'
print('[v110 PACK_87_LIVE_READINESS_UPDATE] OK starter_flow_ready=true ui_copy_cleaned=true other_loaders=false reward/progress/release_readiness=false')
