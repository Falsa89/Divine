#!/usr/bin/env python3
# Pack 81 - Track 13: MD5/critical baseline rebase summary.
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 2, 'rebase chain must include lobby and server.py'
file_to_md5 = {e['file']: e for e in chain}
# Verifica MD5 effettivo del lobby
m_lobby = hashlib.md5(open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx'), 'rb').read()).hexdigest()
assert m_lobby == file_to_md5['frontend/app/pre-battle-lobby.tsx']['to_md5'], f'lobby md5 mismatch: {m_lobby}'
# Verifica MD5 server.py
m_srv = hashlib.md5(open(os.path.join(R, 'backend/server.py'), 'rb').read()).hexdigest()
assert m_srv == file_to_md5['backend/server.py']['to_md5'], f'server.py md5 mismatch: {m_srv}'
# Tracking files contengono il NUOVO lobby MD5
for rel in ('data/design/closed_alpha/v100_runtime_md5_baseline_v1.json',
            'data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json',
            'data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json'):
    txt = open(os.path.join(R, rel)).read()
    assert m_lobby in txt, f'{rel} not rebased to new lobby MD5'
# Pack 79 validator assert sincronizzato
p79 = open(os.path.join(R, 'backend/scripts/validate_v110_pack_79_runtime_real.py')).read()
assert f"== '{m_lobby}'" in p79, 'Pack 79 validator MD5 not synced'
print(f'[v110 PACK_81_MD5_REBASE] OK lobby={m_lobby[:12]} server_py={m_srv[:12]} tracking_files_synced=3 pack79_validator_synced')
