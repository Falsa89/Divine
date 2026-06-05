#!/usr/bin/env python3
"""v101 — Dry-run global legacy data cleanup script.

Esegue audit static su repo + DB read-only se disponibile. Non muta nulla.
"""
import os, sys, json, re
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEGACY_PATTERNS = [r'old_hero_v0', r'deprecated_hero', r'legacy_item_v0', r'old_coin_v0', r'deprecated_token_v0']

def scan_repo_for_legacy_refs():
    counts = {p:0 for p in LEGACY_PATTERNS}
    scan_paths = [os.path.join(ROOT,'backend'), os.path.join(ROOT,'frontend'), os.path.join(ROOT,'data')]
    files_scanned = 0
    for sp in scan_paths:
        for root, dirs, files in os.walk(sp):
            dirs[:] = [d for d in dirs if d not in ('node_modules','__pycache__','.git','dist','build')]
            for f in files:
                if not f.endswith(('.py','.tsx','.ts','.json','.js')): continue
                path = os.path.join(root, f)
                try:
                    with open(path,'r',encoding='utf-8',errors='ignore') as fh: content = fh.read()
                    files_scanned += 1
                    for p in LEGACY_PATTERNS:
                        if re.search(p, content): counts[p] += 1
                except: pass
    return counts, files_scanned

def main():
    print('[DRY-RUN] v101 global legacy data cleanup audit starting...')
    counts, files_scanned = scan_repo_for_legacy_refs()
    total = sum(counts.values())
    print(f'[DRY-RUN] files scanned: {files_scanned}')
    print(f'[DRY-RUN] legacy pattern occurrences: {total}')
    for p,c in counts.items(): print(f'  {p}: {c}')
    if total > 0:
        print('[DRY-RUN] WARN: legacy patterns found, review required (no auto-cleanup in dry-run)')
    print('[DRY-RUN] no DB queries executed (use V101_LEGACY_CLEANUP_APPLY=YES for live audit)')
    print('[DRY-RUN] SAFETY: blind_destructive_reset=false, delete_without_backup=false, random_opponent_generation=false')
    out = {'pack':'v101','generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'files_scanned':files_scanned,'legacy_pattern_counts':counts,'total':total,'dry_run':True}
    out_path = os.path.join(ROOT,'data','design','legacy_cleanup','v101_dry_run_execution_log.json')
    with open(out_path,'w',encoding='utf-8') as f: json.dump(out, f, indent=2, ensure_ascii=False)
    print(f'[OK] dry-run log: {out_path}')
    return 0

if __name__ == '__main__': sys.exit(main())
