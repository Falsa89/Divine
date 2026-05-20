#!/usr/bin/env python3
"""V26 PART G — Frontend smoke read-only."""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/ui/affinity_gifts_frontend_smoke_v26_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

PREVIEW_FILE = Path('/app/frontend/app/affinity-gifts-preview.tsx')
BASE_FRONTEND = 'http://127.0.0.1:3000'
BASE_BACKEND = 'http://127.0.0.1:8001'

FORBIDDEN_INTERACT = [
    (r"method\s*:\s*['\"](POST|PUT|PATCH|DELETE)['\"][^}]*\bgift-spend\b(?!/canary-status)",
     'mutating fetch on gift-spend'),
    (r"hero_id\s*:\s*['\"]borea['\"]", 'hero_id=borea'),
    (r"hero_id\s*:\s*['\"]greek_borea['\"]", 'hero_id=greek_borea'),
    (r"hero_id\s*:\s*['\"]primordial_gaia['\"]", 'hero_id=primordial_gaia'),
    (r"onPress\s*=\s*\{[^}]*\b(?:gift[_\-]?spend|affinity[_\-]?gift|gift_give)\b",
     'onPress invoking affinity gift mutation'),
]

A11Y_HINTS = ['accessibilityLabel', 'accessibilityRole', 'accessibilityHint',
              'aria-label', 'accessible']


def _http(url, timeout=4):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode(errors='ignore')[:5000]
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return -1, str(e)[:200]


def main():
    started = datetime.now(timezone.utc).isoformat()
    out = {
        'task_origin': 'AF2-N-V26-FRONTEND-SMOKE',
        'timestamp_utc': started,
        'mode': 'READ_ONLY',
        'file_present': PREVIEW_FILE.exists(),
        'http_checks': {},
        'static_checks': {},
        'a11y_check': {},
    }

    # 1) HTTP checks
    fe_code, _ = _http(BASE_FRONTEND + '/affinity-gifts-preview')
    cs_code, _ = _http(BASE_BACKEND + '/api/affinity/gift-spend/canary-status')
    out['http_checks'] = {
        'frontend_preview_route': fe_code,
        'backend_canary_status': cs_code,
        'frontend_reachable': fe_code in (200, 304),
        'backend_canary_ok': cs_code == 200,
    }

    # 2) Static checks on preview file
    if PREVIEW_FILE.exists():
        txt = PREVIEW_FILE.read_text(errors='ignore')
        critical = []
        for pat, desc in FORBIDDEN_INTERACT:
            for m in re.finditer(pat, txt, re.IGNORECASE | re.DOTALL):
                critical.append({'pattern': desc, 'match': m.group(0)[:100]})
        out['static_checks'] = {
            'critical_findings': critical,
            'critical_count': len(critical),
            'fetch_method_get_only': bool(re.search(r"method\s*:\s*['\"]GET['\"]", txt)),
            'mentions_borea_id': bool(re.search(r"hero_id.*['\"]borea", txt)),
            'file_size_bytes': len(txt),
        }
        # A11y label coverage
        a11y_hits = sum(txt.lower().count(h.lower()) for h in A11Y_HINTS)
        out['a11y_check'] = {
            'a11y_hits': a11y_hits,
            'a11y_present': a11y_hits > 0,
        }

    # 3) Verdict
    out['verdict'] = 'PASS' if all([
        out['file_present'],
        out['http_checks']['frontend_reachable'],
        out['http_checks']['backend_canary_ok'],
        out['static_checks'].get('critical_count', 1) == 0,
        not out['static_checks'].get('mentions_borea_id', True),
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} fe={fe_code} backend_cs={cs_code} critical={out['static_checks'].get('critical_count')} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
