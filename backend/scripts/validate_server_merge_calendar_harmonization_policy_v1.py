#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_calendar_harmonization_policy_v1'
REQUIRED_WINDOWS = {
    '09:00-10:00 Giudizio delle Stirpi', '15:30-16:30 Titanomachia',
    '17:00-18:00 Fronti del Valhalla', 'Mon/Wed/Fri 20:30-21:30 Crepuscolo dei Titani',
    'Tue/Thu/Sat 22:00-23:00 Guerra dei Tre Troni',
}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_calendar_harmonization_policy_v1.json')
    require_design_only(j, errs, NAME)
    r = j.get('rules', {})
    require(r.get('target_calendar_wins') is True, 'target_calendar_wins must be True', errs)
    require(r.get('source_calendars_paused_at_merge_freeze') is True, 'source_calendars_paused_at_merge_freeze must be True', errs)
    require(r.get('no_duplicate_live_windows') is True, 'no_duplicate_live_windows must be True', errs)
    pw = set(j.get('protected_windows', []))
    missing = REQUIRED_WINDOWS - pw
    require(not missing, f'protected_windows missing: {sorted(missing)}', errs)
    mf = j.get('merge_freeze_window', {})
    require(mf.get('forbidden_during_protected_windows') is True, 'freeze forbidden during protected windows', errs)
    require(mf.get('forbidden_within_2_hours_of_protected_windows') is True, 'freeze forbidden within 2h of protected windows', errs)
    af = j.get('af2n_canary_window_check', {})
    require(af.get('forbid_freeze_during_af2n_canary_burst') is True, 'forbid_freeze_during_af2n_canary_burst must be True', errs)
    return finish(NAME, errs, extra={'protected_window_count': len(pw)})


if __name__ == '__main__':
    sys.exit(main())
