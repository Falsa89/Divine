#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
ap = d.get('approval_proof', {})
assert ap.get('approval_string_provided') is True
assert ap.get('approval_string_value_exact') == 'AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_SU_DIVINE_WAIFUS'
for must in ('player_server_profiles.user_id', 'divine_waifus', 'ObjectId-string'):
    assert any(must in s for s in ap.get('scope_limited_to', [])), f'scope missing {must}'
for forbidden in ('PSP apply', 'legacy cleanup', 'reward live', 'progress live', 'user_heroes mutation', 'copia S1->S2', 'creazione nuovo PSP', 'delete', 'premium grant', 'release readiness claim'):
    assert any(forbidden in s for s in ap.get('approval_NOT_extended_to', [])), f'forbidden scope not declared: {forbidden}'
print('[v110 PACK_84_APPROVAL_PROOF] OK approval_string_exact scope_limited approval_NOT_extended_to_all_forbidden')
