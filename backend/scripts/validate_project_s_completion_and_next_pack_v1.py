#!/usr/bin/env python3
"""PROJECT_S Track H validator — pack completion + next pack roadmap."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_s_completion_and_next_pack_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_S_COMPLETION_AND_NEXT_PACK_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    summary = m.get('project_s_completion_summary') or {}
    if not summary:
        fail('project_s_completion_summary missing')
    if summary.get('pure_resolver_module_created') is not True:
        fail('summary.pure_resolver_module_created must be True')
    for k in ('runtime_imported_anywhere', 'battle_engine_mutated', 'battle_core_mutated', 'frontend_mutated', 'env_flag_created_in_live_env', 'db_writes'):
        if summary.get(k) is not False:
            fail(f'summary.{k} must be False')
    if int(summary.get('tracks_count', 0)) != 8:
        fail(f'tracks_count must be 8 (got {summary.get("tracks_count")})')
    rec = m.get('recommended_next_pack') or {}
    if 'PROJECT_T_STATUS_SECOND_SLICE_SINGLE_POINT_WIRING_CANARY_PACK' not in str(rec.get('pack_id', '')):
        fail('recommended_next_pack.pack_id must be PROJECT_T_..._SINGLE_POINT_WIRING_CANARY_PACK')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k):
            fail(f'ETA {k} missing')
    if int(m.get('suite_expected_pass_after_pack_s', 0)) != 511:
        fail(f'suite_expected_pass_after_pack_s must be 511 (got {m.get("suite_expected_pass_after_pack_s")})')
    print('[PASS] PROJECT_S Track H completion + next pack READY — 8 tracks closed, resolver created, suite target 511')
    sys.exit(0)


if __name__ == '__main__': main()
