#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags  # noqa: E402

NAME = 'benchmark_risk_policy_expanded_v1'
REQUIRED_TOKENS = {
    'paid cooldown clear', 'paid morale boost', 'VIP skip', 'paid revive',
    'uncapped extra entries', 'final blow', 'occupation bonuses', 'guild donation',
    'public spend UI', 'STACK-G', 'hidden odds', 'FOMO', 'alt-account',
    'cross-server data clone', 'borea exposure', 'second server opening',
}


def main() -> int:
    errs = []
    j = load('benchmark_risk_policy_expanded_v1.json')
    check_mandatory_flags(j, errs, NAME)
    joined = ' '.join(j.get('forbidden_or_capped_patterns', []))
    for t in REQUIRED_TOKENS:
        require(t in joined, f'forbidden_or_capped_patterns missing token: {t}', errs)
    inv = j.get('hard_invariants', {})
    require(inv.get('af2n_cap') == 50000, f'hard_invariants.af2n_cap must be 50000 (got {inv.get("af2n_cap")})', errs)
    require(inv.get('af2n_allowlist') == 2500, f'hard_invariants.af2n_allowlist must be 2500 (got {inv.get("af2n_allowlist")})', errs)
    require(inv.get('second_server_opening_allowed') is False, 'second_server_opening_allowed must be False', errs)
    require(inv.get('server_profiles_runtime_enabled') is False, 'server_profiles_runtime_enabled must be False', errs)
    require(inv.get('borea_hidden_from_api_heroes_list') is True, 'borea_hidden_from_api_heroes_list must be True', errs)
    require(inv.get('primordial_gaia_404') is True, 'primordial_gaia_404 must be True', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
