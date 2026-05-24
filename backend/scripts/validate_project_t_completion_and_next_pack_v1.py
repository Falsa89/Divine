#!/usr/bin/env python3
"""PROJECT_T Track H validator — pack completion + next pack roadmap."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_t_completion_and_next_pack_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_T_COMPLETION_AND_NEXT_PACK_READY': fail('verdict mismatch')
    s = m.get('project_t_completion_summary') or {}
    if not s: fail('summary missing')
    if s.get('battle_engine_wired') is not True: fail('summary.battle_engine_wired must be True')
    for k in ('battle_engine_runtime_behavior_changed_with_flag_off', 'flag_in_live_env', 'battle_core_mutated', 'combat_tsx_mutated', 'frontend_mutated', 'db_writes'):
        if s.get(k) is not False: fail(f'summary.{k} must be False')
    if s.get('rollback_drill_passed') is not True: fail('summary.rollback_drill_passed must be True')
    if int(s.get('tracks_count', 0)) != 8: fail(f'tracks_count must be 8 (got {s.get("tracks_count")})')
    rec = m.get('recommended_next_pack') or {}
    if 'PROJECT_U_STATUS_SECOND_SLICE_CANARY_ENV_FLAG_FLIP_PACK' not in str(rec.get('pack_id', '')): fail('recommended_next_pack.pack_id must be PROJECT_U_...')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k): fail(f'ETA {k} missing')
    if int(m.get('suite_expected_pass_after_pack_t', 0)) != 519: fail('suite_expected_pass_after_pack_t must be 519')
    print('[PASS] PROJECT_T Track H completion + next pack READY — 8 tracks closed, wiring applied flag-off-safe, suite target 519')
    sys.exit(0)


if __name__ == '__main__': main()
