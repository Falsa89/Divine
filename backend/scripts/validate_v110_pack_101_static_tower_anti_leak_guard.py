#!/usr/bin/env python3
"""Pack 101 — Static tower anti-leak guard: no users.* mutation in tower files (active code)."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict=open(os.path.join(R,'backend/routes/tower_strict.py')).read()


def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    # Rimuovi anche le response JSON keys che contengono il token (es. "no_users_gold_gems_experience_mutation")
    return s

code = strip_comments_and_docstrings(strict)

# Anti-leak: nessuna mutation su users.* dal codice attivo del tower strict
for forbidden in [
    'db.users.update_one', 'db.users.insert_one', 'db.users.delete_one',
    'db.tower_progress.insert_one', 'db.tower_progress.update_one',
    'db.tower_progress.delete_one',
    '$inc',  # nessun inc da tower_strict (qualsiasi target)
    'reward_claim_ledger', 'grant_fn',
]:
    assert forbidden not in code, f'tower_strict leak: {forbidden}'

# No hardcoded s1
for forbidden in ['server_id="s1"', "server_id='s1'"]:
    assert forbidden not in code, f'tower_strict hardcoded s1: {forbidden}'

# Reward live general / release readiness MUST be False explicitly in response strings
assert '"reward_live_general": False' in strict
assert '"tower_reward_live_grant": False' in strict
assert '"release_readiness_claimed": False' in strict

# Combat legacy: tower_battle/tower_status devono avere il guard prima
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
assert '_pack_101_tower_legacy_block_or_raise()' in combat
assert 'TOWER_LEGACY_QUARANTINED' in combat
print('[v110 PACK_101_STATIC_TOWER_ANTI_LEAK_GUARD] OK no_users_mutation_active_code no_legacy_collection_write no_hardcoded_s1 legacy_quarantined')
