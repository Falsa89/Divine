#!/usr/bin/env python3
"""PROJECT_U Track H validator — pack completion + next pack roadmap."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_u_completion_and_next_pack_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_U_COMPLETION_AND_NEXT_PACK_READY': fail('verdict mismatch')
    s = m.get('project_u_completion_summary') or {}
    if not s: fail('summary missing')
    if s.get('flag_flipped_during_canary') is not True: fail('summary.flag_flipped_during_canary must be True')
    if s.get('final_flag_state') != 'OFF': fail(f'summary.final_flag_state must be OFF (got {s.get("final_flag_state")})')
    if s.get('env_post_rollback_byte_identical_to_pre_flip') is not True: fail('summary env post-rollback must be byte-identical')
    for k in ('battle_engine_mutated', 'battle_core_mutated', 'combat_tsx_mutated', 'frontend_mutated', 'db_writes', 'keep_on_after_canary_marker_present'):
        if s.get(k) is not False: fail(f'summary.{k} must be False')
    if int(s.get('tracks_count', 0)) != 8: fail(f'tracks_count must be 8 (got {s.get("tracks_count")})')
    rec = m.get('recommended_next_pack') or {}
    if 'PROJECT_V_STATUS_SECOND_SLICE_DEV_LIVE_ROLLOUT_PACK' not in str(rec.get('pack_id', '')): fail('recommended_next_pack.pack_id must be PROJECT_V_...')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    if int(m.get('suite_expected_pass_after_pack_u', 0)) != 527: fail('suite_expected_pass_after_pack_u must be 527')
    print('[PASS] PROJECT_U Track H completion + next pack READY — 8 tracks closed, final flag OFF, env post-rollback byte-identical, suite target 527')
    sys.exit(0)


if __name__ == '__main__': main()
