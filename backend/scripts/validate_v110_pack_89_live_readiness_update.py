#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_live_readiness_update_v1.json')))
for k in ('inventory_psp_scoped_loader_runtime_ready','inventory_legacy_path_marked_non_player_facing','team_formation_strict_server_scope_preserved','pack_87_starter_team_preserved'):
    assert d.get(k) is True
for k in ('currencies_psp_scoped_loader_ready','story_psp_scoped_loader_ready','equipment_psp_scoped_loader_ready','inventory_write_paths_promoted','reward_live','progress_live','ledger_live','battle_engine_authoritative_live','legacy_cleanup_executed','release_readiness_claimed'):
    assert d.get(k) is False
print('[v110 PACK_89_LIVE_READINESS_UPDATE] OK inventory_read_ready=true write_paths_not_promoted=true reward/progress=false')
