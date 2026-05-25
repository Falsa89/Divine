#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track D validator (audit-only).
import json, sys
from pathlib import Path

P = Path('/app/data/design/audit/project_gacha_rate_sanity_audit_v1.json')


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_GACHA_RATE_SANITY_AND_BANNER_GUARD_AUDIT_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['flag_flips'] == 0
    # rate frontend/backend devono combaciare su standard/premium
    fe = d['banner_rates_frontend']
    be = d['banner_rates_backend']
    for banner in be:
        for star in be[banner]:
            assert abs(fe[banner][star] - be[banner][star]) < 1e-9, f'rate drift on {banner} {star}'
    # premium 5*+6* somma >= 30% — conferma rates molto generose
    assert (fe['premium']['5*'] + fe['premium']['6*']) >= 0.30
    assert d['looks_dev_or_test'] is True
    assert d['public_lock_recommended_until_signoff'] is True
    assert d['recommended_next_pack'] == 'PROJECT_GACHA_RATE_SANITY_FIX_OR_LOCK_PACK'
    print('[PASS] PLAYER-LEGACY Track D gacha rate sanity audit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
