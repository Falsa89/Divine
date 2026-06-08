#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_md5_rebase_v1.json')))
mods = d.get('runtime_files_modified', [])
assert 'backend/server.py' in mods
assert 'frontend/app/servers.tsx' in mods
# pre-battle-lobby NOT modified in this pack
not_mod = d.get('runtime_files_not_modified_in_this_pack', [])
assert 'frontend/app/pre-battle-lobby.tsx' in not_mod
# Verifica chain: ogni entry deve avere replacement_invariant_functional=true e validator_weakening=false e fake_PASS=false
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 2, f'chain must have >=2 entries, got {len(chain)}'
for entry in chain:
    assert entry.get('replacement_invariant_functional') is True, f'entry {entry.get("file")} replacement_invariant_functional must be true'
    assert entry.get('validator_weakening') is False, f'entry {entry.get("file")} validator_weakening must be false'
    if 'fake_PASS' in entry:
        assert entry.get('fake_PASS') is False
hist = d.get('historical_reference', [])
for p in ('Pack 80','Pack 81','Pack 82','Pack 84','Pack 85','Pack 86'):
    assert any(p in h for h in hist), f'historical reference for {p} missing'
# Verifica MD5 server.py e servers.tsx siano cambiati rispetto a Pack 86 baseline
cur_srv = hashlib.md5(open(os.path.join(R, 'backend/server.py'), 'rb').read()).hexdigest()
cur_servers = hashlib.md5(open(os.path.join(R, 'frontend/app/servers.tsx'), 'rb').read()).hexdigest()
assert cur_srv != '272c70b37190e1fa8b6e712e83fdda83', 'server.py md5 unchanged — starter claim endpoint NOT applied?'
assert cur_servers != '91dc7f8c8f49934453b35a09cc9eaeab', 'servers.tsx md5 unchanged — onEnter starter claim call NOT applied?'
# Pre-battle-lobby unchanged
cur_lobby = hashlib.md5(open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx'), 'rb').read()).hexdigest()
assert cur_lobby == '4c720c53a29ca2a7fee4ca821221b479', f'pre-battle-lobby.tsx MD5 unexpectedly changed in Pack 87: {cur_lobby}'
print(f'[v110 PACK_87_MD5_REBASE] OK 2_runtime_files_modified server.py={cur_srv[:12]} servers.tsx={cur_servers[:12]} pre_battle_lobby_unchanged={cur_lobby[:12]} replacement_invariant_functional validator_weakening=false')
