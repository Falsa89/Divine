#!/usr/bin/env python3
"""PROJECT_I Track H validator — project 99→100 final live-gate roadmap."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/project_management/project_i_project_99_to_100_final_live_gate_roadmap_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_99_TO_100_FINAL_LIVE_GATE_ROADMAP_READY': fail('verdict mismatch')
    if m.get('current_global_progress_percent') < 95: fail('current_global_progress_percent must be >= 95')
    if m.get('target_global_progress_percent') != 100: fail('target_global_progress_percent must be 100')
    breakdown = m.get('remaining_one_percent_breakdown', {})
    total = sum(float(v) for v in breakdown.values())
    if abs(total - 1.0) > 0.05:
        fail(f'remaining_one_percent_breakdown should sum to ~1.0 (got {total:.3f})')
    packs = m.get('roadmap_packs', [])
    if len(packs) < 5: fail('roadmap_packs must list at least 5 future packs')
    for p in packs:
        for k in ('pack_id', 'name', 'deliverables'):
            if k not in p: fail(f'roadmap pack missing {k}')
    if not m.get('out_of_scope_for_technical_100'): fail('out_of_scope_for_technical_100 missing')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'time band {k} missing')
    print('[PASS] PROJECT_I Track H project 99→100 final live-gate roadmap READY: breakdown sum ~1.0; 5+ packs planned; ETA bands provided')
    sys.exit(0)

if __name__ == '__main__': main()
