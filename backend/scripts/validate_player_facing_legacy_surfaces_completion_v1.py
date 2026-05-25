#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track H completion validator.
import json, sys, hashlib
from pathlib import Path

P = Path('/app/data/design/project_management/project_player_facing_legacy_surfaces_completion_v1.json')
SAFE = Path('/app/frontend/app/safe-previews.tsx')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')


def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> int:
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_PLAYER_FACING_LEGACY_SURFACES_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT_READY'
    # Tutti i track verdetti READY/IMPLEMENTED
    for k in 'ABCDEFGH':
        v = d['track_verdicts'][k]
        assert 'READY' in v or 'IMPLEMENTED_SAFE' in v, f'track {k} not READY: {v}'
    # Invarianti MD5
    assert md5_of(BE) == d['invariant_files_md5']['battle_engine_py'], 'battle_engine.py drift'
    assert md5_of(ENV) == d['invariant_files_md5']['backend_env'], '.env drift'
    # Safe previews aggiornato
    assert md5_of(SAFE) == d['safe_previews_tsx_md5_post'], 'safe-previews.tsx drift'
    # No backend/db changes
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['flag_flips'] == 0
    assert d['new_live_buttons'] == 0
    assert d['new_api_calls'] == 0
    assert d['frontend_changes'] == 1
    # Progress diff <= 1pp
    diff = d['progress_estimate']['global_project_post'] - d['progress_estimate']['global_project_pre']
    assert 0 <= diff <= 1.0
    # Next pack order popolato
    assert len(d['recommended_next_pack_order']) >= 5
    print('[PASS] PLAYER-LEGACY Track H completion \u2014 next={}'.format(d['recommended_next_pack_order'][0]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
