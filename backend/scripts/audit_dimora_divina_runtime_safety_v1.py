#!/usr/bin/env python3
# HOUSING RUNTIME SAFETY AUDIT (READ-ONLY)
# Verifica che NESSUN file runtime contenga riferimenti attivi al resolver Housing
# o al battle-bonus Housing.
import os, sys, re
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path('/app')
OUT = ROOT / 'data/design/housing/_dimora_divina_runtime_safety_audit_v1_result.json'
OUT.parent.mkdir(parents=True, exist_ok=True)

# Aree dove cerchiamo l'assenza di runtime housing
RUNTIME_DIRS = [
    ROOT / 'backend' / 'routes',
    ROOT / 'backend' / 'server.py',
]
# Pattern che indicherebbero implementazione runtime housing
FORBIDDEN_PATTERNS = [
    r'class\s+HousingBonusResolver',
    r'def\s+resolve_housing_bonus',
    r'from\s+\S+\s+import\s+HousingBonusResolver',
    r'/api/housing/(claim|claim-all|resident|resolve)',
]

BATTLE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]
BATTLE_FORBIDDEN_HOUSING = [
    r'housing_bonus', r'dimora_divina', r'sanctuary_housing',
]

def scan(paths, patterns):
    hits = []
    for p in paths:
        files = []
        if p.is_file():
            files = [p]
        elif p.is_dir():
            files = list(p.rglob('*.py')) + list(p.rglob('*.tsx')) + list(p.rglob('*.ts'))
        for f in files:
            try:
                t = f.read_text(errors='ignore')
            except Exception:
                continue
            for pat in patterns:
                for m in re.finditer(pat, t):
                    hits.append({'file':str(f),'pattern':pat,'match_start':m.start()})
    return hits

def main():
    errs = []
    runtime_hits = scan(RUNTIME_DIRS, FORBIDDEN_PATTERNS)
    if runtime_hits:
        for h in runtime_hits:
            errs.append(f'runtime_housing_present:{h["file"]}:{h["pattern"]}')
    battle_hits = scan(BATTLE_FILES, BATTLE_FORBIDDEN_HOUSING)
    if battle_hits:
        for h in battle_hits:
            errs.append(f'battle_file_housing_reference:{h["file"]}:{h["pattern"]}')

    out = {'task_origin':'DIMORA-DIVINA-RUNTIME-SAFETY-AUDIT','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"DIMORA-DIVINA-RUNTIME-SAFETY-AUDIT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
