#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track E validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/economy_gacha_roster_risk_audit_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_ECONOMY_MONETIZATION_GACHA_ROSTER_RISK_AUDIT_READY'
    assert d['iap_backend_present'] is False, 'IAP backend should not be present'
    assert len(d['risks']) >= 6
    ids = {r['id'] for r in d['risks']}
    for must in ('GACHA-PREMIUM-RATES', 'ARTIFACT-LIVE-EXPOSED',
                 'SHOP-LIVE-NO-IAP', 'BATTLEPASS-PREMIUM-NO-IAP',
                 'VIP-SPEND-NO-IAP', 'HEROES-LEGACY-VISIBILITY'):
        assert must in ids, f'missing risk: {must}'
    print(f"[PASS] FULL-REPO Track E economy risk \u2014 risks={len(d['risks'])} iap_present={d['iap_backend_present']}")
    return 0
if __name__ == '__main__': sys.exit(main())
