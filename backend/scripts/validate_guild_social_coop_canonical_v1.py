#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'guild_social_coop_canonical_v1'
REQUIRED_TOKENS = {'server-bound', 'activity points', 'Scrigni dell\u2019Elisio', 'Roles'}


def main() -> int:
    errs = []
    j = load('guild_social_coop_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    check_canonical_fields(j, NAME, errs)
    joined = ' '.join(j.get('how_works_in_divine', [])).lower()
    for t in REQUIRED_TOKENS:
        require(t.lower() in joined, f'how_works_in_divine missing token: {t}', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
