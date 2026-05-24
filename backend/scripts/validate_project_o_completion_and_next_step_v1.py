#!/usr/bin/env python3
"""PROJECT_O Track H validator — completion + next pack."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_o_completion_and_next_step_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_O_COMPLETION_NEXT_STEP_READY': fail('verdict mismatch')
    if not m.get('project_o_completion_summary'): fail('summary missing')
    rec = m.get('recommended_next_pack', {})
    if not rec.get('pack_id') or not rec.get('deliverables'): fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    print('[PASS] PROJECT_O Track H completion + roadmap READY; next pack PROJECT_P planned')
    sys.exit(0)


if __name__ == '__main__': main()
