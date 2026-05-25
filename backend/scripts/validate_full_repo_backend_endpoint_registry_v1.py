#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track C validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/backend_endpoint_mutation_registry_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_FULL_BACKEND_ENDPOINT_AND_MUTATION_REGISTRY_READY'
    assert d['endpoint_count'] >= 100, f"expected >=100 endpoints, got {d['endpoint_count']}"
    assert d['mutating_endpoint_count'] >= 50
    # server-profiles deve avere almeno 1 inert/503
    assert d['inert_503_count'] >= 1
    for e in d['endpoints']:
        for k in ('file', 'path', 'method', 'mutating', 'feature', 'risk'):
            assert k in e
    # almeno gacha/shop/artifact/heroes presenti come feature
    feats = set(d['by_feature'].keys())
    for must in ('gacha', 'artifact', 'shop', 'hero'):
        assert must in feats, f'missing feature {must}: {feats}'
    print(f"[PASS] FULL-REPO Track C backend \u2014 endpoints={d['endpoint_count']} mutating={d['mutating_endpoint_count']} inert503={d['inert_503_count']}")
    return 0
if __name__ == '__main__': sys.exit(main())
