#!/usr/bin/env python3
"""PROJECT_P Track H validator — completion + next system."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_p_completion_and_next_system_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_P_COMPLETION_AND_NEXT_SYSTEM_READY': fail('verdict mismatch')
    if not m.get('project_p_completion_summary'): fail('summary missing')
    rec = m.get('recommended_next_pack', {})
    if not rec.get('pack_id'): fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art', {})
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    # If prod rollout NOT executed (default safe path), ensure required-to-unblock list is present.
    if m.get('prod_rollout_executed_in_pack_p') is False:
        if not m.get('required_to_unblock_pack_p'): fail('required_to_unblock_pack_p missing in READY_NOT_APPLIED state')
    print(f'[PASS] PROJECT_P Track H completion + roadmap READY; prod_executed={m.get("prod_rollout_executed_in_pack_p")}')
    sys.exit(0)


if __name__ == '__main__': main()
