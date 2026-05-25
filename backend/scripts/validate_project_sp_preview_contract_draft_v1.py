#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_preview_contract_draft_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_SERVER_PROFILES_PREVIEW_CONTRACT_DRAFT_READY'
    assert d['audit_mode'] == 'design_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['implementation_status'] == 'design_draft_only_no_endpoint_added'
    assert d['global_markers']['TRACK_C_SERVER_PROFILES_PREVIEW_CONTRACT_DRAFT_APPROVAL'] == 'true'
    c = d['contract_draft']
    assert c['endpoint'] == 'GET /api/account/server-profiles/preview'
    assert c['auth']['required'] is True
    fg = c['feature_flag_gating']
    assert 'SERVER_PROFILES_RUNTIME_ENABLED' in fg['primary']
    assert fg['both_off_response']['http'] == 503
    inv = c['explicit_non_mutation_invariants']
    for i in ['no write to users.server', 'no write to server_profiles']:
        assert i in inv, f'missing invariant: {i}'
    assert c['http_methods_supported'] == ['GET']
    assert set(c['http_methods_explicitly_rejected']) >= {'POST'}
    print('[PASS] DUAL-READ Track C preview contract draft READY')
    return 0
if __name__ == '__main__': sys.exit(main())
