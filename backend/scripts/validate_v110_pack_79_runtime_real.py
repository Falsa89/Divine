#!/usr/bin/env python3
# Pack 79 — runtime real validator (verifica modifica file runtime, NOT solo design).
import hashlib, json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lobby_md5 = hashlib.md5(open(os.path.join(R,'frontend/app/pre-battle-lobby.tsx'),'rb').read()).hexdigest()
v96_md5 = hashlib.md5(open(os.path.join(R,'backend/routes/v96_team_formation.py'),'rb').read()).hexdigest()
# Pack 80 — MD5 rebase autorizzato per real lobby team fetch.
assert lobby_md5 == 'f8b770a118548602a7f680f59b6c409c', f'lobby md5 unexpected: {lobby_md5}'
# v96 md5 cambia se aggiungiamo righe; verifica che sia DIVERSO dal baseline pre-Pack 79.
assert v96_md5 != '640bd161cfbc5e9696511704d8613ecc', 'v96 NOT modified — Pack 79 falso!'
# Verifica che il lobby file contenga le patch chiave
lobby_src = open(os.path.join(R,'frontend/app/pre-battle-lobby.tsx')).read()
assert 'const PLAYER_SAFE_FALLBACK_TEAM: EnemyUnit[] = [];' in lobby_src
assert 'blocked_no_team_for_server' in lobby_src
assert 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' in lobby_src
# Verifica v96 contiene la promozione real loader
v96_src = open(os.path.join(R,'backend/routes/v96_team_formation.py')).read()
assert 'server_id: Optional[str] = None' in v96_src
assert 'filter_applied' in v96_src
assert 'player_server_profiles' in v96_src
assert 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' in v96_src
assert 'saved_formation_server_scoped' in v96_src
# Verifica summary JSON
S = os.path.join(R, 'data/design/v110_pack_79_runtime/v110_pack_79_runtime_summary_v1.json')
d = json.load(open(S))
assert d.get('runtime_files_modified_count', 0) >= 2
assert 'frontend/app/pre-battle-lobby.tsx' in d.get('runtime_files_modified', [])
assert 'backend/routes/v96_team_formation.py' in d.get('runtime_files_modified', [])
rebase = d.get('md5_rebase_chain', [])
assert len(rebase) >= 1
assert rebase[0].get('authorized') is True
loader = d.get('team_formation_loader_promotion', {})
assert loader.get('filter_applied_when_server_id_present') is True
assert loader.get('psp_aware_lookup') is True
assert loader.get('blocker_PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER_emitted_when_no_team_for_server') is True
assert loader.get('backend_restarted_and_smoke_ok') is True
assert loader.get('db_writes') == 0
lobby = d.get('lobby_runtime_fix', {})
for k in ('PLAYER_SAFE_FALLBACK_TEAM_emptied','no_3_slot_placeholder_player_facing','new_source_label_blocked_no_team_for_server','blocker_PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER_enforced','battle_launch_disabled_when_blocker'):
    assert lobby.get(k) is True, k
sf = d.get('safety_flags',{})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','production_db_writes','reward_live','progress_live','legacy_cleanup_executed','false_filter_applied_true','fake_team_as_real','fake_enemy_as_authored','3_slot_placeholder_player_facing','battle_engine_formula_rewrite','approval_flags_changed_to_yes_for_pack_79'):
    assert sf.get(k) is False, k
print(f'[v110 PACK_79_RUNTIME_REAL] OK runtime_files=2 lobby_md5={lobby_md5[:12]} v96_md5={v96_md5[:12]} md5_rebase_authorized=true loader_promoted=true blocker_enforced=true db_writes=0')
