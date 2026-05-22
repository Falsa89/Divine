#!/usr/bin/env python3
# SLC-G WRITE GATE CONTRACT VALIDATOR (READ-ONLY)
# Verifica che il contratto write-gate sia ben formato, gated, design-only e
# che richieda esplicitamente l'approvazione utente per qualsiasi scrittura.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_write_gate_contract_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_write_gate_contract_v1.json'

REQUIRED_GATES = [
    'G1_PRIOR_SLC_PASS','G2_API_SMOKE_INVARIANTS','G3_AF2N_INVARIANTS',
    'G4_RUNTIME_FLAGS_UNSET','G5_PROTECTED_FILE_NO_DIFF','G6_DRY_RUN_REPORT_PRESENT',
    'G7_BACKUP_MANIFEST_PRESENT','G8_ROLLBACK_PLAN_PRESENT','G9_IDEMPOTENCY_CONTRACT_PRESENT',
    'G10_ZERO_UNSAFE_UNKNOWN','G11_EXPLICIT_USER_APPROVAL_PRESENT','G12_BASELINE_DIFF_PASS_OR_AUTHORIZED',
]

def main():
    errs = []
    if not SRC.exists():
        errs.append('contract_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('migration_applied') is not False: errs.append('migration_applied_not_false')
        if d.get('explicit_user_write_approval_required') is not True: errs.append('explicit_user_write_approval_required_not_true')
        gates = {g.get('id') for g in (d.get('gates_all_must_pass') or [])}
        for g in REQUIRED_GATES:
            if g not in gates: errs.append(f'gate_missing:{g}')
        if 'approval_marker_required_in_prompt' not in d:
            errs.append('approval_marker_required_in_prompt_missing')
        if d.get('write_apply_script_creation_is_separate_gated_step') is not True:
            errs.append('write_apply_script_must_be_separate_gated_step')
        if 'signoffs_required' not in d or not d['signoffs_required']:
            errs.append('signoffs_required_missing')

    out = {
        'task_origin':'SLC-G-WRITE-GATE-CONTRACT',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'errors':errs,'verdict':'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-WRITE-GATE-CONTRACT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
