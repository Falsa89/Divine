#!/usr/bin/env python3
# SLC-H ENDPOINT CONTRACT VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_h_endpoint_contract_v1_result.json'
SRC = DESIGN_DIR / 'slc_h_endpoint_contract_v1.json'
SCHEMAS = DESIGN_DIR / 'slc_h_request_response_schemas_v1.json'

REQUIRED_EP_IDS = {'SH-EP-001','SH-EP-002','SH-EP-003','SH-EP-004','SH-EP-005'}
REQUIRED_PATHS = {'/api/servers','/api/account/server-profiles','/api/account/server-profiles/select','/api/account/active-server','/api/account/server-profiles/create'}
REQUIRED_SCHEMAS = {'public_server_summary','GET_api_servers_response','account_server_profile','GET_api_account_server_profiles_response','POST_api_account_server_profiles_select_body','active_server_resolution','failure_response'}

def main():
    errs = []
    if not SRC.exists():
        errs.append('contract_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('route_patch_applied') is not False: errs.append('route_patch_applied_not_false')
        if d.get('second_server_opening_allowed') is not False: errs.append('second_server_opening_allowed_not_false')
        if d.get('runtime_implementation_status') != 'NOT_IMPLEMENTED': errs.append('runtime_implementation_status_not_NOT_IMPLEMENTED')
        eps = d.get('endpoints') or []
        seen_ids = {e.get('id') for e in eps}
        seen_paths = {e.get('path') for e in eps}
        for r in REQUIRED_EP_IDS:
            if r not in seen_ids: errs.append(f'endpoint_id_missing:{r}')
        for r in REQUIRED_PATHS:
            if r not in seen_paths: errs.append(f'endpoint_path_missing:{r}')
        inv = d.get('shared_contract_invariants') or {}
        for k, expected in [('slc_g_migration_must_be_applied',True),('unsafe_unknown_must_be_zero',True),
                            ('af2n_cap_must_stay',50000),('af2n_allowlist_must_stay',2500),
                            ('paid_currency_account_wide',True),('free_resources_server_bound',True),
                            ('no_automatic_resource_copy_between_servers',True),
                            ('no_borea_visibility_change',True),('no_primordial_gaia_change',True),
                            ('heroes_count_unchanged',100)]:
            if inv.get(k) != expected: errs.append(f'invariant_mismatch:{k}=expected={expected},got={inv.get(k)}')

    if not SCHEMAS.exists():
        errs.append('schemas_file_missing')
    else:
        s = json.loads(SCHEMAS.read_text()).get('schemas', {})
        for r in REQUIRED_SCHEMAS:
            if r not in s: errs.append(f'schema_missing:{r}')

    out = {'task_origin':'SLC-H-ENDPOINT-CONTRACT','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-H-ENDPOINT-CONTRACT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
