#!/usr/bin/env python3
# Pack 80 — Track J: MD5 rebase summary + baseline tracking files updated.
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 1, 'md5_rebase_chain empty'
lobby_entry = chain[0]
assert lobby_entry.get('file') == 'frontend/app/pre-battle-lobby.tsx'
assert lobby_entry.get('authorized') is True
assert lobby_entry.get('to_md5') == 'e817fac7a89e4e4ffb4186e91500377c'
assert lobby_entry.get('from_md5') == '5ab539bd6a2fdb617a09edfc95f3d06a'
# Verifica MD5 corrente reale del file
m = hashlib.md5(open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx'), 'rb').read()).hexdigest()
assert m == 'e817fac7a89e4e4ffb4186e91500377c', f'lobby current md5 mismatch: {m}'
# Verifica che TUTTI i tracking files siano stati aggiornati con il NUOVO MD5
track_files = [
    'data/design/closed_alpha/v100_runtime_md5_baseline_v1.json',
    'data/design/battle_launch/v108_pre_combat_story_md5_forensic_audit_v1.json',
    'data/design/battle_launch/v108_pre_combat_story_md5_supersede_review_v1.json',
]
for rel in track_files:
    txt = open(os.path.join(R, rel)).read()
    assert 'e817fac7a89e4e4ffb4186e91500377c' in txt, f'tracking file {rel} not rebased to new MD5'
    # historical_references preserva l'hash precedente
    assert '5ab539bd6a2fdb617a09edfc95f3d06a' in txt, f'tracking file {rel} must preserve old hash as historical reference'
# Pack 79 validator assert e' stato rebased al nuovo MD5
p79 = open(os.path.join(R, 'backend/scripts/validate_v110_pack_79_runtime_real.py')).read()
assert "== 'e817fac7a89e4e4ffb4186e91500377c'" in p79, 'Pack 79 validator assert not rebased'
print(f'[v110 LOBBY_TEAM_FETCH_MD5_REBASE] OK lobby_md5={m[:12]} authorized=true tracking_files_updated=3 historical_preserved=true')
