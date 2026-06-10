#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_gate_invariant_preservation_v1.json')))
for k in ('pack_84_psp_normalization_preserved','pack_85_psp_onboarding_preserved','pack_86_lobby_psp_ensure_preserved','pack_87_server_scoped_starter_preserved','pack_88_team_formation_strict_preserved','pack_89_inventory_psp_scoped_preserved','pack_90_inventory_write_strict_preserved','pack_91_inventory_frontend_preserved','pack_92_core_server_scope_preserved','pack_93_economy_progress_preserved','pack_94_equipment_strict_preserved','pack_94_legacy_earn_pvp_guild_quarantine_preserved','pack_95_story_strict_preserved','pack_95_reward_claim_ledger_foundation_preserved','pack_95_legacy_quarantine_preserved','pack_96_reward_claim_endpoint_live_gated_preserved','pack_96_qa_and_story_marker_sources_preserved','pack_96_premium_block_preserved','postqa_d_gates_locked_unless_explicit','battle_engine_unchanged','battle_simulate_not_called_from_staging_or_live','story_tsx_unchanged','combat_tsx_unchanged'):
    assert d[k] is True, k
print('[v110 PACK_97_GATE_INVARIANT_PRESERVATION] OK packs_84_96_preserved battle_engine_unchanged postqa_d_locked')
