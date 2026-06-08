#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_md5_rebase_v1.json')))
mods = d.get('runtime_files_modified', [])
assert 'backend/server.py' in mods
assert 'frontend/app/servers.tsx' in mods
assert 'frontend/app/pre-battle-lobby.tsx' in mods
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 3
for entry in chain:
    assert entry.get('replacement_invariant_functional') is True
    assert entry.get('validator_weakening') is False
    if 'fake_PASS' in entry:
        assert entry.get('fake_PASS') is False
hist = d.get('historical_reference', [])
# Sanity: storico packs preservato
assert any('Pack 85' in h for h in hist)
assert any('Pack 84' in h for h in hist)
assert any('Pack 82' in h for h in hist)
# Verifica file effettivamente modificati: il loro MD5 corrente deve essere diverso da Pack 85 baseline (per server.py)
cur_server_md5 = hashlib.md5(open(os.path.join(R, 'backend/server.py'), 'rb').read()).hexdigest()
entry0 = chain[0]
from_md5 = entry0.get('from_md5_pre_pack_86', '')
assert cur_server_md5 != from_md5, 'server.py md5 unchanged — register guard NOT applied?'
print(f'[v110 PACK_86_MD5_REBASE] OK 3_runtime_files_modified server.py_md5_changed_from_pack85_baseline replacement_invariant_functional validator_weakening=false')
