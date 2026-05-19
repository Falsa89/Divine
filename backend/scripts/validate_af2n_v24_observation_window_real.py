#!/usr/bin/env python3
"""V24 — Validate observation window real."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v24_observation_window_real_result.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') != 'PASS':
        for f in d.get('fails', []): print(f'FAIL: {f}')
        return 2
    if not d.get('backend_stable'): print('FAIL: backend_not_stable'); return 2
    print('PASS: AF2-N-V24-OBSERVATION-WINDOW-REAL'); return 0


if __name__ == '__main__':
    sys.exit(main())
