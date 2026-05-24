#!/usr/bin/env python3
"""PROJECT_M Track D validator — in-process flag ON canary fixture."""
import importlib.util, json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_m_flag_on_in_process_canary_fixture_v1.json')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_D_FLAG_ON_IN_PROCESS_CANARY_FIXTURE_READY': fail('verdict mismatch')
    if m.get('backend_env_toggled') is not False: fail('backend_env_toggled must be False')
    saved = os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED')
    spec = importlib.util.spec_from_file_location('_seam', SEAM); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    try:
        os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = 'true'
        # C1: buff_offensive atk_pct 0.10 -> atk_pct=0.10
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.10}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('atk_pct', 0.0) - 0.10) > 1e-9: fail(f'C1 atk_pct expected 0.10 got {env.get("atk_pct")}')
        # C2: buff_offensive crit_pct 0.05
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_offensive', 'stat': 'crit_pct', 'value': 0.05}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('crit_pct', 0.0) - 0.05) > 1e-9: fail(f'C2 crit_pct expected 0.05 got {env.get("crit_pct")}')
        # C3: buff_defensive def_pct 0.10
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_defensive', 'stat': 'def_pct', 'value': 0.10}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('def_pct', 0.0) - 0.10) > 1e-9: fail(f'C3 def_pct expected 0.10 got {env.get("def_pct")}')
        # C4: buff_defensive hp_pct 0.15
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_defensive', 'stat': 'hp_pct', 'value': 0.15}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('hp_pct', 0.0) - 0.15) > 1e-9: fail(f'C4 hp_pct expected 0.15 got {env.get("hp_pct")}')
        # C5: out-of-slice category (debuff) ignored -> zero envelope
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'debuff', 'stat': 'atk_pct', 'value': 0.50}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if any(env.get(k, -1.0) != 0.0 for k in ('atk_pct', 'def_pct', 'hp_pct', 'crit_pct')):
            fail(f'C5 out-of-slice must yield zero envelope, got {env}')
        # C6: cap clamp at master 0.30
        out = mod.apply_prefight_status_slice_preview({}, [{'category': 'buff_offensive', 'stat': 'atk_pct', 'value': 0.99}], dry_run=True)
        env = out.get('status_envelope_preview', {})
        if abs(env.get('atk_pct', 0.0) - 0.30) > 1e-9: fail(f'C6 cap clamp expected 0.30 got {env.get("atk_pct")}')
    finally:
        if saved is None: os.environ.pop('STATUS_RUNTIME_BUFF_SLICE_ENABLED', None)
        else: os.environ['STATUS_RUNTIME_BUFF_SLICE_ENABLED'] = saved
    # Confirm env was properly restored.
    if os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED', '').strip().lower() == 'true' and saved is None:
        fail('flag env leakage after test')
    print('[PASS] PROJECT_M Track D in-process canary: C1-C6 PASS; env restored; no backend toggle')
    sys.exit(0)


if __name__ == '__main__': main()
