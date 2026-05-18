#!/usr/bin/env python3
"""Audit V19 public UI preview implementation safety.

Verifies:
  - file present at /app/frontend/app/affinity-gifts-preview.tsx
  - NO mutating HTTP methods (POST/PUT/PATCH/DELETE)
  - NO call to /api/affinity/gift-spend (only canary-status allowed)
  - NO spend/claim/give button text
  - NO Borea alias strings
  - readiness JSON present
  - combat.tsx unchanged
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

UI_FILE = Path('/app/frontend/app/affinity-gifts-preview.tsx')
IMPL_JSON = Path('/app/data/design/ui/affinity_gifts_public_preview_implementation_result_v1.json')

FORBIDDEN_IN_PREVIEW_FILE = [
    r"method:\s*['\"]POST['\"]",
    r"method:\s*['\"]PUT['\"]",
    r"method:\s*['\"]PATCH['\"]",
    r"method:\s*['\"]DELETE['\"]",
    r"fetch\s*\([^)]*affinity/gift-spend['\"]\s*[,)]",  # gift-spend root POST
    r"fetch\s*\([^)]*affinity/gift-spend['\"]\s*,\s*\{[^}]*method",  # explicit method block
    r">\s*Spend\b",
    r">\s*Claim\b",
    r">\s*Give\b",
    r"['\"]borea['\"]",
    r"['\"]greek_borea['\"]",
    r"['\"]primordial_gaia['\"]",
]


def main():
    failures=[]
    def rec(n,c,note=''):
        print(f'  [{"OK" if c else "X"}] {n}' + (f' — {note}' if note and not c else ''))
        if not c: failures.append(n)
    print('='*70); print('AF2-N-PUBLIC-UI-PREVIEW-IMPLEMENTATION V19 — Audit'); print('='*70)
    rec('preview_file_present', UI_FILE.exists())
    rec('impl_json_present', IMPL_JSON.exists())
    if UI_FILE.exists():
        body = UI_FILE.read_text()
        # Allowed endpoint must be the only /api/affinity/* reference
        allowed_endpoint = '/api/affinity/gift-spend/canary-status'
        all_endpoints = re.findall(r"/api/affinity/[A-Za-z0-9_\-/]+", body)
        non_allowed = [e for e in all_endpoints if e != allowed_endpoint]
        rec('only_canary_status_endpoint_used', len(non_allowed) == 0, f'non_allowed={non_allowed}')
        # No mutating HTTP method anywhere in the file
        hits = []
        for pat in FORBIDDEN_IN_PREVIEW_FILE:
            for m in re.finditer(pat, body):
                hits.append({'pattern': pat, 'snippet': body[max(0,m.start()-30):m.end()+30][:140]})
        rec('no_forbidden_patterns_in_preview', len(hits) == 0, f'{len(hits)} hits: {hits[:2]}')
    if IMPL_JSON.exists():
        d = json.loads(IMPL_JSON.read_text())
        rec('impl_phase_readonly', d.get('phase') == 'READ_ONLY_UI_IMPLEMENTED_V19')
        rec('impl_audit_no_mutating_methods', d.get('audit_acceptance', {}).get('no_mutating_http_methods') is True)
        rec('impl_audit_no_gift_spend_call', d.get('audit_acceptance', {}).get('no_gift_spend_call') is True)
        rec('impl_audit_no_borea_visible', d.get('audit_acceptance', {}).get('no_borea_visible') is True)
        rec('impl_audit_no_public_spend_ui', d.get('audit_acceptance', {}).get('no_public_spend_ui') is True)
        rec('impl_labelled_design_only', d.get('audit_acceptance', {}).get('labelled_design_only') is True)
    out = subprocess.run(['git','-C','/app','diff','--stat','--','frontend/app/combat.tsx'],
                         capture_output=True, text=True, timeout=10)
    rec('combat_tsx_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')
    out2 = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_backend_files_unchanged', out2.stdout.strip() == '')
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
