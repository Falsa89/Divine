#!/usr/bin/env python3
"""Pack 109 — Mobile QA Checklist.

Verifica esistenza file `docs/divine/110_CLOSED_ALPHA_MOBILE_QA_CHECKLIST.md`
e contenuto canonico.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
qa = os.path.join(R, 'docs/divine/110_CLOSED_ALPHA_MOBILE_QA_CHECKLIST.md')
assert os.path.exists(qa), 'mobile QA checklist missing'
c = open(qa).read().lower()
for tok in ('home', 'lobby', 'daily', 'tower', 'shop', 'forge', 'rewards', 'guild',
            'arena', 'pvp', 'event', 'server', 'logout', 'safe area', 'permissions',
            'no_silent_s1_fallback', 'reward_live_general=false', 'release_readiness_claimed=false'):
    assert tok in c, f'mobile QA missing token: {tok}'
print('[v110 PACK_109_MOBILE_QA_CHECKLIST] OK mobile_qa_present_with_canonical_tokens')
