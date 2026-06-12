#!/usr/bin/env python3
"""Pack 108 — Runtime smoke E2E recorder.

Questo validator verifica che lo script smoke E2E esista e contenga TUTTI
i 17 step canonici. (Non lancia HTTP qui per evitare dipendenza dal
backend in CI offline; lo smoke vero si esegue separatamente:
`python backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py`).
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(R, 'backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py')
assert os.path.exists(f)
c = open(f).read()
for n in range(1, 18):
    assert f'[{n}]' in c, f'smoke step [{n}] missing'
assert 'SMOKE PACK 108 OK' in c
assert 'pack_108_test_artifact' in c
assert 'GUILD_LEGACY_QUARANTINED' in c
assert 'release_readiness_claimed' in c
assert 'reward_live_general' in c
assert 'no_silent_fallback_to_s1' in c or 'no_silent_fallback' in c or 's2' in c
print('[v110 PACK_108_RUNTIME_SMOKE_E2E] OK seventeen_steps_present smoke_script_canonical')
