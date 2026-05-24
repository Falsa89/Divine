#!/usr/bin/env python3
"""PROJECT_J Track H validator — completion + next pack roadmap."""
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/project_management/project_j_completion_and_next_pack_roadmap_v1.json')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_J_COMPLETION_AND_NEXT_PACK_ROADMAP_READY': fail('verdict mismatch')
    if not m.get('project_j_completion_summary'): fail('completion summary missing')
    packs = m.get('next_pack_roadmap', [])
    if len(packs) < 4: fail('at least 4 next packs required')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    print(f'[PASS] PROJECT_J Track H completion + roadmap READY: {len(packs)} next packs; ETA bands')
    sys.exit(0)
if __name__ == '__main__': main()
