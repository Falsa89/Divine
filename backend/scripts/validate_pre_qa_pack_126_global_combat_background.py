#!/usr/bin/env python3
"""
Pack 126 — Validator: global combat background fallback for preview modes.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BG = REPO_ROOT / 'frontend' / 'components' / 'ui' / 'battleBackgrounds.ts'
COMBAT = REPO_ROOT / 'frontend' / 'app' / 'combat.tsx'

REQUIRED_BG = [
    ('mode?: string', 'mode field in BattleBgContext'),
    ('MODE_BG_FALLBACK', 'mode-to-faction fallback map'),
    ("story: 'greek'", 'story mode fallback'),
    ("tower: 'norse'", 'tower mode fallback'),
    ("training: 'celtic'", 'training mode fallback'),
    ("arena: 'greek'", 'arena mode fallback'),
    ("boss: 'egyptian'", 'boss mode fallback'),
    ("raid: 'egyptian'", 'raid mode fallback'),
    ('hero_id || hero.id', 'extractFaction fallback on hero_id prefix'),
]
REQUIRED_COMBAT = [
    ('mode: previewCtxLocal.mode', 'preview branch passes mode to pickBattleBackground'),
]


def main() -> int:
    errors = []
    src_bg = BG.read_text(encoding='utf-8') if BG.exists() else ''
    src_combat = COMBAT.read_text(encoding='utf-8') if COMBAT.exists() else ''
    for pat, desc in REQUIRED_BG:
        if pat not in src_bg:
            errors.append(f'battleBackgrounds.ts missing `{pat}`: {desc}')
        else:
            print(f'OK    {desc}')
    for pat, desc in REQUIRED_COMBAT:
        if pat not in src_combat:
            errors.append(f'combat.tsx missing `{pat}`: {desc}')
        else:
            print(f'OK    {desc}')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126 — global combat background')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_GLOBAL_COMBAT_BACKGROUND', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_global_combat_background_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  global combat background mode fallback present, never null in preview')
    return 0


if __name__ == '__main__':
    sys.exit(main())
