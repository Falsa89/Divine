#!/usr/bin/env python3
"""V23 — UI safety recheck (same constraints as V22)."""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path

UI = Path('/app/frontend/app/affinity-gifts-preview.tsx')
OUT = Path('/app/data/design/ui/affinity_gifts_public_preview_v23_safety_result.json')


def main():
    if not UI.exists():
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({'overall_status':'FAIL','reason':'UI missing'}, indent=2))
        print('FAIL: ui_missing'); return 2
    t = UI.read_text(encoding='utf-8', errors='ignore')
    stripped = re.sub(r'/\*.*?\*/','',t,flags=re.DOTALL)
    stripped = '\n'.join(ln.split('//')[0] for ln in stripped.splitlines())
    checks = {}
    checks['no_post_method'] = ("method: 'POST'" not in stripped and 'method: "POST"' not in stripped
                                 and "method:'POST'" not in stripped)
    checks['no_put_patch_delete'] = all(
        f"method: '{m}'" not in stripped and f'method: "{m}"' not in stripped
        for m in ('PUT','PATCH','DELETE')
    )
    checks['no_borea_in_code'] = all(x not in stripped.lower() for x in ['borea','greek_borea','primordial_gaia'])
    code_paths = re.findall(r"[`'\"][^`'\"]*/api/affinity/gift-spend[^`'\"]*[`'\"]", stripped)
    checks['fetch_only_canary_status'] = (len(code_paths) >= 1) and all('canary-status' in p for p in code_paths)
    checks['no_runtime_toggle_word'] = all(w not in stripped.lower() for w in ['toggle','set_flag','enable_runtime'])
    checks['no_broad_rollout_terms'] = all(w not in stripped.lower() for w in ['broad_rollout','broadrollout'])
    checks['has_accessibility'] = 'accessibilityLabel' in t or 'accessibilityRole' in t
    overall = all(checks.values())
    out_doc = {
        'result_id':'affinity_gifts_public_preview_v23_safety_result',
        'task_origin':'V23-AF2N-PUBLIC-UI-SAFETY-RECHECK',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'ui_path': str(UI), 'checks': checks,
        'overall_status': 'PASS' if overall else 'FAIL',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    if not overall:
        for k,v in checks.items():
            if not v: print(f'FAIL: {k}')
        return 2
    print('PASS: AF2-N-PUBLIC-UI-V23-SAFETY'); return 0


if __name__ == '__main__':
    sys.exit(main())
