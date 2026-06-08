#!/usr/bin/env python3
# Pack 82 - Track 10: gate/runtime invariant preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert g.get(k) is True, f'{k} must be true'
# Pack 81 user_heroes promotion preserved: server-scoped path ancora presente
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in ('user_heroes_are_server_scoped', 'PLAYER_SERVER_PROFILE_REQUIRED', 'SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING', 'account_wide_legacy_DEPRECATED', 'server_scoped_psp_filtered', 'db.user_heroes.find({"user_id": uid, "server_id": sid})'):
    assert tok in src, f'Pack 81 invariant token missing: {tok}'
# Pack 80 lobby invariants ancora presenti
lobby = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
for tok in ('PLAYER_SLOT_COUNT', 'EmptySlotCard', '/api/team/get-formation', 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER', '/api/user/heroes?server_id='):
    assert tok in lobby, f'Pack 80 lobby invariant token missing: {tok}'
print('[v110 PACK_82_GATE_INVARIANT_PRESERVATION] OK pack80 + pack81 invariants preserved postqa_d_unchanged battle_engine_unchanged')
