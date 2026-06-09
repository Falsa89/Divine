#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_md5_rebase_v1.json')))
mods=d.get('runtime_files_modified',[])
assert 'backend/routes/items.py' in mods
chain=d.get('md5_rebase_chain',[])
assert len(chain)>=1
for e in chain:
    assert e.get('replacement_invariant_functional') is True
    assert e.get('validator_weakening') is False
    if 'fake_PASS' in e: assert e.get('fake_PASS') is False
m=hashlib.md5(open(os.path.join(R,'backend/routes/items.py'),'rb').read()).hexdigest()
assert m==chain[0].get('to_md5_post_pack_89'), f'items.py md5 mismatch: {m}'
print(f'[v110 PACK_89_MD5_REBASE] OK items.py={m[:12]} replacement_invariant_functional validator_weakening=false')
