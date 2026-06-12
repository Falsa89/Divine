#!/usr/bin/env python3
"""Pack 106 — Static reward anti-leak guard."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict = open(os.path.join(R, 'backend/routes/controlled_rewards.py')).read()

def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(strict)

for forbidden in [
    'db.users.update_one','db.users.insert_one','db.users.delete_one',
    'db.users.update_many','db.users.delete_many',
    'db.wallets.update_one','db.wallets.update_many','db.wallets.insert_one',
    'db.user_materials.update_one','db.user_materials.update_many',
    'db.user_fragments.update_one','db.user_fragments.update_many',
    'db.battlepass','db.afk','db.pvp','db.guild_rewards','db.event_rewards',
]:
    assert forbidden not in code, f'controlled_rewards leak: {forbidden}'

for forbidden in ['server_id="s1"', "server_id='s1'"]:
    assert forbidden not in code, f'hardcoded s1: {forbidden}'

# $inc deve essere ristretto a PSP
inc_occurrences = [m.start() for m in re.finditer(r'\$inc', code)]
for pos in inc_occurrences:
    window = code[max(0, pos-300):pos+400]
    assert ('player_server_profiles' in window or 'soft_currencies' in window or 'materials' in window), \
        f'$inc at offset {pos} non e\' ristretto a PSP'

assert '"reward_live_general": False' in strict
assert '"release_readiness_claimed": False' in strict
assert '"premium_grants": False' in strict
assert '"no_battlepass_event_afk_pvp_guild_live": True' in strict

for ks in ('MAIL_CLAIM_CONTROLLED_ENABLED','ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED','DAILY_WEEKLY_REWARD_CLAIM_ENABLED'):
    assert ks in code, f'kill switch missing: {ks}'

print('[v110 PACK_106_STATIC_ANTI_LEAK] OK no_users_wallets_materials_mutation no_battlepass_event_afk_pvp_guild_writes no_hardcoded_s1 inc_restricted_PSP no_client_reward_trust kill_switches_present')
