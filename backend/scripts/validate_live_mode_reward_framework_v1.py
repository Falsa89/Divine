#!/usr/bin/env python3
"""LIVE-MODES — validate divine_live_mode_reward_framework_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'live_mode_reward_framework_v1'

REQUIRED_CATEGORIES = {
    'participation_reward', 'personal_performance_reward', 'guild_result_reward',
    'server_or_faction_collective_reward', 'leaderboard_reward', 'consolation_reward',
    'milestone_reward', 'shop_currency', 'first_clear_reward', 'recurring_reward',
}
REQUIRED_ANTI_P2W_TOKENS = {
    'paid cooldown clear', 'paid morale boost', 'VIP skip', 'paid revive',
    'uncapped extra entries', 'final blow',
}


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'divine_live_mode_reward_framework_v1.json')
    require_design_only_flags(j, errs, NAME)
    cats = set(j.get('reward_categories', []))
    missing = REQUIRED_CATEGORIES - cats
    require(not missing, f'reward_categories missing: {sorted(missing)}', errs)
    anti = ' '.join(j.get('anti_p2w', []))
    for tok in REQUIRED_ANTI_P2W_TOKENS:
        require(tok in anti, f'anti_p2w missing token: {tok}', errs)
    require(isinstance(j.get('rule'), str) and 'each mode' in j.get('rule', ''), 'rule must explain per-mode reward category selection', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR, {'reward_categories_count': len(cats)})


if __name__ == '__main__':
    sys.exit(main())
