#!/usr/bin/env python3
"""LIVE-MODES — validate divine_live_mode_broadcast_policy_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'live_mode_broadcast_policy_v1'


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'divine_live_mode_broadcast_policy_v1.json')
    require_design_only_flags(j, errs, NAME)
    require(j.get('max_visible_announcements') == 3, f'max_visible_announcements must be 3 (got {j.get("max_visible_announcements")})', errs)
    require(isinstance(j.get('significant_events_only'), list) and len(j['significant_events_only']) >= 5, 'significant_events_only must be a non-trivial list', errs)
    require(isinstance(j.get('spam_prevention'), list) and j['spam_prevention'], 'spam_prevention required', errs)
    require('priority_queue' in (j.get('queue') or '').lower() or 'queue' in (j.get('queue') or '').lower(), 'queue must be a queue policy', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR)


if __name__ == '__main__':
    sys.exit(main())
