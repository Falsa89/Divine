#!/usr/bin/env python3
"""LIVE-MODES — validate divine_live_mode_benchmark_risk_policy_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'live_mode_benchmark_risk_policy_v1'

REQUIRED_TOKENS = {
    'paid cooldown clear', 'paid morale boost', 'VIP skip', 'paid revive',
    'uncapped extra entries', 'final blow', 'occupation bonuses', 'guild donation',
    'public spend UI', 'STACK-G',
}


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'divine_live_mode_benchmark_risk_policy_v1.json')
    require_design_only_flags(j, errs, NAME)
    items = j.get('forbidden_or_capped_patterns', [])
    joined = ' '.join(items)
    for t in REQUIRED_TOKENS:
        require(t in joined, f'forbidden_or_capped_patterns missing token: {t}', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR, {'forbidden_patterns_count': len(items)})


if __name__ == '__main__':
    sys.exit(main())
