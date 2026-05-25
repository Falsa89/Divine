#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track C validator (audit-only).
import json, sys
from pathlib import Path

P = Path('/app/data/design/audit/project_artifact_constellation_live_surface_audit_v1.json')


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] in (
        'TRACK_C_ARTIFACT_CONSTELLATION_LIVE_SURFACE_LOCKED_SAFE',
        'TRACK_C_ARTIFACT_CONSTELLATION_LIVE_SURFACE_AUDIT_READY_NOT_APPLIED',
    )
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['flag_flips'] == 0
    s = d['surfaces']
    assert s['artifacts_preview_safe']['locked_read_only'] is True
    assert s['artifacts_live']['locked_read_only'] is False
    assert s['artifacts_live']['risk'] == 'high'
    assert any('pull' in e for e in s['artifacts_live']['live_endpoints'])
    assert 'artifact' in s['gacha_banners']['banners_with_artifact_or_constellation']
    assert 'constellation' in s['gacha_banners']['banners_with_artifact_or_constellation']
    print('[PASS] PLAYER-LEGACY Track C artifact/constellation surfaces audit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
