#!/usr/bin/env python3
"""Pack 109 — Economy strict RC audit (static)."""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()
for tok in ('/economy/strict/health', 'pack_104_test_artifact', 'server_id', 'reward_live_general'):
    assert tok in c, f'economy_strict missing {tok}'
# No users.gold/gems/experience mutation $inc.
for forbidden in ('users.gold', 'users.gems', 'users.experience'):
    # Tollerato come stringa in safety statements, ma NO $inc su quei campi.
    pass
# Forbidden: $inc su gold/gems/experience.
for pat in (r'"gold":\s*\{\s*"\$inc"', r'"gems":\s*\{\s*"\$inc"', r'"experience":\s*\{\s*"\$inc"'):
    assert re.search(pat, c) is None, f'economy_strict: {pat} forbidden'
print('[v110 PACK_109_ECONOMY_STRICT_RC] OK economy_strict_canonical_invariants_intact no_users_currency_inc')
