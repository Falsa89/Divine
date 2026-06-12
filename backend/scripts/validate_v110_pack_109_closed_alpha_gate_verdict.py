#!/usr/bin/env python3
"""Pack 109 — Closed Alpha Gate Verdict.

Verifica che il report dichiari un verdict canonico ammesso.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
report = open(os.path.join(R, 'docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md')).read()
ALLOWED = ('CLOSED_ALPHA_READY', 'CLOSED_ALPHA_CONDITIONAL_READY', 'CLOSED_ALPHA_NOT_READY')
found = [v for v in ALLOWED if v in report]
assert found, f'no canonical verdict in report; allowed: {ALLOWED}'
# Verdict canonico atteso: CONDITIONAL_READY (deferred systems documentati).
assert 'CLOSED_ALPHA_CONDITIONAL_READY' in report or 'CLOSED_ALPHA_READY' in report
# Verifica explicit non-claims richiesti.
rep_low = report.lower()
assert 'public_launch_ready=false' in rep_low or 'public_launch_ready: false' in rep_low
assert 'production_release_ready=false' in rep_low or 'production_release_ready: false' in rep_low
assert 'reward_live_general=false' in rep_low or 'reward_live_general: false' in rep_low
print(f'[v110 PACK_109_CLOSED_ALPHA_GATE_VERDICT] OK verdict_in_report=' + ','.join(found))
