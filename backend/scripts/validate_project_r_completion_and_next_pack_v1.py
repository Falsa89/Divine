#!/usr/bin/env python3
"""PROJECT_R Track H validator — pack completion + next pack roadmap."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_r_completion_and_next_pack_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_R_COMPLETION_AND_NEXT_PACK_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    summary = m.get('project_r_completion_summary') or {}
    if not summary:
        fail('project_r_completion_summary missing')
    for k in ('db_writes', 'battle_engine_mutated', 'battle_core_mutated', 'frontend_mutated', 'runtime_activated', 'live_env_flag_created'):
        if summary.get(k) is not False:
            fail(f'summary.{k} must be False')
    if summary.get('design_only') is not True:
        fail('summary.design_only must be True')
    if int(summary.get('tracks_count', 0)) != 8:
        fail(f'tracks_count must be 8 (got {summary.get("tracks_count")})')
    rec = m.get('recommended_next_pack') or {}
    if not rec.get('pack_id') or not rec.get('candidates'):
        fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k):
            fail(f'ETA {k} missing')
    if int(m.get('suite_expected_pass_after_pack_r', 0)) != 503:
        fail(f'suite_expected_pass_after_pack_r must be 503 (got {m.get("suite_expected_pass_after_pack_r")})')
    print('[PASS] PROJECT_R Track H completion + next pack roadmap READY — 8 tracks closed, design-only, suite target 503')
    sys.exit(0)


if __name__ == '__main__':
    main()
