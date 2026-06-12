#!/usr/bin/env python3
"""Pack 106 — Controlled reward catalog server-side: no premium, capped."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.controlled_reward_catalog_v1 import (
    MAIL_REWARD_CATALOG_V1, ACHIEVEMENT_REWARD_CATALOG_V1, DAILY_WEEKLY_REWARD_CATALOG_V1,
    ALLOWED_PACK_106_REWARDS, FORBIDDEN_PACK_106_REWARDS,
    get_mail_reward, get_achievement_reward, get_daily_weekly_task, CATALOG_VERSION,
)

assert CATALOG_VERSION.startswith('controlled_reward_catalog_v1')
assert 'gems' in FORBIDDEN_PACK_106_REWARDS
assert 'mission_coins' in ALLOWED_PACK_106_REWARDS
assert 'honor' in ALLOWED_PACK_106_REWARDS
for m in ('steel_ore','magic_dust','ancient_relic','phoenix_feather','crystal_shard'):
    assert m in ALLOWED_PACK_106_REWARDS, f'material missing: {m}'
for f in ('gems','premium_pull','standard_pull','stamina','experience','gold'):
    assert f in FORBIDDEN_PACK_106_REWARDS, f'forbidden missing: {f}'

def _check_reward(label, reward):
    for k, v in reward.get('soft_currencies', {}).items():
        assert k in ALLOWED_PACK_106_REWARDS, f'{label} soft forbidden: {k}'
        assert k not in FORBIDDEN_PACK_106_REWARDS, f'{label} soft forbidden: {k}'
    for k, v in reward.get('materials', {}).items():
        assert k in ALLOWED_PACK_106_REWARDS, f'{label} mat forbidden: {k}'

for mid, m in MAIL_REWARD_CATALOG_V1.items():
    _check_reward(f'mail.{mid}', m['reward'])
for aid, a in ACHIEVEMENT_REWARD_CATALOG_V1.items():
    _check_reward(f'ach.{aid}', a['reward'])
for tid, t in DAILY_WEEKLY_REWARD_CATALOG_V1.items():
    assert t['period'] in ('daily', 'weekly')
    _check_reward(f'task.{tid}', t['reward'])

assert get_mail_reward('welcome_pack_mail') is not None
assert get_mail_reward('nope') is None
assert get_achievement_reward('first_login_achievement') is not None
assert get_daily_weekly_task('weekly_consistency_task')['period'] == 'weekly'

print('[v110 PACK_106_CONTROLLED_REWARD_CATALOG] OK deterministic no_premium soft_and_materials_whitelisted lookups_work')
