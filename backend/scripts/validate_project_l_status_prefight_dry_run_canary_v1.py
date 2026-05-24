#!/usr/bin/env python3
"""PROJECT_L Track C validator — status pre-fight dry-run canary path."""
import importlib.util, json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_status_prefight_dry_run_canary_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_PREFIGHT_DRY_RUN_CANARY_READY': fail('verdict mismatch')
    if m.get('seam_available') is not True: fail('seam_available must be True')
    if not SEAM.exists(): fail('seam file missing')
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    try:
        # DR1: flag unset, dry_run=False -> identity
        os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        p = {'a': 1}
        if mod.apply_prefight_status_slice_preview(p) is not p: fail('DR1 identity failed')
        # DR2: flag=false, dry_run=False -> identity
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'false'
        if mod.apply_prefight_status_slice_preview(p) is not p: fail('DR2 identity failed')
        # DR3: flag=true, dry_run=False -> identity (live activation NOT authorized)
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        if mod.apply_prefight_status_slice_preview(p) is not p: fail('DR3 identity failed (live activation must be blocked)')
        # DR4: flag=true, dry_run=True, empty statuses -> zero envelope, original unchanged
        out = mod.apply_prefight_status_slice_preview(p, [], dry_run=True)
        if out is p: fail('DR4 must return copy')
        if 'a' not in p or 'status_envelope_preview' in p: fail('DR4 original must be unchanged')
        env = out.get('status_envelope_preview')
        if not isinstance(env, dict): fail('DR4 envelope missing')
        if any(env.get(k, -1.0) != 0.0 for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct')): fail('DR4 envelope must be all-zero')
        # DR5: flag=true, dry_run=True, with one buff_offensive atk_pct=0.10 (10%) -> atk_pct=0.10
        out = mod.apply_prefight_status_slice_preview(p, [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.10}], dry_run=True)
        env = out.get('status_envelope_preview')
        if abs(env.get('atk_pct', 0.0) - 0.10) > 1e-9: fail(f'DR5 atk_pct expected 0.10 got {env.get("atk_pct")}')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    print('[PASS] PROJECT_L Track C dry-run canary path READY: DR1-DR5 all PASS; live activation blocked')
    sys.exit(0)


if __name__ == '__main__': main()
