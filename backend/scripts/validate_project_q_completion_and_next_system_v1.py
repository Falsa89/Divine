#!/usr/bin/env python3
"""PROJECT_Q Track H validator — pack completion + next system roadmap.

Verifica che il pack sia chiuso onestamente:
- verdict atteso
- artifact_live_import_executed_in_pack_q == False (5 firme mancanti)
- recommended_next_pack popolato
- ETAs presenti
- required_to_unblock_pack_q_live_import presente quando live_import_executed == false
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_q_completion_and_next_system_v1.json')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_H_PROJECT_Q_COMPLETION_AND_NEXT_SYSTEM_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    summary = m.get('project_q_completion_summary') or {}
    if not summary:
        fail('project_q_completion_summary missing')
    if summary.get('db_writes') is not False:
        fail('summary.db_writes must be False')
    if summary.get('live_import_executed') is not False:
        fail('summary.live_import_executed must be False')
    if summary.get('battle_engine_mutated') is not False:
        fail('summary.battle_engine_mutated must be False')
    if summary.get('frontend_mutated') is not False:
        fail('summary.frontend_mutated must be False')
    if int(summary.get('tracks_count', 0)) != 8:
        fail(f'tracks_count must be 8 (got {summary.get("tracks_count")})')
    rec = m.get('recommended_next_pack') or {}
    if not rec.get('pack_id') or not rec.get('candidates'):
        fail('recommended_next_pack incomplete')
    eta = m.get('honest_time_remaining_excluding_graphics_audio_art') or {}
    for k in ('aggressive', 'realistic', 'prudent'):
        if not eta.get(k):
            fail(f'ETA {k} missing')
    if m.get('artifact_live_import_executed_in_pack_q') is False:
        if not (m.get('required_to_unblock_pack_q_live_import') or []):
            fail('required_to_unblock_pack_q_live_import missing when live import not executed')
    if m.get('artifact_live_import_status') != 'PENDING_APPROVAL':
        fail(f'artifact_live_import_status must be PENDING_APPROVAL (got {m.get("artifact_live_import_status")})')
    print(f'[PASS] PROJECT_Q Track H completion READY — 8 tracks closed, live_import_executed=False, status=PENDING_APPROVAL')
    sys.exit(0)


if __name__ == '__main__':
    main()
