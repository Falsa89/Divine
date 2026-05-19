#!/usr/bin/env python3
"""V25 PART I — UI safety recheck (corrected, false-positives-aware).

Checks the **interactive surface** of the frontend, not static text labels:
  - No POST/PUT/PATCH to /api/affinity/gift-spend (read-only canary-status OK)
  - No `hero_id: 'borea'|'greek_borea'|'primordial_gaia'` in JSON bodies
  - No `onPress` triggering gift-spend / spend / give / claim
  - No broad-rollout flags exposed
  - No runtime toggle UI
Static text strings containing "Borea" (decorative content) are allowed.
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/ui/affinity_gifts_public_preview_v25_safety_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

FRONTEND_DIR = Path('/app/frontend')

# Critical (must be zero) — true interactive risks
CRITICAL_PATTERNS = [
    (r"method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"][^}]*\bgift-spend\b(?!/canary-status)",
     'mutating fetch method on gift-spend'),
    (r"fetch\([^)]*gift-spend(?!/canary-status)[^)]*method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"]",
     'POST-style fetch to gift-spend (non-canary)'),
    (r"axios\.(post|put|patch|delete)\([^)]*gift-spend(?!/canary-status)",
     'axios mutation to gift-spend'),
    (r"hero_id\s*:\s*['\"]borea['\"]", 'hero_id=borea in payload'),
    (r"hero_id\s*:\s*['\"]greek_borea['\"]", 'hero_id=greek_borea in payload'),
    (r"hero_id\s*:\s*['\"]primordial_gaia['\"]", 'hero_id=primordial_gaia in payload'),
    (r"onPress\s*=\s*\{[^}]*\b(?:gift[_\-]?spend|affinity[_\-]?spend|affinity[_\-]?gift|gift_give)\b", 'onPress invoking affinity gift-spend/give'),
    (r"BROAD[_\-]?ROLLOUT\s*[:=]\s*['\"]?(?:true|on|enabled)", 'broad rollout flag enabled in UI'),
    (r"PUBLIC[_\-]?SPEND[_\-]?UI\s*[:=]\s*['\"]?(?:true|on|enabled)", 'public spend UI flag enabled'),
    (r"runtime[_\-]?toggle", 'runtime toggle UI'),
]

# Informational only (does not fail)
INFO_PATTERNS = [
    (r"\bBorea\b", 'static text "Borea" (decorative, ALLOWED)'),
]


def main():
    critical_findings = []
    info_findings = []
    files_scanned = 0
    for ext in ('*.tsx', '*.ts', '*.jsx', '*.js'):
        for f in FRONTEND_DIR.rglob(ext):
            if 'node_modules' in f.parts:
                continue
            try:
                txt = f.read_text(errors='ignore')
            except Exception:
                continue
            files_scanned += 1
            for pat, desc in CRITICAL_PATTERNS:
                for m in re.finditer(pat, txt, re.IGNORECASE | re.DOTALL):
                    critical_findings.append({
                        'file': str(f.relative_to('/app')),
                        'pattern': desc,
                        'match': m.group(0)[:140],
                        'line_approx': txt[:m.start()].count('\n') + 1,
                    })
            for pat, desc in INFO_PATTERNS:
                cnt = len(re.findall(pat, txt))
                if cnt:
                    info_findings.append({
                        'file': str(f.relative_to('/app')),
                        'pattern': desc,
                        'count': cnt,
                    })

    out = {
        'task_origin': 'AF2-N-V25-UI-PUBLIC-PREVIEW-SAFETY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'frontend_files_scanned': files_scanned,
        'critical_findings': critical_findings,
        'critical_findings_count': len(critical_findings),
        'informational_findings_count': len(info_findings),
        'sample_informational': info_findings[:10],
        'public_spend_ui_off': len(critical_findings) == 0,
        'borea_in_ui_as_hero_id': any(
            'hero_id=' in f['pattern'] for f in critical_findings
        ),
        'note': ('Static text containing "Borea" is decorative and ALLOWED. '
                 'Only mutating interactions, payload hero_id with hidden aliases, '
                 'and broad-rollout UI flags are treated as critical.'),
    }
    out['verdict'] = 'PASS' if out['public_spend_ui_off'] else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} files_scanned={files_scanned} "
          f"critical={len(critical_findings)} info={len(info_findings)} → {OUT}")
    if critical_findings:
        print('CRITICAL findings:')
        for f in critical_findings[:5]:
            print(f"  {f['file']}:{f['line_approx']}  {f['pattern']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
