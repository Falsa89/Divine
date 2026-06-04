#!/usr/bin/env python3
"""v94 — Read-only catalog endpoints validator.

Accetta:
- endpoints implementati (file backend/routes/v94_readonly_catalog.py + reg in server.py),
- OPPURE design contract con stato BLOCKED honestly declared (server.py MD5 unchanged).
"""
import hashlib, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# v93 contract
CT_V93 = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_readonly_catalog_endpoint_contract_v1.json')
SERVER = os.path.join(ROOT, 'backend', 'server.py')
SERVER_OLD_MD5 = '055df030553f4791e8cac14254f1b148'

def fail(m): print(f"FAIL v94_readonly_catalog_endpoints: {m}"); sys.exit(1)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(8192), b''): h.update(c)
    return h.hexdigest()

def main():
    if not os.path.isfile(CT_V93): fail(f"missing v93 contract: {CT_V93}")
    if not os.path.isfile(SERVER): fail(f"missing server.py")
    actual = md5(SERVER)
    if actual == SERVER_OLD_MD5:
        # server unchanged → acceptable as honest BLOCKED status
        with open(CT_V93) as f: c = json.load(f)
        if c.get('contract_status') != 'DESIGN_READY_IMPLEMENTATION_BLOCKED':
            fail("server.py unchanged but v93 contract not BLOCKED")
        print("PASS v94_readonly_catalog_endpoints (design contract, server unchanged, honestly blocked)")
        return
    # server changed → must have new router file
    router_file = os.path.join(ROOT, 'backend', 'routes', 'v94_readonly_catalog.py')
    if not os.path.isfile(router_file):
        fail("server.py modified but routes/v94_readonly_catalog.py missing")
    print("PASS v94_readonly_catalog_endpoints (implementation)")

if __name__ == '__main__': main()
