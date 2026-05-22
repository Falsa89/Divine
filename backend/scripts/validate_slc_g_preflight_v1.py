#!/usr/bin/env python3
# SLC-G PREFLIGHT VALIDATOR (READ-ONLY / DESIGN-ONLY)
# Verifica che TUTTI gli artefatti SLC prerequisiti e le invarianti baseline siano intatte
# prima di considerare anche solo la simulazione dry-run del backfill default_s1.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_preflight_v1_result.json'

REQUIRED_PRIOR = [
    'account_entity_schema_v1.json',
    'account_wide_document_contract_v1.json',
    'server_bound_document_contract_v1.json',
    'collection_scope_migration_matrix_v1.json',
    'multishard_index_plan_v1.json',
    'single_to_multishard_migration_phase_plan_v1.json',
    'slc_c_multishard_rollback_plan_v1.json',
    'server_profile_creation_contract_v1.json',
    'slc_f_collection_scope_matrix_v1.json',
    'slc_f_endpoint_patch_contract_v1.json',
    'server_merge_tooling_offline_plan_v1.json',
    'server_merge_abort_rollback_policy_v1.json',
    'slc_g_default_s1_migration_preflight_v1.json',
    'slc_g_default_s1_backfill_plan_v1.json',
    'slc_g_write_gate_contract_v1.json',
    'slc_g_backup_manifest_contract_v1.json',
    'slc_g_rollback_plan_v1.json',
    'slc_g_idempotency_contract_v1.json',
    'slc_g_readiness_rollup_v1.json',
]

BENCH_INDEX_CANDIDATES = [
    ROOT / 'data/design/benchmark_canonical/benchmark_canonical_index_v1.json',
    ROOT / 'data/design/benchmark/benchmark_canonical_index_v1.json',
]

def main():
    errs = []
    for f in REQUIRED_PRIOR:
        p = DESIGN_DIR / f
        if not p.exists():
            errs.append(f'missing_prior_artifact:{f}')
    if not any(p.exists() for p in BENCH_INDEX_CANDIDATES):
        # try recursive fallback
        alt = list(ROOT.glob('data/design/**/benchmark_canonical_index_v1.json'))
        if not alt:
            errs.append('missing_benchmark_canonical_index')
    # invariants checks (env flags must be unset)
    if os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED'):
        errs.append('flag_must_be_unset:SERVER_PROFILES_RUNTIME_ENABLED')
    if os.environ.get('SECOND_SERVER_OPENING_ENABLED'):
        errs.append('flag_must_be_unset:SECOND_SERVER_OPENING_ENABLED')
    # design_only on SLC-G plan
    plan = json.loads((DESIGN_DIR / 'slc_g_default_s1_backfill_plan_v1.json').read_text()) if (DESIGN_DIR/'slc_g_default_s1_backfill_plan_v1.json').exists() else {}
    if plan.get('migration_applied') is not False or plan.get('db_write') is not False or plan.get('design_only') is not True:
        errs.append('plan_flags_must_be_design_only_no_write')

    out = {
        'task_origin':'SLC-G-PREFLIGHT',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-PREFLIGHT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
