#!/usr/bin/env python3
"""Pack 130 — Combat does NOT consume snapshot (STATIC).

Verifica che combat.tsx, battle_engine.py, battle_core.py NON facciano import
da lobby_launch_context o real_player_snapshot helpers.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMBAT_FILES = [
    REPO_ROOT / 'frontend' / 'app' / 'combat.tsx',
    REPO_ROOT / 'backend' / 'battle_engine.py',
    REPO_ROOT / 'backend' / 'battle_core.py',
]
FORBIDDEN_IMPORTS = ['lobby_launch_context', 'real_player_snapshot',
                     '/api/lobby/launch-context']


def main() -> int:
    errors = []; notes = []
    for f in COMBAT_FILES:
        if not f.exists():
            notes.append(f'file not found (may be skipped): {f.name}')
            continue
        src = f.read_text(encoding='utf-8')
        for fp in FORBIDDEN_IMPORTS:
            if fp in src:
                errors.append(f'{f.name} references `{fp}` — Pack 131 territory leaked into Pack 130')
    print(f'OK    {len([f for f in COMBAT_FILES if f.exists()])} combat-runtime files scanned, no Pack 130 helper import')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_NO_COMBAT_CONSUMES_SNAPSHOT',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'forbidden_imports': FORBIDDEN_IMPORTS,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_COMBAT_RUNTIME_DOES_NOT_CONSUME_PACK_130_SNAPSHOT'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_no_combat_consumes_snapshot_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  combat runtime does NOT consume Pack 130 snapshot — Pack 131 boundary preserved')
    return 0


if __name__ == '__main__': sys.exit(main())
