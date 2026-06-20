#!/usr/bin/env python3
"""POST_CHAIN — Future Pack Leak Guard.

Enforces that no unauthorized Pack 134+ implementation file has been added
to the repository. Distinguishes between:
- ROADMAP/DOC mentions (allowed inside post-chain docs and this validator);
- REAL implementation files (BLOCKED).

Real-file leak patterns checked (file NAMES only):
  pack_134, PACK_134, v134_, 536_PACK_134, 537_PACK_134, ...
  pack_135, PACK_135, etc.

Allowlist of paths where these tokens may appear as STRINGS (mentions):
- docs/divine/536_POST_CHAIN_*.md (this hygiene pass docs)
- backend/scripts/validate_post_chain_future_pack_leak_guard.py (self)
- data/design/system_safety/post_chain_repo_hygiene_pass_1_marker.json
- docs/divine/535_PACK_133_*FINAL_REPORT.md (mentions Pack 134 in recommendation)

Main check: NAME-based (no file in repo matching real-leak NAME patterns).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IGNORE = ['.git/', 'node_modules/', '__pycache__/', '.expo/']
# Real-file leak NAME patterns (file names matching these are blocked).
LEAK_NAME_RE = re.compile(r'(?:^|/|_)pack_(13[4-9]|1[4-9]\d|[2-9]\d{2})[._-]', re.IGNORECASE)
LEAK_NAME_RE_2 = re.compile(r'^(?:536|537|538|539|54\d|55\d|56\d|57\d|58\d|59\d|6\d{2})_PACK_(13[4-9]|1[4-9]\d|[2-9]\d{2})_', re.IGNORECASE)
LEAK_V_RE = re.compile(r'^v(13[4-9]|1[4-9]\d|[2-9]\d{2})_', re.IGNORECASE)


def _is_leak_filename(name):
    return bool(LEAK_NAME_RE.search(name) or LEAK_NAME_RE_2.search(name) or LEAK_V_RE.search(name))


def main():
    errs, scanned, leaks = [], 0, []
    for p in REPO_ROOT.rglob('*'):
        if not p.is_file():
            continue
        rel = str(p.relative_to(REPO_ROOT))
        if any(s in rel for s in IGNORE):
            continue
        scanned += 1
        # Allow file 536_POST_CHAIN_REPO_HYGIENE_PASS_1_*.md (no pack number 134+ in name).
        # The regex LEAK_NAME_RE_2 catches '536_PACK_134_*'; '536_POST_CHAIN_*' does not match.
        if _is_leak_filename(p.name):
            leaks.append(rel)
    if leaks:
        for f in leaks[:30]:
            errs.append(f'future-pack file leak: {f}')
    return _emit(errs, scanned, leaks)


def _emit(errs, scanned, leaks):
    report = {'pack': 'POST_CHAIN_FUTURE_PACK_LEAK_GUARD',
              'status': 'PASS' if not errs else 'FAIL',
              'errors': errs,
              'files_scanned': scanned,
              'leak_files_detected': leaks,
              'guard_scope': 'Pack 134..Pack 999 (NAME-based)',
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'post_chain_future_pack_leak_guard_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errs:
        for e in errs: print(f'FAIL {e}')
        return 1
    print(f'PASS  no future-pack (134+) file leak ({scanned} files scanned)')
    return 0


if __name__ == '__main__': sys.exit(main())
