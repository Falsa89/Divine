#!/usr/bin/env python3
"""PROJECT_K Track H validator — completion + next pack status."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_k_completion_and_live_gate_status_v1.json')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_K_COMPLETION_AND_LIVE_GATE_STATUS_READY': fail('verdict mismatch')
    if not m.get('project_k_completion_summary'): fail('summary missing')
    if not m.get('honest_blocker_for_wiring'): fail('honest_blocker_for_wiring missing')
    rec = m.get('recommended_next_pack', {})
    if not rec.get('pack_id') or not rec.get('deliverables'): fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    print('[PASS] PROJECT_K Track H completion + roadmap READY; honest blocker recorded')
    sys.exit(0)
if __name__ == '__main__': main()
