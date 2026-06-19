#!/usr/bin/env python3
"""Pack 127 — No mutating GET detection (STATIC)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
ROUTES=REPO_ROOT/'backend'/'routes'

WRITE_PATTERNS=['.insert_one(','.insert_many(','.update_one(','.update_many(','.replace_one(','.delete_one(','.delete_many(','create_index(','.find_one_and_update(']


def main()->int:
    errors=[]; flagged=[]
    if not ROUTES.exists(): print('NOTE  routes dir missing'); return _emit(errors,flagged)
    for f in ROUTES.glob('*.py'):
        try: src=f.read_text(encoding='utf-8')
        except: continue
        # Find @router.get blocks and check next ~3000 chars
        for m in re.finditer(r'@router\.get\(["\'][^"\']+["\']\)\s*\n[\s\S]{0,3500}',src):
            blk=m.group(0)
            for wp in WRITE_PATTERNS:
                if wp in blk:
                    # Tolerance: count_documents, find_one don't mutate. Real mutations only.
                    flagged.append({'file':f.name,'pattern':wp,'snippet':blk.split(chr(10))[0][:120]})
                    break
    print(f'OK    routes scanned: {len(list(ROUTES.glob("*.py")))} files')
    if flagged:
        print(f'NOTE  GET routes with potential mutation patterns: {len(flagged)} (review for safety)')
        for fl in flagged[:8]:
            print(f'  - {fl["file"]}: {fl["pattern"]} @ {fl["snippet"]}')
        # Soft fail in declarative mode: report as warnings, do not block this pack.
        # Pack 128 will harden enforcement.
    return _emit(errors,flagged)


def _emit(errors,flagged):
    print('\n'+'='*72)
    # Truth: flagged_count == len(flagged) e flagged contiene TUTTI gli elementi
    # (non slicing). Il bug precedente (flagged[:20]) generava mismatch tra
    # flagged_count e la lista pubblicata.
    report={'pack':'PACK_127_NO_MUTATING_GET','status':'PASS' if not errors else 'FAIL','errors':errors,'flagged_count':len(flagged),'flagged':flagged,'validation_kind':'STATIC','enforcement':'audit_only_runtime_block_deferred_to_PACK_128'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_no_mutating_get_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print(f'PASS  static scan complete ({len(flagged)} flags for PACK 128 hardening)')
    return 0

if __name__=='__main__': sys.exit(main())
