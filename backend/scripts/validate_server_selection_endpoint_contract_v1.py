#!/usr/bin/env python3
"""SLC-E — Validate server_selection_endpoint_contract_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_e_server_selection_endpoint_contract_v1'
REQUIRED_PATHS = {
    ('GET',  '/api/servers'),
    ('GET',  '/api/account/server-profiles'),
    ('POST', '/api/account/server-profiles/select'),
    ('GET',  '/api/account/active-server'),
}


def main() -> int:
    errs = []
    j = load_json('server_selection_endpoint_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('endpoint_contract_only') is True, 'endpoint_contract_only must be True', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    require(j.get('no_route_created') is True, 'no_route_created must be True', errs)
    require(j.get('no_auth_change') is True, 'no_auth_change must be True', errs)
    require(j.get('do_not_implement_routes_now') is True, 'do_not_implement_routes_now must be True', errs)
    require(j.get('implementation_status') == 'NOT_IMPLEMENTED_IN_RUNTIME', 'implementation_status NOT_IMPLEMENTED_IN_RUNTIME', errs)
    eps = {(e.get('method'), e.get('path')) for e in j.get('future_endpoints', [])}
    missing = REQUIRED_PATHS - eps
    require(not missing, f'missing endpoints: {sorted(missing)}', errs)
    # POST select must reject closed/archived/merged/merge_pending/planned
    sel = next((e for e in j['future_endpoints'] if e.get('path') == '/api/account/server-profiles/select'), None)
    if sel:
        joined = ' '.join(sel.get('rejection_rules', []))
        for k in ('archived', 'merged', 'merge_pending', 'planned', 'closed_to_new', 'second_server_locked'):
            require(k in joined, f'select endpoint missing rejection for {k}', errs)
        forb = ' '.join(sel.get('forbidden', []))
        require('never_clone_server_bound_progress' in forb, 'select must forbid cloning server-bound progress', errs)
    require(j.get('safety', {}).get('second_server_opening_allowed') is False, 'safety.second_server_opening_allowed must be False', errs)
    require(j.get('safety', {}).get('borea_safe') is True, 'safety.borea_safe must be True', errs)
    return finish(NAME, errs, {'endpoints_count': len(eps)})


if __name__ == '__main__':
    sys.exit(main())
