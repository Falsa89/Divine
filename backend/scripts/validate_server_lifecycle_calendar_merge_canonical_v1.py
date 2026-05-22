#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'server_lifecycle_calendar_merge_canonical_v1'
EXPECTED_STATUSES = {'planned', 'open', 'crowded', 'closed_to_new', 'merge_pending', 'merged', 'archived'}


def main() -> int:
    errs = []
    j = load('server_lifecycle_calendar_merge_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    sl = j.get('server_lifecycle', {})
    check_canonical_fields(sl, NAME + '.server_lifecycle', errs)
    require(set(sl.get('statuses', [])) == EXPECTED_STATUSES, f'statuses must match {sorted(EXPECTED_STATUSES)}', errs)
    cal = j.get('server_calendar', {})
    require(len(cal.get('daily_windows', [])) == 6, f'daily_windows must be 6 (got {len(cal.get("daily_windows", []))})', errs)
    require(len(cal.get('weekly_windows', [])) == 2, f'weekly_windows must be 2 (got {len(cal.get("weekly_windows", []))})', errs)
    mr = j.get('merge_recovery', {})
    check_canonical_fields(mr, NAME + '.merge_recovery', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
