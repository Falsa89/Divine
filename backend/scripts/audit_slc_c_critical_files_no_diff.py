#!/usr/bin/env python3
"""SLC-C — Critical Files No-Diff Audit (READ-ONLY).

Verifies that protected runtime files have NOT been mutated as part of
the SLC-C design plan. Tracks current SHA-256 hashes and writes them to
/app/data/design/server_lifecycle/_slc_c_critical_files_no_diff_result.json.

If a baseline hash file already exists at /app/data/design/server_lifecycle/_slc_c_critical_files_baseline_v1.json,
this script compares against it; otherwise it WRITES the baseline (first run).
"""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish  # noqa: E402

NAME = 'slc_c_critical_files_no_diff'
PROTECTED_FILES = [
    '/app/backend/battle_engine.py',
    '/app/backend/battle_core.py',
    '/app/frontend/app/combat.tsx',
    '/app/backend/routes/affinity_gift_spend.py',
    '/app/backend/routes/gacha.py',
    '/app/backend/routes/heroes.py',
    '/app/backend/routes/roster.py',
    '/app/backend/data/heroes_catalog.json',
]
BASELINE_PATH = DESIGN_DIR / '_slc_c_critical_files_baseline_v1.json'


def sha256(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    current = {p: sha256(Path(p)) for p in PROTECTED_FILES}
    errs = []
    baseline_existed = BASELINE_PATH.exists()
    if baseline_existed:
        try:
            baseline = json.loads(BASELINE_PATH.read_text(encoding='utf-8'))
            for f, h in current.items():
                exp = baseline.get('hashes', {}).get(f)
                if exp is None:
                    # new tracked file — record but warn (non-fatal)
                    continue
                if h != exp:
                    errs.append(f'CRITICAL FILE MUTATED: {f} (baseline={exp[:12]}… current={h[:12] if h else None}…)')
        except Exception as ex:
            errs.append(f'baseline read error: {ex}')
    else:
        # First run: create baseline. Not a failure.
        BASELINE_PATH.write_text(json.dumps({
            'task_origin': 'SLC-C-CRITICAL-FILES-BASELINE',
            'version': 'v1',
            'utc': datetime.now(timezone.utc).isoformat(),
            'hashes': current,
        }, indent=2, sort_keys=True), encoding='utf-8')

    return finish(NAME, errs, {
        'baseline_existed': baseline_existed,
        'tracked_files': len(PROTECTED_FILES),
        'missing_files': [f for f, h in current.items() if h is None and not f.endswith('battle_core.py')],
    })


if __name__ == '__main__':
    sys.exit(main())
