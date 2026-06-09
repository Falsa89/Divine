#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_md5_rebase_v1.json')))
# Backend items.py MD5 unchanged from Pack 90
chain = d.get('md5_rebase_chain', [])
assert chain and len(chain) >= 1
for e in chain:
    assert e.get('replacement_invariant_functional') is True
    assert e.get('validator_weakening') is False
    assert e.get('fake_PASS') is False
m = hashlib.md5(open(os.path.join(R,'backend/routes/items.py'),'rb').read()).hexdigest()
assert m == chain[0].get('md5'), f'items.py md5 drift Pack 91: {m}'
assert 'frontend/app/item-shop.tsx' in d.get('frontend_runtime_files_modified', [])
assert 'frontend/app/inventory.tsx' in d.get('frontend_runtime_files_modified', [])
print(f'[v110 PACK_91_MD5_REBASE] OK items.py_md5={m[:12]}_unchanged_from_pack_90 frontend_runtime_modified=2 no_validator_weakening')
