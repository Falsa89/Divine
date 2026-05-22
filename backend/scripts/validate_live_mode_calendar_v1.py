#!/usr/bin/env python3
"""LIVE-MODES — validate divine_live_mode_calendar_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'live_mode_calendar_v1'

EXPECTED_WINDOWS = [
    ('09:00-10:00', 'Giudizio delle Stirpi', 'daily'),
    ('11:00-12:00', 'Assalto del Ragnarök', 'daily'),
    ('14:00-15:00', 'Giudizio delle Stirpi', 'daily'),
    ('15:30-16:30', 'Titanomachia', 'daily'),
    ('17:00-18:00', 'Fronti del Valhalla', 'daily'),
    ('19:00-20:00', 'Assalto del Ragnarök', 'daily'),
    ('20:30-21:30', 'Crepuscolo dei Titani', 'mon_wed_fri'),
    ('22:00-23:00', 'Guerra dei Tre Troni', 'tue_thu_sat'),
]


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'divine_live_mode_calendar_v1.json')
    require_design_only_flags(j, errs, NAME)
    cal = j.get('calendar', [])
    require(len(cal) == 8, f'calendar must have exactly 8 windows (got {len(cal)})', errs)
    times_seen = [c.get('time') for c in cal]
    require(times_seen == [w[0] for w in EXPECTED_WINDOWS], f'calendar times mismatch; got {times_seen}', errs)
    for i, (t, mode, freq) in enumerate(EXPECTED_WINDOWS):
        if i < len(cal):
            c = cal[i]
            require(c.get('mode') == mode, f'window {t}: mode mismatch “{c.get("mode")}” != “{mode}”', errs)
            require(c.get('frequency') == freq, f'window {t}: frequency “{c.get("frequency")}” != “{freq}”', errs)
    # Guerra dei Tre Troni must include prep_days mon_wed_fri
    war3 = next((c for c in cal if c.get('mode') == 'Guerra dei Tre Troni'), None)
    if war3:
        require(war3.get('prep_days') == 'mon_wed_fri', f'Guerra dei Tre Troni: prep_days must be mon_wed_fri (got {war3.get("prep_days")})', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR, {'window_count': len(cal)})


if __name__ == '__main__':
    sys.exit(main())
