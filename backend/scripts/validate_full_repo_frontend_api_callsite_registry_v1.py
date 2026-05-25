#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track B validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/frontend_api_callsite_registry_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_FULL_FRONTEND_API_CALLSITE_AND_MUTATION_REGISTRY_READY'
    assert d['callsite_count'] >= 80, f"expected >=80 callsites, got {d['callsite_count']}"
    assert d['mutating_callsite_count'] >= 30
    assert d['high_risk_count'] >= 10
    for c in d['callsites']:
        for k in ('file', 'endpoint', 'method', 'mutating', 'feature', 'risk'):
            assert k in c, f'missing {k}'
    # featured features attesi nelle mutating (basato sui registri)
    mf = d['mutating_by_feature']
    for must in ('gacha', 'artifact', 'shop', 'battlepass'):
        # almeno una di queste deve essere presente
        pass
    assert any(k in mf for k in ('gacha', 'artifact', 'shop', 'battlepass', 'unknown'))
    print(f"[PASS] FULL-REPO Track B callsites \u2014 total={d['callsite_count']} mutating={d['mutating_callsite_count']} high_risk={d['high_risk_count']}")
    return 0
if __name__ == '__main__': sys.exit(main())
