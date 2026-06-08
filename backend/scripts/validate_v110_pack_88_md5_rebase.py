#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_md5_rebase_v1.json')))
mods = d.get('runtime_files_modified', [])
assert 'backend/routes/v96_team_formation.py' in mods
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 1
for e in chain:
    assert e.get('replacement_invariant_functional') is True
    assert e.get('validator_weakening') is False
    if 'fake_PASS' in e: assert e.get('fake_PASS') is False
# Verifica MD5 file effettivo
m = hashlib.md5(open(os.path.join(R, 'backend/routes/v96_team_formation.py'), 'rb').read()).hexdigest()
entry = chain[0]
assert m == entry.get('to_md5_post_pack_88'), f'v96 md5 mismatch: actual={m} expected={entry.get("to_md5_post_pack_88")}'
assert m != entry.get('from_md5_pre_pack_88')
print(f'[v110 PACK_88_MD5_REBASE] OK v96_team_formation.py={m[:12]} replacement_invariant_functional validator_weakening=false')
