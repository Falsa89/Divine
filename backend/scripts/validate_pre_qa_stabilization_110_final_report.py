#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Final report validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rep = os.path.join(R, 'docs/divine/112_PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_FINAL_REPORT.md')
assert os.path.exists(rep)
c = open(rep).read().lower()
for t in ('verdict', 'gacha quarantine proof', 'team formation', 'useserverscope',
          'auth token compatibility', 'menu cleanup', 'achievements legacy quarantine',
          'mutating route allowlist', 'runtime smoke', 'static anti-leak',
          'data invariants', 'pack 91-109', 'qa kickoff preservation',
          'reward_live_general=false', 'release_readiness_claimed=false',
          'public_launch_ready=false', 'production_release_ready=false',
          'next step'):
    assert t in c, f'final report missing: {t}'
print('[v110 PRE_QA_110_FINAL_REPORT_VALIDATOR] OK final_report_canonical_sections_present')
