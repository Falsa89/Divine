#!/usr/bin/env python3
"""Pack 126-FIX-B — Validator: selected_server_id propagation in battle/hero-collection/pre-battle-lobby."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    'frontend/app/(tabs)/battle.tsx': ['selected_server_id', 'useServerScope'],
    'frontend/app/hero-collection.tsx': ['selected_server_id', 'useServerScope', 'server_id=${encodeURIComponent(selected_server_id)}'],
    'frontend/app/pre-battle-lobby.tsx': ['selectedServerId', 'get-formation?server_id=${encodeURIComponent(selectedServerId)}', '/api/user/heroes?server_id=${encodeURIComponent(selectedServerId)}'],
}


def main() -> int:
    errors = []
    for rel, pats in TARGETS.items():
        p = REPO_ROOT / rel
        if not p.exists():
            errors.append(f'missing {rel}'); continue
        src = p.read_text(encoding='utf-8')
        for pat in pats:
            if pat not in src:
                errors.append(f'{rel}: missing pattern `{pat}`')
            else:
                print(f'OK    {rel}: {pat}')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    report = {'pack':'PACK_126_FIX_B_SELECTED_SERVER_ID_PROPAGATION','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_b_selected_server_id_propagation_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  selected_server_id propagated across battle/hero-collection/pre-battle-lobby')
    return 0

if __name__ == '__main__': sys.exit(main())
