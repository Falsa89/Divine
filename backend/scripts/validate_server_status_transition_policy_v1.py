#!/usr/bin/env python3
"""SLC-E — Validate server_status_transition_policy_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_e_server_status_transition_policy_v1'
EXPECTED = {'planned', 'open', 'crowded', 'closed_to_new', 'merge_pending', 'merged', 'archived'}


def main() -> int:
    errs = []
    j = load_json('server_status_transition_policy_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    statuses = j.get('statuses', [])
    seen = {s.get('status') for s in statuses}
    require(seen == EXPECTED, f'status set mismatch; expected={EXPECTED} got={seen}', errs)
    by = {s.get('status'): s for s in statuses}
    require(by['planned']['selectable'] is False, 'planned must not be selectable', errs)
    require(by['planned']['new_profile_allowed'] is False, 'planned must not allow new profiles', errs)
    require(by['open']['selectable'] is True, 'open must be selectable', errs)
    require(by['open']['new_profile_allowed'] is True, 'open must allow new profiles', errs)
    require(by['crowded']['new_profile_allowed'] == 'only_below_hard_cap', 'crowded must only allow new profiles below hard cap', errs)
    require(by['closed_to_new']['new_profile_allowed'] is False, 'closed_to_new must NOT allow new profiles', errs)
    require(by['closed_to_new']['existing_profile_allowed'] is True, 'closed_to_new must allow existing profiles', errs)
    require(by['merge_pending']['new_profile_allowed'] is False, 'merge_pending must NOT allow new profiles', errs)
    require(by['merged']['existing_profile_allowed'] == 'redirect_to_target', 'merged must redirect existing to target', errs)
    require(by['archived']['selectable'] is False, 'archived must not be selectable', errs)
    require(by['archived']['new_profile_allowed'] is False, 'archived must not allow new profiles', errs)
    require(by['archived']['existing_profile_allowed'] is False, 'archived must not allow existing profiles', errs)
    require(j.get('safety', {}).get('second_server_opening_allowed') is False, 'safety.second_server_opening_allowed must be False', errs)
    return finish(NAME, errs, {'status_count': len(statuses)})


if __name__ == '__main__':
    sys.exit(main())
