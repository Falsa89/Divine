#!/usr/bin/env python3
"""Pack 104 — Static economy anti-leak guard."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()

def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(strict)

# Anti-leak invariant: NESSUNA mutation users.* / wallets / user_materials / user_fragments
for forbidden in [
    'db.users.update_one','db.users.insert_one','db.users.delete_one',
    'db.users.update_many','db.users.delete_many',
    'db.wallets.update_one','db.wallets.update_many','db.wallets.insert_one',
    'db.user_materials.update_one','db.user_materials.update_many','db.user_materials.insert_one',
    'db.user_fragments.update_one','db.user_fragments.update_many','db.user_fragments.insert_one',
]:
    assert forbidden not in code, f'economy_strict leak: {forbidden}'

# No hardcoded s1
for forbidden in ['server_id="s1"', "server_id='s1'"]:
    assert forbidden not in code, f'economy_strict hardcoded s1: {forbidden}'

# Ogni $inc deve essere ristretto a soft_currencies.* (PSP) o $unset/$set su user_equipment/user_heroes server-scoped
inc_occurrences = [m.start() for m in re.finditer(r'\$inc', code)]
for pos in inc_occurrences:
    window = code[max(0, pos-300):pos+500]
    assert 'soft_currencies' in window or 'player_server_profiles' in window, \
        f'$inc occurrence at offset {pos} non e\' ristretto a PSP'

# Reward live general / release readiness MUST be False explicitly in response bodies.
assert '"reward_live_general": False' in strict
assert '"release_readiness_claimed": False' in strict
assert '"premium_grants": False' in strict
assert '"no_iap_gacha_payment": True' in strict

# Client price/reward MUST never appear in active code (no payload['price']/cost/grant).
for forbidden_field in ("req.price","req['price']","req.cost","req.grant"):
    assert forbidden_field not in code, f'client price/reward trust: {forbidden_field}'

# Triple kill switch present
for ks in ('REWARD_CLAIM_LEDGER_LIVE_ENABLED','ECONOMY_STRICT_WRITES_ENABLED','SHOP_BUY_STRICT_ENABLED','SOUL_FORGE_RETIRE_STRICT_ENABLED','EQUIPMENT_STRICT_WRITES_ENABLED'):
    assert ks in code, f'kill switch missing: {ks}'

# Server-scoped writes: user_heroes/user_equipment filtering MUST always include server_id
# (regex con re.S per accettare multiline call args).
for pat in [
    r"db\.user_heroes\.find_one\(\s*\{[^}]*server_id",
    r"db\.user_heroes\.delete_one\(\s*\{[^}]*server_id",
    r"db\.user_equipment\.find_one\(\s*\{[^}]*server_id",
    r"db\.user_equipment\.update_one\(\s*\{[^}]*server_id",
    r"db\.user_equipment\.update_many\(\s*\{[^}]*server_id",
]:
    assert re.search(pat, code, re.S), f'server_id filter missing: {pat}'

print('[v110 PACK_104_STATIC_ANTI_LEAK] OK no_users_wallets_materials_mutation no_hardcoded_s1 inc_restricted_PSP no_client_price_trust triple_kill_switch_present server_scoped_filtering_enforced')
