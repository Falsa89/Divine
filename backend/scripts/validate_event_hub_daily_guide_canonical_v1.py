#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'event_hub_daily_guide_canonical_v1'


def main() -> int:
    errs = []
    j = load('event_hub_daily_guide_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    eh = j.get('event_hub', {})
    check_canonical_fields(eh, NAME + '.event_hub', errs)
    require(any('Single Event Hub' in s for s in eh.get('how_works_in_divine', [])), 'event_hub must declare “Single Event Hub”', errs)
    require(any('max 3 visible announcements' in s for s in eh.get('how_works_in_divine', [])), 'event_hub must reference broadcast cap (3)', errs)
    dg = j.get('daily_guide', {})
    check_canonical_fields(dg, NAME + '.daily_guide', errs, optional_inspiration=True)
    require(any('Borea' in s for s in dg.get('how_works_in_divine', [])), 'daily_guide must explicitly mention Borea NOT shown as starter', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
