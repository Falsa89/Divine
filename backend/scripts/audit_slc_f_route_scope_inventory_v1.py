#!/usr/bin/env python3
"""SLC-F route scope inventory audit (read-only).

Scans /app/backend/routes/ for user_id touchpoints and validates the
static classification declared in slc_f_route_scope_inventory_v1.json.
"""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, finish, require, load, require_design_only  # noqa: E402

NAME = 'slc_f_route_scope_inventory_v1'
ROUTES = Path('/app/backend/routes')
ALLOWED_SCOPES = {'account_wide', 'server_bound', 'mixed_account_owned_server_equipped',
                  'global_catalog_readonly', 'unsafe_unknown'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'slc_f_route_scope_inventory_v1.json')
    require_design_only(j, errs, NAME)
    fam = j.get('route_family_classification', [])
    require(len(fam) >= 25, f'route_family_classification must have >=25 entries (got {len(fam)})', errs)
    seen_files = set()
    files_classified_existing = 0
    user_id_counts = {}
    for entry in fam:
        require(entry.get('scope') in ALLOWED_SCOPES, f'family {entry.get("family")}: invalid scope {entry.get("scope")}', errs)
        p = Path(entry.get('file', ''))
        if p.exists():
            files_classified_existing += 1
            seen_files.add(str(p))
            try:
                txt = p.read_text(errors='ignore')
            except Exception:
                txt = ''
            user_id_counts[str(p)] = len(re.findall(r'\buser_id\b', txt))
    # protected files referenced by inventory must exist
    prot = j.get('protected_route_files_no_diff_required', [])
    for f in prot:
        require(Path(f).exists() or f.endswith('battle_core.py'),
                f'protected file in inventory missing: {f}', errs)
    # NO unsafe_unknown should remain
    require(not j.get('unsafe_unknown_routes', []), 'unsafe_unknown_routes must be empty in SLC-F final inventory', errs)
    # Refresh inventory result with live stats
    extra = {
        'files_classified_count': len(fam),
        'files_existing_on_disk': files_classified_existing,
        'top_user_id_routes': sorted(user_id_counts.items(), key=lambda kv: -kv[1])[:10],
        'total_user_id_refs_in_classified_routes': sum(user_id_counts.values()),
    }
    return finish(NAME, errs, extra=extra)


if __name__ == '__main__':
    sys.exit(main())
