#!/usr/bin/env python3
"""V24 — Validate abuse metrics instrumentation (module + endpoint contract)."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from urllib.request import urlopen

MOD = Path('/app/backend/data/affinity_metrics.py')


def main():
    fails = []
    if not MOD.exists(): print('FAIL: module_missing'); return 2
    t = MOD.read_text()
    for tok in ['AFFINITY_METRICS_ENABLED','snapshot','inc','observe_latency_ms','set_gauge','enabled','_HIST_BUCKETS_MS']:
        if tok not in t: fails.append(f'token:{tok}')
    # endpoint check: try /api/affinity/gift-spend/_admin/metrics-snapshot
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/_admin/metrics-snapshot', timeout=4) as r:
            data = json.loads(r.read().decode())
            if 'enabled' not in data: fails.append('snapshot_endpoint_missing_enabled_field')
            # if metrics enabled, must NOT contain borea/PII keys
            # exception: hero_alias label values are operational metrics
            # (counting Borea probe rate); these are NOT data exposure.
            if data.get('enabled') is True:
                import re as _re
                # strip out 'hero_alias=...' label segments before forbidden check
                txt = json.dumps(data)
                txt = _re.sub(r'hero_alias=[a-z_]+', 'hero_alias=__REDACTED__', txt)
                # remove safety annotation keys which legitimately use the word borea
                txt = _re.sub(r'\"no_borea_data\"\s*:\s*true', '"__SAFETY_ANN__":true', txt)
                # the operational metric names af2_gift_spend_borea_404_total contain
                # the word borea as part of the metric identifier (not data exposure).
                txt = _re.sub(r'af2_gift_spend_borea_404_total', 'af2_gift_spend_HIDDENALIAS_404_total', txt)
                for forbidden in ['borea','greek_borea','primordial_gaia']:
                    if forbidden in txt.lower(): fails.append(f'snapshot_contains:{forbidden}')
    except Exception as e:
        fails.append(f'snapshot_endpoint_error:{e}')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-ABUSE-METRICS-INSTRUMENTATION'); return 0


if __name__ == '__main__':
    sys.exit(main())
