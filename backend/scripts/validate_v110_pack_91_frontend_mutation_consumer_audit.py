#!/usr/bin/env python3
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_frontend_mutation_consumer_audit_v1.json')))
muts = d.get('frontend_inventory_mutation_callers', [])
assert len(muts) >= 2, muts
for c in muts:
    assert c.get('post_pack_91_passes_server_id') is True, c
# Static verification: actually grep the files
for c in muts:
    fp = os.path.join(R, c['file'])
    assert os.path.exists(fp), f'missing {fp}'
    src = open(fp).read()
    assert 'server_id' in src, f'no server_id in {fp}'
    assert 'useServerScope' in src, f'no useServerScope hook in {fp}'
print('[v110 PACK_91_FRONTEND_MUTATION_CONSUMER_AUDIT] OK callers_audited=2 post_pack_91_passes_server_id=true')
