#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_live_readiness_update_v1.json')))
assert d.get('team_formation_strict_server_scope_backend_ready') is True
assert d.get('team_formation_account_wide_fallback_removed_with_server_id') is True
assert d.get('pack_87_starter_team_preserved') is True
assert d.get('core_loader_promotion_prep_documented') is True
for k in ('inventory_psp_scoped_loader_ready','currencies_psp_scoped_loader_ready','story_psp_scoped_loader_ready','equipment_psp_scoped_loader_ready','reward_live','progress_live','ledger_live','battle_engine_authoritative_live','legacy_cleanup_executed','release_readiness_claimed'):
    assert d.get(k) is False
print('[v110 PACK_88_LIVE_READINESS_UPDATE] OK strict_team_ready=true loaders_ready=false reward/progress/release_readiness=false')
