#!/usr/bin/env python3
"""V23 — Validate observation window."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage4_observation_window_v23_result.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') != 'PASS':
        for f in d.get('fails', []): print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V23-STAGE4-OBSERVATION-WINDOW'); return 0


if __name__ == '__main__':
    sys.exit(main())
