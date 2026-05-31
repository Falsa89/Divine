"""validate_mega_batch_acceleration_1_rollup.py

Rollup validator for MEGA_BATCH_ACCELERATION_1. Aggregates all 4 track validators,
asserts proof markers exist, forbidden files unchanged via simple presence checks,
and suite runner contains each tuple exactly once.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'backend' / 'scripts'
SUITE = SCRIPTS / 'run_hero_skill_kit_validator_suite.py'

VALIDATORS = [
    'validate_project_story_battle_instance_preview_endpoint_v1.py',
    'validate_project_material_raid_gem_track_preview_unlock_v1.py',
    'validate_project_mode_battle_entrypoint_registry_expansion_v1.py',
    'validate_project_guide_codex_fill_gaps_v1.py',
]

TUPLES = [
    "PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT",
    "PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK",
    "PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION",
    "PROJECT-GUIDE-CODEX-FILL-GAPS",
    "MEGA-BATCH-ACCELERATION-1-ROLLUP",
]

MARKERS = [
    ROOT / 'data' / 'design' / 'story_visual_battle' / 'story_battle_instance_preview_endpoint_proof_marker_v1.json',
    ROOT / 'data' / 'design' / 'material_raid_runtime' / 'material_raid_gem_track_preview_unlock_proof_marker_v1.json',
    ROOT / 'data' / 'design' / 'battle_entrypoints' / 'mode_battle_entrypoint_registry_expansion_proof_marker_v1.json',
    ROOT / 'data' / 'design' / 'guide_codex' / 'guide_codex_fill_gaps_proof_marker_v1.json',
    ROOT / 'data' / 'design' / 'mega_batch_acceleration' / 'mega_batch_acceleration_1_proof_marker_v1.json',
]

FAILS: list[str] = []


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    # 1) all validators executable and PASS
    for v in VALIDATORS:
        path = SCRIPTS / v
        if not path.exists():
            _fail(f'missing validator file: {v}')
            continue
        try:
            r = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                _fail(f'validator FAILED: {v} :: stdout={r.stdout.strip()[:200]} :: stderr={r.stderr.strip()[:200]}')
        except Exception as e:
            _fail(f'validator exec error: {v} :: {e}')

    # 2) all proof markers exist + db_writes=0 where applicable
    for mp in MARKERS:
        if not mp.exists():
            _fail(f'missing proof marker: {mp}')
            continue
        try:
            d = json.loads(mp.read_text())
            if d.get('db_writes', 0) != 0:
                _fail(f'marker {mp.name} db_writes != 0')
        except Exception as e:
            _fail(f'marker {mp.name} invalid JSON: {e}')

    # 3) suite runner contains each tuple exactly once
    if not SUITE.exists():
        _fail('suite runner missing')
    else:
        txt = SUITE.read_text()
        for tid in TUPLES:
            n = len(re.findall(re.escape("'" + tid + "'"), txt))
            if n == 0:
                _fail(f"suite runner missing tuple id: {tid}")
            elif n > 1:
                _fail(f"suite runner duplicate tuple id (count={n}): {tid}")
        if 'PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1' not in txt:
            _fail('suite runner missing PUBLIC_SYNC_TAG_v31_MEGA_BATCH_ACCELERATION_1 sentinel')
        if 'MEGA_BATCH_ACCELERATION_1_REGISTRATION_SENTINEL' not in txt:
            _fail('suite runner missing MEGA_BATCH_ACCELERATION_1_REGISTRATION_SENTINEL')

    # 4) forbidden files unchanged (presence + known markers)
    story = ROOT / 'frontend' / 'app' / 'story.tsx'
    if story.exists() and '/api/story/battle' not in story.read_text():
        _fail('story.tsx no longer references /api/story/battle')
    combat = ROOT / 'frontend' / 'app' / 'combat.tsx'
    if combat.exists() and '/api/battle/simulate' not in combat.read_text():
        _fail('combat.tsx no longer references /api/battle/simulate')
    be = ROOT / 'backend' / 'battle_engine.py'
    if not be.exists():
        _fail('battle_engine.py missing')

    if FAILS:
        print('[FAIL] MEGA_BATCH_ACCELERATION_1 rollup validator')
        for f in FAILS:
            print('  -', f)
        return 1
    print('[PASS] MEGA_BATCH_ACCELERATION_1 rollup validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
