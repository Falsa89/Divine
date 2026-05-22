#!/usr/bin/env python3
"""SLC-E — Validate active_server_resolution_contract_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_e_active_server_resolution_contract_v1'


def main() -> int:
    errs = []
    j = load_json('active_server_resolution_contract_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('runtime_attached') is False, 'runtime_attached must be False', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    require(j.get('implementation_status') == 'NOT_IMPLEMENTED_IN_RUNTIME', 'implementation_status NOT_IMPLEMENTED_IN_RUNTIME', errs)
    fd = j.get('future_dependencies', {})
    require(fd.get('get_current_user', {}).get('server_aware') is False, 'get_current_user must not be server-aware', errs)
    require('account_id_plus_active_server_id' in fd.get('get_current_server_profile', {}).get('scope', ''), 'get_current_server_profile scope must reference account_id+active_server_id', errs)
    er = j.get('endpoint_requirements', {})
    require(er.get('server_bound_endpoints_require_resolved_profile') is True, 'server-bound endpoints must require resolved profile', errs)
    require(er.get('account_wide_endpoints_must_explicitly_opt_out_of_server_id') is True, 'account-wide endpoints must opt out of server_id', errs)
    sources = j.get('active_server_resolution_sources', [])
    require(len(sources) >= 4, f'expected >=4 resolution sources (got {len(sources)})', errs)
    src_names = ' '.join(s.get('source', '') for s in sources)
    for token in ('X-Server-ID', 'stored_active_server_id', 'server_id query parameter', 'default_legacy_server_id=s1'):
        require(token in src_names, f'resolution source missing: {token}', errs)
    uf = j.get('unsafe_fallback_removal', {})
    require(uf.get('requires_explicit_user_approval') is True, 'unsafe fallback removal must require explicit approval', errs)
    require('phase 11' in uf.get('phase', ''), 'unsafe fallback removal must reference phase 11', errs)
    fm = j.get('failure_modes', {})
    require('HTTP 423' in fm.get('no_active_server_resolved', ''), 'no_active_server must map to HTTP 423', errs)
    require('HTTP 403' in fm.get('server_id_header_does_not_match_owned_profile', ''), 'X-Server-ID mismatch must map to HTTP 403', errs)
    require('HTTP 410' in fm.get('resolved_server_is_archived', ''), 'archived server must map to HTTP 410', errs)
    require('HTTP 308' in fm.get('resolved_server_is_merged', ''), 'merged server must map to HTTP 308', errs)
    require(j.get('safety', {}).get('second_server_opening_allowed') is False, 'second_server_opening_allowed must be False', errs)
    require(j.get('safety', {}).get('future_feature_flag') == 'SERVER_PROFILES_RUNTIME_ENABLED', 'future_feature_flag must be SERVER_PROFILES_RUNTIME_ENABLED', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
