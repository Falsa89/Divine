#!/usr/bin/env python3
"""PROJECT_J REQUIRED-candidate 2 — first slice does NOT touch tick loop."""
import sys
from pathlib import Path
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
FORBIDDEN_PATTERNS = ('tick(', 'on_tick', 'apply_tick', 'tick_loop', 'process_tick')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    src = R.read_text()
    for pat in FORBIDDEN_PATTERNS:
        if pat in src: fail(f'resolver references tick loop pattern: {pat}')
    print('[PASS] resolver does NOT touch tick loop'); sys.exit(0)
if __name__ == '__main__': main()
