"""validate_project_guide_codex_fill_gaps_v1.py

MEGA_BATCH_ACCELERATION_1 TRACK D validator. Content foundation only.
No runtime/tutorial/home/menu wiring.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'data' / 'design' / 'guide_codex' / 'guide_codex_fill_gaps_v1.json'
MARKER = ROOT / 'data' / 'design' / 'guide_codex' / 'guide_codex_fill_gaps_proof_marker_v1.json'

FAILS: list[str] = []


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    if not GUIDE.exists():
        _fail(f'guide file missing: {GUIDE}')
        print('[FAIL] PROJECT_GUIDE_CODEX_FILL_GAPS validator')
        for f in FAILS:
            print('  -', f)
        return 1
    d = json.loads(GUIDE.read_text())
    topics = d.get('topics') or []
    ids = {t.get('id') for t in topics if isinstance(t, dict)}
    required = {
        'story_visual_battle_transition', 'battle_report_replay_save_share',
        'gear', 'gemme', 'rune', 'material_raid', 'artifact', 'divine_weapon', 'guild_war',
    }
    missing = required - ids
    if missing:
        _fail(f'guide missing topics: {sorted(missing)}')

    # Gemme vs Rune separation must be explicit
    gemme = next((t for t in topics if t.get('id') == 'gemme'), {})
    rules = ' '.join(gemme.get('key_rules', []) if isinstance(gemme, dict) else [])
    if 'Rune' not in rules or 'socket' not in rules.lower():
        _fail('gemme topic must explicitly separate from Rune and mention socket')

    artifact = next((t for t in topics if t.get('id') == 'artifact'), {})
    art_rules = ' '.join(artifact.get('key_rules', []) if isinstance(artifact, dict) else [])
    if 'Divine' not in art_rules:
        _fail('artifact topic must explicitly separate from Divine Weapon')

    if d.get('runtime_wiring_changed') is not False:
        _fail('guide.runtime_wiring_changed must be false')
    if d.get('tutorial_unlock_changed') is not False:
        _fail('guide.tutorial_unlock_changed must be false')

    if not MARKER.exists():
        _fail(f'guide marker missing: {MARKER}')
    else:
        m = json.loads(MARKER.read_text())
        for k in ('gemme_vs_rune_separated', 'artifact_vs_divine_weapon_separated',
                  'story_visual_battle_transition_explained', 'guild_war_exception_explained'):
            if m.get(k) is not True:
                _fail(f'marker.{k} must be true')
        if m.get('db_writes') != 0:
            _fail('marker.db_writes must be 0')

    if FAILS:
        print('[FAIL] PROJECT_GUIDE_CODEX_FILL_GAPS validator')
        for f in FAILS:
            print('  -', f)
        return 1
    print('[PASS] PROJECT_GUIDE_CODEX_FILL_GAPS validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
