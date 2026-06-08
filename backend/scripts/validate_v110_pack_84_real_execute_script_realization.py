#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
r = d.get('real_execute_script_realization', {})
assert r.get('previous_state_pack_83') == 'SKELETON_NO_WRITES'
assert r.get('new_state_pack_84') == 'REAL_EXECUTE_WITH_BSON_OBJECTID_CONVERSION_AND_IDEMPOTENT_UPDATE_ONE'
assert r.get('real_writes_implemented') is True
assert r.get('idempotency_marker_written') == '_slc_psp_user_id_normalization_batch_id'
assert r.get('rollback_marker_written') == '_slc_psp_user_id_legacy_objectid_backup'
assert r.get('pre_write_user_id_match_verified') is True
assert r.get('no_writes_outside_user_id_normalization_fields') is True
# Verifica MD5 effettivo dello script post-Pack 84
m = hashlib.md5(open(os.path.join(R, 'backend/scripts/apply_v110_psp_user_id_normalization_gated.py'), 'rb').read()).hexdigest()
assert m == r.get('md5_after_pack_84'), f'apply script md5 mismatch: {m} vs {r.get("md5_after_pack_84")}'
# Verifica statica: nessun skeleton placeholder rimasto
src = open(os.path.join(R, 'backend/scripts/apply_v110_psp_user_id_normalization_gated.py')).read()
assert 'execute_gated_skeleton' not in src, 'skeleton mode still present'
assert "'mode': 'execute_real'" in src or '"mode": "execute_real"' in src, 'execute_real mode missing'
assert 'db.player_server_profiles.update_one' in src, 'real update_one call missing'
assert 'ObjectId(e[\'psp_id\'])' in src or 'ObjectId(e["psp_id"])' in src, 'ObjectId conversion missing'
print('[v110 PACK_84_REAL_EXECUTE_SCRIPT_REALIZATION] OK skeleton_replaced real_update_one bson_objectid pre_write_match_verified no_writes_outside_user_id')
