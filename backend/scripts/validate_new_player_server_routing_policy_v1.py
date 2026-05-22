#!/usr/bin/env python3
"""SLC-E — Validate new_player_server_routing_policy_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_e_new_player_server_routing_policy_v1'


def main() -> int:
    errs = []
    j = load_json('new_player_server_routing_policy_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    r = j.get('rules', {})
    require(r.get('default_for_new_account') == 'newest_open_server', 'default_for_new_account must be newest_open_server', errs)
    require(r.get('if_newest_is_crowded') == 'choose_newest_open_not_crowded', 'crowded fallback rule mismatch', errs)
    require(r.get('existing_player_default') == 'return_to_last_active_server', 'existing player must return to last active server', errs)
    require(r.get('no_auto_migration_old_to_new') is True, 'no_auto_migration_old_to_new must be True', errs)
    require(r.get('no_cross_server_resource_copy') is True, 'no_cross_server_resource_copy must be True', errs)
    require(r.get('legacy_player_default_in_future_migration') == 's1', 'legacy player default must be s1', errs)
    pri = j.get('selection_priority', [])
    require(len(pri) >= 4, f'selection_priority must have >=4 entries (got {len(pri)})', errs)
    require(pri[0] == 'existing_active_server_profile', 'first priority must be existing_active_server_profile', errs)
    forb = j.get('forbidden', {})
    for k in ('never_copy_inventory_across_servers', 'never_copy_roster_across_servers',
              'never_copy_free_currency_across_servers', 'never_auto_route_existing_players_to_new_server',
              'never_expose_borea_in_starter_routing'):
        require(forb.get(k) is True, f'forbidden.{k} must be True', errs)
    cw = j.get('compatibility_window', {})
    require(cw.get('single_shard_runtime') is True, 'compatibility_window.single_shard_runtime must be True', errs)
    require(cw.get('second_server_opening_allowed') is False, 'compatibility_window.second_server_opening_allowed must be False', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
