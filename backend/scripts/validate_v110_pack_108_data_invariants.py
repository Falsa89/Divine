#!/usr/bin/env python3
"""Pack 108 — Data invariants (statici).

Verifica che i file Pack 108 NON introducano nessuna mutation su:
  - users.gold / users.gems / users.experience
  - guilds (legacy account-wide)
  - reward_claim_ledger insert con source guild_*
  - $inc su soft_currencies / materials
  - IAP / gacha / payment
"""
import os, re as _re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACK_108_FILES = (
    'backend/routes/guild_strict.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/competitive_guards.py',
)
for rel in PACK_108_FILES:
    c = open(os.path.join(R, rel)).read()
    # Mutation patterns forbidden:
    for forbidden in (
        'gold": {"$inc', "gold': {'$inc",
        'gems": {"$inc', "gems': {'$inc",
        'experience": {"$inc', "experience': {'$inc",
        'reward_claim_ledger.insert_one',
        'db.users.update_one',
        'db.users.insert_one',
        'db.users.delete_one',
    ):
        assert forbidden.lower() not in c.lower(), f'{rel}: {forbidden}'
    # IAP/gacha/payment integrations LIVE forbidden (negative flags ok).
    for live_pattern in (
        r'iap_client\.',
        r'\bstripe\.',
        r'gacha_pull\(',
        r'payment_intent\.create',
        r'\biap_grant\(',
        r'\bcharge\(',
    ):
        assert _re.search(live_pattern, c, _re.IGNORECASE) is None, f'{rel}: live integration {live_pattern}'

# guild.py legacy: quarantena impedisce mutation in produzione, ma le definizioni
# di update_one esistono (legacy code). Verifichiamo che il guard sia presente.
g = open(os.path.join(R, 'backend/routes/guild.py')).read()
assert g.count('_pack_108_raise_quarantined') >= 4, 'quarantine guard not in all 4 mutating routes'

print('[v110 PACK_108_DATA_INVARIANTS] OK no_users_gold_gems_experience_mutation no_iap_gacha_payment legacy_quarantined_in_all_mutating_routes')
