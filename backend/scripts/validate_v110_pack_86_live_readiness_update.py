#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_live_readiness_update_v1.json')))
assert d.get('new_server_psp_ensure_backend_ready') is True
assert d.get('new_server_psp_ensure_frontend_ready') is True
assert d.get('registration_global_starter_guard_active') is True
for k in ('starter_flow_ready','reward_live','progress_live','ledger_live','battle_engine_authoritative_live','legacy_cleanup_executed','release_readiness_claimed'):
    assert d.get(k) is False, f'{k} must be false'
print('[v110 PACK_86_LIVE_READINESS_UPDATE] OK backend_ready=true frontend_ready=true register_guard_active=true reward/progress/release_readiness=false')
