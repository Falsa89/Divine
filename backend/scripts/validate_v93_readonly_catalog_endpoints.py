#!/usr/bin/env python3
"""v93 — Read-only catalog endpoints contract validator (blocked OK)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CT = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_readonly_catalog_endpoint_contract_v1.json')
DOC = os.path.join(ROOT, 'docs', 'divine', '93_READONLY_ENCOUNTER_LIVE_AVATAR_CATALOG_ENDPOINTS.md')

def fail(m): print(f"FAIL v93_readonly_catalog_endpoints: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(CT): fail(f"missing contract: {CT}")
    if not os.path.isfile(DOC): fail(f"missing doc: {DOC}")
    with open(CT) as f: data = json.load(f)
    eps = data.get('endpoints_designed') or []
    if len(eps) < 4: fail("must design at least 4 endpoints")
    for ep in eps:
        if not ep.get('read_only'): fail(f"endpoint {ep.get('path')} must be read_only")
        if ep.get('db_writes') != 0: fail(f"endpoint {ep.get('path')}.db_writes must be 0")
        if not ep.get('idempotent'): fail(f"endpoint {ep.get('path')} must be idempotent")
    if data.get('contract_status') != 'DESIGN_READY_IMPLEMENTATION_BLOCKED': fail("contract_status mismatch")
    saf = data.get('safety') or {}
    if saf.get('md5_lock_mutation') is not False: fail("safety.md5_lock_mutation must be false")
    print("PASS v93_readonly_catalog_endpoints")

if __name__ == '__main__': main()
