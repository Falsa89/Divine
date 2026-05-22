#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'summon_pity_fragment_canonical_v1'
REQUIRED_TOKENS = {'pity', 'fragments', 'Wishlist', 'soft pity', 'hard pity', 'banner_id'}


def main() -> int:
    errs = []
    j = load('summon_pity_fragment_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    check_canonical_fields(j, NAME, errs)
    joined = ' '.join(j.get('how_works_in_divine', []))
    for t in REQUIRED_TOKENS:
        require(t.lower() in joined.lower(), f'how_works_in_divine missing token: {t}', errs)
    b = j.get('baseline_today', {})
    require('current_pity_scope' in b and 'future_pity_scope' in b, 'baseline_today must include current and future pity scope', errs)
    require('user_id' in b.get('current_pity_scope', ''), 'current_pity_scope must reference user_id (single-shard)', errs)
    require('account_id' in b.get('future_pity_scope', '') and 'server_id' in b.get('future_pity_scope', ''), 'future_pity_scope must reference account_id+server_id', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
