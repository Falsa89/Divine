#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'sanctuary_housing_dimora_divina_canonical_v1'
REQUIRED_TOKENS_IN_HOW = {
    'Housing inside Sanctuary', 'Equipped state and bonuses server-bound',
    'Paid furniture ownership may be account-wide', 'PvP caps stricter than PvE',
    'cosmetic/global cap resolver',
}


def main() -> int:
    errs = []
    j = load('sanctuary_housing_dimora_divina_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    check_canonical_fields(j, NAME, errs, optional_inspiration=False)
    require(j.get('name') == 'Santuario \u2014 Dimora Divina', f'name must be “Santuario — Dimora Divina” (got {j.get("name")})', errs)
    joined = ' '.join(j.get('how_works_in_divine', []))
    for t in REQUIRED_TOKENS_IN_HOW:
        require(t in joined, f'how_works_in_divine missing token: {t}', errs)
    require(j.get('runtime_status') == 'not_implemented', f'runtime_status must be not_implemented (got {j.get("runtime_status")})', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
