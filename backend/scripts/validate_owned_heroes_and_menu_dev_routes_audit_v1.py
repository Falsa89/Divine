#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track G validator (audit-only).
import json, sys
from pathlib import Path

P = Path('/app/data/design/audit/project_owned_heroes_and_menu_dev_routes_audit_v1.json')


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_OWNED_HEROES_LEGACY_VISIBILITY_AND_MENU_DEV_ROUTES_AUDIT_READY'
    assert d['audit_only'] is True
    assert d['menu_changed'] is False
    assert d['heroes_deleted'] == 0
    assert d['user_heroes_mutated'] == 0
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    classifications = {r['classification'] for r in d['menu_dev_routes']}
    assert 'dev' in classifications
    assert 'PROJECT_HERO_LIST_LEGACY_OWNED_VISIBILITY_FIX_PACK' in d['recommended_next_packs']
    assert 'PROJECT_MENU_DEV_ROUTE_HARDENING_PACK' in d['recommended_next_packs']
    print('[PASS] PLAYER-LEGACY Track G heroes + menu dev routes audit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
