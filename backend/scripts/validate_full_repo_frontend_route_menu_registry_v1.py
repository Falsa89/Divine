#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track A validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/frontend_route_menu_registry_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_FULL_FRONTEND_ROUTE_AND_MENU_REGISTRY_READY'
    assert d['route_count'] >= 40, f"expected >=40 routes, got {d['route_count']}"
    assert d['menu_entry_count'] >= 20
    tags = d['counts_by_tag']
    # Devono esistere almeno alcune route LOCKED_PREVIEW (server_profiles, housing, artifacts-preview, status-codex)
    assert tags.get('LOCKED_PREVIEW', 0) >= 4, f'too few locked previews: {tags}'
    # Ogni route ha i campi minimi
    for r in d['routes']:
        for k in ('file', 'route', 'tag', 'flags'):
            assert k in r
    print(f"[PASS] FULL-REPO Track A registry \u2014 routes={d['route_count']} menu={d['menu_entry_count']} tags={tags}")
    return 0
if __name__ == '__main__': sys.exit(main())
