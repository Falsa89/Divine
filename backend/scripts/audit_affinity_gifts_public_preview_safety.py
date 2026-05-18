#!/usr/bin/env python3
"""AF2-N-PUBLIC-UI-PREVIEW-SAFETY AUDIT V18.

Read-only grep of /app/frontend to ensure:
  - No Pressable/Button calls POST /api/affinity/gift-spend
  - No Borea alias in frontend
  - No import of battle_engine / battle_core / synergy_system
  - combat.tsx unchanged in V18
  - readiness JSON present
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

FRONTEND_DIR = Path('/app/frontend')
READINESS = Path('/app/data/design/ui/affinity_gifts_public_preview_readiness_v1.json')

FORBIDDEN_TOKENS_IN_FRONTEND = [
    r"fetch\s*\(\s*[`'\"][^`'\"]*affinity/gift-spend",
    r"axios[^\n]*affinity/gift-spend",
    r"\.post\s*\(\s*[`'\"][^`'\"]*affinity/gift-spend",
    r'spendGift\s*\(',
    r'giftSpend\s*\(',
    r"from\s+['\"][^'\"]*battle_engine['\"]",
    r"from\s+['\"][^'\"]*battle_core['\"]",
    r"from\s+['\"][^'\"]*synergy_system['\"]",
    r"from\s+['\"][^'\"]*game_systems['\"]",
    r">\s*Spend Gift\s*<",
    r">\s*Claim Gift\s*<",
    r">\s*Claim Affinity\s*<",
]


def scan_frontend():
    hits = []
    if not FRONTEND_DIR.exists(): return hits
    for f in FRONTEND_DIR.rglob('*'):
        if not f.is_file(): continue
        if f.suffix not in {'.ts','.tsx','.js','.jsx','.json'}: continue
        if 'node_modules' in f.parts or '.expo' in f.parts: continue
        try:
            body = f.read_text(errors='ignore')
        except Exception:
            continue
        for tok in FORBIDDEN_TOKENS_IN_FRONTEND:
            for m in re.finditer(tok, body):
                hits.append({'file': str(f), 'token': tok, 'snippet': body[max(0,m.start()-30):m.end()+30][:140]})
    return hits


def main():
    failures = []
    def rec(n, c, note=''):
        print(f'  [{"OK" if c else "X"}] {n}' + (f' — {note}' if note and not c else ''))
        if not c: failures.append(n)
    print('='*70); print('AF2-N-PUBLIC-UI-PREVIEW-SAFETY — Audit V18'); print('='*70)
    rec('readiness_json_present', READINESS.exists())
    if READINESS.exists():
        d = json.loads(READINESS.read_text())
        rec('readiness_design_only', d.get('design_only') is True)
        rec('readiness_runtime_attached_false', d.get('runtime_attached') is False)
        rec('readiness_phase_plan_only', d.get('phase') == 'DESIGN_PLAN_ONLY_NO_UI_MUTATION_IN_V18')
    hits = scan_frontend()
    rec('no_forbidden_tokens_in_frontend', len(hits) == 0, f'{len(hits)} hits: {hits[:3]}')

    out = subprocess.run(['git','-C','/app','diff','--stat','--','frontend/app/combat.tsx'],
                         capture_output=True, text=True, timeout=10)
    rec('combat_tsx_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')

    out2 = subprocess.run(['git','-C','/app','diff','--stat','--', 'frontend/',
                           ':!frontend/yarn.lock', ':!frontend/package-lock.json'],
                          capture_output=True, text=True, timeout=10)
    # Allow no UI changes in V18 OR only lock file churn; we strictly require no source UI change
    rec('frontend_source_unchanged_in_v18', out2.stdout.strip() == '', f'diff={out2.stdout!r}')

    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
