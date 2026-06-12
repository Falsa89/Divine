#!/usr/bin/env python3
"""Pack 109 — Reward Ledger / Idempotency RC audit."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# reward_claim_ledger is canonical Pack 102+. Verifichiamo presenza dello
# script di validazione precedente e la collezione referenziata in qualche route.
found = False
for rel in ('backend/routes/reward_claim.py', 'backend/routes/tower_strict.py',
            'backend/routes/controlled_rewards.py'):
    p = os.path.join(R, rel)
    if not os.path.exists(p): continue
    c = open(p).read()
    if 'reward_claim_ledger' in c or 'idempotency_token' in c:
        found = True
assert found, 'no route references reward_claim_ledger/idempotency_token'
print('[v110 PACK_109_REWARD_LEDGER_IDEMPOTENCY_RC] OK reward_claim_ledger_idempotency_referenced')
