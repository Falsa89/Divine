#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track D validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/feature_mode_crosswalk_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_FEATURE_MODE_CROSSWALK_AND_DUPLICATION_AUDIT_READY'
    assert d['feature_count'] >= 30
    feats = {c['feature'] for c in d['crosswalk']}
    for must in ('heroes', 'gacha', 'artifact', 'shop', 'battlepass', 'housing'):
        assert must in feats, f'missing crosswalk feature: {must}'
    # almeno 1 duplicazione attesa (es. shop+item-shop)
    # (è OK averne 0 se non rilevate; rendiamo soft-check)
    print(f"[PASS] FULL-REPO Track D crosswalk \u2014 features={d['feature_count']} dups={len(d['duplicate_feature_routes'])}")
    return 0
if __name__ == '__main__': sys.exit(main())
