#!/usr/bin/env python3
"""PROJECT_H Track H validator — project release candidate DoD finalization."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_h_release_candidate_dod_finalization_v1.json')
REQUIRED_LAYERS = {'slc_h', 'af2n', 'combat_status_skill', 'economy_battlepass_shop', 'gacha_summon', 'housing', 'artifacts', 'qa_release', 'suite_hygiene'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_RELEASE_CANDIDATE_DOD_FINALIZED': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    layers = m.get('dod_layers', {})
    if set(layers.keys()) != REQUIRED_LAYERS:
        fail(f'dod_layers keys mismatch: missing={sorted(REQUIRED_LAYERS - layers.keys())} extra={sorted(layers.keys() - REQUIRED_LAYERS)}')
    for name, layer in layers.items():
        if 'readiness_percent' not in layer: fail(f'dod_layers.{name} missing readiness_percent')
        if 'status' not in layer: fail(f'dod_layers.{name} missing status')
        if 'blockers' not in layer or not isinstance(layer['blockers'], list): fail(f'dod_layers.{name} blockers missing or not list')
    if m.get('aggregate_technical_readiness_excluding_graphics_audio_art_percent', 0) < 95:
        fail('aggregate_technical_readiness must be >= 95')
    plan = m.get('next_stage_plan', {})
    for phase in ('phase_RC_LIVE_FLAG_FLIPS', 'phase_RUNTIME_INTEGRATIONS', 'phase_MANUAL_QA', 'phase_GRAPHICS_AUDIO_ART_HANDOFF'):
        if not plan.get(phase): fail(f'next_stage_plan missing {phase}')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'time estimate missing {k}')
    print('[PASS] PROJECT_H Track H project release candidate DoD FINALIZED: 9 layers; 4 next-stage phases; honest ETA bands provided')
    sys.exit(0)

if __name__ == '__main__': main()
