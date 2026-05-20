#!/usr/bin/env python3
"""V29 PART J — UI safety audit V29."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/ui/affinity_gifts_public_preview_v29_safety_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR = Path('/app/frontend')

CRITICAL = [
    (r"method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"][^}]*\bgift-spend\b(?!/canary-status)", 'mutating fetch'),
    (r"axios\.(post|put|patch|delete)\([^)]*gift-spend(?!/canary-status)", 'axios mutation'),
    (r"hero_id\s*:\s*['\"]borea['\"]", 'hero_id=borea'),
    (r"hero_id\s*:\s*['\"]greek_borea['\"]", 'hero_id=greek_borea'),
    (r"hero_id\s*:\s*['\"]primordial_gaia['\"]", 'hero_id=primordial_gaia'),
    (r"onPress\s*=\s*\{[^}]*\b(?:gift[_\-]?spend|affinity[_\-]?gift|gift_give|gift_claim)\b", 'onPress gift mutation'),
    (r"BROAD[_\-]?ROLLOUT\s*[:=]\s*['\"]?(?:true|on|enabled)", 'broad rollout flag'),
    (r"PUBLIC[_\-]?SPEND[_\-]?UI\s*[:=]\s*['\"]?(?:true|on|enabled)", 'public spend UI'),
    (r"runtime[_\-]?toggle", 'runtime toggle UI'),
    (r"battle[_\-]?wiring\s*[:=]\s*['\"]?(?:true|on|enabled)", 'battle wiring UI'),
]


def main():
    critical = []; files_scanned = 0
    for ext in ('*.tsx', '*.ts', '*.jsx', '*.js'):
        for f in FRONTEND_DIR.rglob(ext):
            if 'node_modules' in f.parts: continue
            try: txt = f.read_text(errors='ignore')
            except Exception: continue
            files_scanned += 1
            for pat, desc in CRITICAL:
                for m in re.finditer(pat, txt, re.IGNORECASE | re.DOTALL):
                    critical.append({'file': str(f.relative_to('/app')), 'pattern': desc,
                                     'match': m.group(0)[:120],
                                     'line_approx': txt[:m.start()].count('\n') + 1})
    out = {
        'task_origin': 'AF2-N-V29-UI-PUBLIC-PREVIEW-SAFETY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'frontend_files_scanned': files_scanned,
        'critical_findings': critical,
        'critical_count': len(critical),
        'verdict': 'PASS' if not critical else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} files={files_scanned} critical={len(critical)}")
    return 0 if not critical else 2


if __name__ == '__main__':
    sys.exit(main())
