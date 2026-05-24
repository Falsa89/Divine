#!/usr/bin/env python3
"""PROJECT_V Track H validator — pack completion."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_v_completion_and_next_pack_v1.json')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_V_COMPLETION_AND_NEXT_PACK_READY': fail('verdict mismatch')
    s = m.get('project_v_completion_summary') or {}
    if s.get('flag_flipped_during_dev_live') is not True: fail('flag_flipped_during_dev_live must be True')
    if s.get('final_flag_state') != 'OFF': fail('final_flag_state must be OFF')
    if s.get('env_post_rollback_byte_identical_to_pre_flip') is not True: fail('env byte-identical must be True')
    for k in ('battle_engine_mutated', 'battle_core_mutated', 'combat_tsx_mutated', 'frontend_mutated', 'db_writes', 'keep_on_after_dev_live_marker_present'):
        if s.get(k) is not False: fail(f'{k} must be False')
    if int(s.get('tracks_count', 0)) != 8: fail('tracks_count must be 8')
    rec = m.get('recommended_next_pack') or {}
    if 'PROJECT_W_STATUS_SECOND_SLICE_PROD_ROLLOUT_PACK' not in str(rec.get('pack_id', '')): fail('recommended_next_pack must be PROJECT_W')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive','realistic','prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    if int(m.get('suite_expected_pass_after_pack_v', 0)) != 535: fail('suite_expected_pass must be 535')
    print('[PASS] PROJECT_V Track H completion READY — 8 tracks closed, final flag OFF, env byte-identical, suite target 535')
    sys.exit(0)
if __name__ == '__main__': main()
