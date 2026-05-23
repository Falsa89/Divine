#!/usr/bin/env python3
# SLC-G-GUILDS CLEANUP GATE CONTRACT VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_cleanup_gate_contract_v1_result.json'
SRC = DESIGN_DIR / 'slc_g_guilds_cleanup_gate_contract_v1.json'

REQUIRED_GATES = [
    'GUILD-G1','GUILD-G2','GUILD-G3','GUILD-G4','GUILD-G5','GUILD-G6',
    'GUILD-G7','GUILD-G8','GUILD-G9','GUILD-G10','GUILD-G11','GUILD-G12','GUILD-G13',
]

def main():
    errs = []
    if not SRC.exists():
        errs.append('contract_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        if d.get('db_write') is not False: errs.append('db_write_not_false')
        if d.get('cleanup_applied') is not False: errs.append('cleanup_applied_not_false')
        if d.get('explicit_write_approval_marker_required') != 'SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true':
            errs.append('approval_marker_string_incorrect')
        gates = {g.get('id') for g in (d.get('gates_all_must_pass') or [])}
        for g in REQUIRED_GATES:
            if g not in gates: errs.append(f'gate_missing:{g}')
        if 'on_any_gate_fail' not in d: errs.append('on_any_gate_fail_missing')
        if 'on_all_gates_pass_and_approval_marker_absent' not in d: errs.append('default_path_for_no_approval_missing')

    out = {'task_origin':'SLC-G-GUILDS-CLEANUP-GATE-CONTRACT','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-G-GUILDS-CLEANUP-GATE-CONTRACT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
