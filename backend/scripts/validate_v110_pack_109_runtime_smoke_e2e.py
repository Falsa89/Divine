#!/usr/bin/env python3
"""Pack 109 — Runtime Smoke E2E Recorder.

Verifica che lo smoke script contenga 15 step canonici.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py')).read()
for n in range(1, 16):
    assert f'[{n}]' in c, f'smoke step [{n}] missing'
assert 'SMOKE PACK 109 CLOSED ALPHA RC OK' in c
print('[v110 PACK_109_RUNTIME_SMOKE_E2E] OK fifteen_steps_present')
