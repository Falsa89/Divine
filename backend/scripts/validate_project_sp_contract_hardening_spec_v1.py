#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_contract_hardening_spec_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_SERVER_PROFILE_CONTRACT_HARDENING_SPEC_READY'
    assert d['implementation_status'] == 'contract_draft_only_no_endpoint_added'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['global_markers']['TRACK_B_SERVER_PROFILE_CONTRACT_HARDENING_SPEC_APPROVAL'] == 'true'
    eps = d['endpoints']
    paths = [e['endpoint'] for e in eps]
    assert any('preview' in p for p in paths)
    assert any('select' in p for p in paths)
    assert any(p.endswith('/server-profiles') for p in paths)
    for e in eps:
        assert 'get_current_user' in e['auth']
        assert 'flag_gating' in e
    # Non-mutation guarantees for preview present
    pv = next(e for e in eps if 'preview' in e['endpoint'])
    inv = pv['non_mutation_invariants']
    assert any('users.server' in i for i in inv)
    # Required error envelopes
    for k in ['capacity_response_design','maintenance_response_design','not_found_response_design','auth_failure_response_design','rollback_error_response_design']:
        assert k in d, f'missing {k}'
    print(f"[PASS] AUTH-HARDEN Track B contract spec READY \u2014 endpoints={len(eps)}")
    return 0
if __name__ == '__main__': sys.exit(main())
