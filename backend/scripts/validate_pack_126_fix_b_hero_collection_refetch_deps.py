#!/usr/bin/env python3
"""Pack 126-FIX-B — Validator: hero-collection refetch deps include selected_server_id + refreshToken."""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
T = REPO_ROOT / 'frontend' / 'app' / 'hero-collection.tsx'


def main() -> int:
    errors = []
    src = T.read_text(encoding='utf-8') if T.exists() else ''
    # Find useEffect that loads heroes and check its deps array
    m = re.search(r'useEffect\(\(\)\s*=>\s*\{[\s\S]*?/api/user/heroes[\s\S]*?\},\s*\[([^\]]+)\]', src)
    if not m:
        errors.append('useEffect with /api/user/heroes call not found')
    else:
        deps = m.group(1)
        print(f'OK    deps array: {deps.strip()}')
        if 'selected_server_id' not in deps:
            errors.append('selected_server_id missing in deps array')
        else:
            print('OK    selected_server_id in deps')
        if 'refreshToken' not in deps:
            errors.append('refreshToken missing in deps array')
        else:
            print('OK    refreshToken in deps')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    report = {'pack':'PACK_126_FIX_B_HERO_COLLECTION_REFETCH_DEPS','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_b_hero_collection_refetch_deps_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  hero-collection refetch deps include selected_server_id + refreshToken')
    return 0

if __name__ == '__main__': sys.exit(main())
