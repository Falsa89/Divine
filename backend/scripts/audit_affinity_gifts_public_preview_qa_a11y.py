#!/usr/bin/env python3
"""V20 Public UI Preview QA/A11y Audit.

Validates:
  - file present
  - no mutating HTTP methods
  - no spend/claim/give button text
  - no Borea alias visible
  - 'Design only' / 'Spend disabled' label present
  - sanitized read-only canary status (no allowlist size/user ids/ledger counts)
  - mobile layout uses SafeAreaView + ScrollView + RefreshControl
  - accessibilityLabel / accessibilityRole present on key elements
  - status rows have non-color-only indicators (✓ prefix for good states)
  - no public route linking (no Stack/Tabs Link to this route in app router)
  - smoke render (cannot really render React Native without Metro; we do static
    syntactic / structural checks)
"""
from __future__ import annotations
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

UI = Path('/app/frontend/app/affinity-gifts-preview.tsx')
OUT = Path('/app/data/design/ui/affinity_gifts_public_preview_qa_a11y_audit_v1.json')

MUTATING_METHODS = [r"method:\s*['\"]POST['\"]", r"method:\s*['\"]PUT['\"]", r"method:\s*['\"]PATCH['\"]", r"method:\s*['\"]DELETE['\"]"]
FORBIDDEN_BUTTON_TEXT = [r">\s*Spend\b", r">\s*Claim\b", r">\s*Give\b"]
BOREA_ALIASES = ['borea', 'greek_borea', 'primordial_gaia']


def _scan_for_link_to_route():
    """Scan all frontend code (except the preview file itself) for Link/href to /affinity-gifts-preview."""
    hits = []
    for f in Path('/app/frontend').rglob('*'):
        if not f.is_file(): continue
        if f.suffix not in {'.ts','.tsx','.js','.jsx'}: continue
        if 'node_modules' in f.parts or '.expo' in f.parts: continue
        if f.resolve() == UI.resolve(): continue
        try:
            body = f.read_text(errors='ignore')
        except Exception: continue
        if 'affinity-gifts-preview' in body:
            hits.append(str(f))
    return hits


def main():
    audit = {
        'audit_id': 'affinity_gifts_public_preview_qa_a11y_audit_v1',
        'task_origin': 'AF2-N-PUBLIC-UI-PREVIEW-QA-A11Y-AUDIT-V20',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'design_only': True, 'runtime_attached': False,
        'file': str(UI),
        'checks': {},
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'stage4_applied': False, 'battle_runtime_attached': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': BOREA_ALIASES,
        }
    }
    failures = []
    def rec(n, c, note=''):
        audit['checks'][n] = {'pass': bool(c), 'note': note}
        print(f'  [{"OK" if c else "X"}] {n}' + (f' — {note}' if note and not c else ''))
        if not c: failures.append(n)
    print('='*70); print('AF2-N-PUBLIC-UI-PREVIEW QA/A11Y — Audit V20'); print('='*70)
    rec('file_present', UI.exists())
    if not UI.exists(): print('Overall: FAIL'); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(audit, indent=2) + '\n'); return 1
    body = UI.read_text()
    # Strip TS/JS comments before content-leak checks to avoid false positives
    # from legitimate "// Sanitize: never display canary_allowlist_size, ..." docs.
    body_no_comments = re.sub(r'//[^\n]*', '', body)
    body_no_comments = re.sub(r'/\*.*?\*/', '', body_no_comments, flags=re.S)
    rec('no_mutating_http_methods', not any(re.search(p, body) for p in MUTATING_METHODS))
    rec('no_spend_claim_give_button_text', not any(re.search(p, body) for p in FORBIDDEN_BUTTON_TEXT))
    rec('no_borea_alias_string', not any((f"'{a}'" in body) or (f'"{a}"' in body) for a in BOREA_ALIASES))
    rec('label_design_only_present', 'Design only' in body)
    rec('label_spend_disabled_present', 'Spend disabled' in body)
    rec('uses_only_canary_status', '/api/affinity/gift-spend/canary-status' in body)
    # ensure no other /api/affinity/* endpoint is referenced
    endpoints = re.findall(r"/api/affinity/[A-Za-z0-9_\-/]+", body)
    non_allowed = [e for e in endpoints if e != '/api/affinity/gift-spend/canary-status']
    rec('no_other_affinity_endpoint_referenced', len(non_allowed) == 0, f'non_allowed={non_allowed}')
    # Sanitization checks (use body_no_comments to avoid false positives from docs)
    rec('does_not_show_allowlist_size_field', 'canary_allowlist_size' not in body_no_comments)
    rec('does_not_show_user_ids', 'user_id' not in body_no_comments)
    rec('does_not_show_ledger_total_rows', 'ledger_total_rows' not in body_no_comments)
    rec('uses_count_only_for_hidden_aliases', '__hidden_aliases_blocked_count__' in body)
    # Mobile/layout
    rec('uses_SafeAreaView', 'SafeAreaView' in body)
    rec('uses_ScrollView', 'ScrollView' in body)
    rec('uses_RefreshControl', 'RefreshControl' in body)
    rec('uses_StyleSheet', 'StyleSheet.create' in body)
    rec('uses_Platform_handling', 'Platform' in body)
    # A11y
    a11y_label_count = len(re.findall(r'accessibilityLabel\s*=', body))
    a11y_role_count = len(re.findall(r'accessibilityRole\s*=', body))
    rec('accessibility_labels_count_ge_5', a11y_label_count >= 5, f'count={a11y_label_count}')
    rec('accessibility_roles_count_ge_4', a11y_role_count >= 4, f'count={a11y_role_count}')
    # No color-only indicator: good states have a checkmark prefix '✓ '
    rec('non_color_only_indicator_for_good_states', "'✓ '" in body or '\u2713 ' in body or '"✓ "' in body)
    # No discoverability link
    link_hits = _scan_for_link_to_route()
    rec('no_public_menu_or_tabs_link_to_preview', len(link_hits) == 0, f'hits={link_hits}')
    # Combat files unchanged
    out = subprocess.run(['git','-C','/app','diff','--stat','--','frontend/app/combat.tsx'],
                         capture_output=True, text=True, timeout=10)
    rec('combat_tsx_unchanged', out.stdout.strip() == '')
    out2 = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_backend_unchanged', out2.stdout.strip() == '')
    # Static smoke: file parses-ish (balanced braces; brackets; double quotes)
    rec('balanced_braces', body.count('{') == body.count('}'))
    rec('balanced_brackets', body.count('[') == body.count(']'))
    rec('balanced_parens', body.count('(') == body.count(')'))

    overall_pass = not failures
    audit['overall_status'] = 'PASS' if overall_pass else 'FAIL'
    audit['failures_count'] = len(failures)
    audit['a11y_label_count'] = a11y_label_count
    audit['a11y_role_count'] = a11y_role_count
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print('-'*70); print('Overall:', 'PASS' if overall_pass else 'FAIL')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
