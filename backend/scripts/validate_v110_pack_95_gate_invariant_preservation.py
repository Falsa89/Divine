#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_gate_invariant_preservation_v1.json')))
for k in ('pack_84_psp_normalization_preserved','pack_85_psp_onboarding_preserved','pack_86_lobby_psp_ensure_preserved','pack_87_server_scoped_starter_preserved','pack_88_team_formation_strict_preserved','pack_89_inventory_psp_scoped_preserved','pack_90_inventory_write_strict_preserved','pack_91_inventory_frontend_preserved','pack_92_core_server_scope_preserved','pack_93_economy_progress_preserved','pack_94_equipment_strict_preserved','pack_94_legacy_earn_pvp_guild_quarantine_preserved','postqa_d_gates_locked_unless_explicit','battle_engine_unchanged','battle_simulate_not_called_from_staging_or_live','story_tsx_unchanged','combat_tsx_unchanged'):
    assert d.get(k) is True, k
print('[v110 PACK_95_GATE_INVARIANT_PRESERVATION] OK packs_84_94_preserved battle_engine_unchanged postqa_d_locked')
