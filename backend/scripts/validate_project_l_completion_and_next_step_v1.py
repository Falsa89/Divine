#!/usr/bin/env python3
"""PROJECT_L Track H validator — completion + next pack roadmap."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_l_completion_and_next_step_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_L_COMPLETION_NEXT_STEP_READY': fail('verdict mismatch')
    if not m.get('project_l_completion_summary'): fail('summary missing')
    if m.get('seam_status') != 'CREATED_INERT_NOT_IMPORTED_BY_LIVE_RUNTIME': fail('seam_status mismatch')
    rec = m.get('recommended_next_pack', {})
    if not rec.get('pack_id') or not rec.get('deliverables'): fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    print('[PASS] PROJECT_L Track H completion + roadmap READY; next pack PROJECT_M planned')
    sys.exit(0)


if __name__ == '__main__': main()
