#!/usr/bin/env python3
"""
Pack 126 — Validator: preview result has NO fake EXP / no rewards.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / 'frontend' / 'components' / 'battle' / 'buildPostBattleSummary.ts'
COMBAT = REPO_ROOT / 'frontend' / 'app' / 'combat.tsx'


def main() -> int:
    errors = []
    src_b = BUILDER.read_text(encoding='utf-8') if BUILDER.exists() else ''
    src_c = COMBAT.read_text(encoding='utf-8') if COMBAT.exists() else ''
    # buildPostBattleSummary: preview short-circuit
    if 'is_preview_local' not in src_b or 'is_preview || result?.preview' not in src_b:
        errors.append('buildPostBattleSummary does not short-circuit preview (is_preview_local | is_preview | preview)')
    else:
        print('OK    buildPostBattleSummary short-circuits on preview')
    # Old `Math.max(1, ...)` clamp removed
    if 'Math.max(1, Math.floor(totalHeroExp' in src_b:
        errors.append('Math.max(1,...) clamp still present (would give fake +1 EXP)')
    else:
        print('OK    Math.max(1,...) clamp REMOVED (no fake +1 EXP)')
    # combat.tsx: explicit no-reward banner in result phase
    if "PREVIEW COMPLETATA" not in src_c:
        errors.append('combat.tsx missing PREVIEW COMPLETATA banner in result phase')
    else:
        print('OK    combat.tsx PREVIEW COMPLETATA banner present')
    if 'Nessuna EXP' not in src_c or 'Nessun reward' not in src_c:
        errors.append('combat.tsx missing explicit no-EXP/no-reward labels')
    else:
        print('OK    explicit no-EXP/no-reward labels present')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126 — preview result no fake EXP')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_PREVIEW_RESULT_NO_FAKE_EXP', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_preview_result_no_fake_exp_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  preview result shows 0 EXP, 0 rewards, explicit no-progress banner')
    return 0


if __name__ == '__main__':
    sys.exit(main())
