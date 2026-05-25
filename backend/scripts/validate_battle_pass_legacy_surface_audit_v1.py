#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track F validator (audit-only).
import json, sys
from pathlib import Path

P = Path('/app/data/design/audit/project_battle_pass_legacy_surface_audit_v1.json')


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_BATTLE_PASS_LEGACY_SURFACE_AND_MONETIZATION_AUDIT_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['flag_flips'] == 0
    assert d['premium_purchase_path']['iap_backed'] is False
    assert d['premium_purchase_path']['risk'] == 'high'
    assert d['should_lock_until_new_contract'] is True
    assert d['recommended_next_pack'] == 'PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_PACK'
    print('[PASS] PLAYER-LEGACY Track F battle pass audit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
