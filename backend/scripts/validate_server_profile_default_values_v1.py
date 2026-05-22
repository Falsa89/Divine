#!/usr/bin/env python3
"""SLC-B — Validate server_profile_default_values_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_b_server_profile_default_values_v1'


def main() -> int:
    errs = []
    j = load_json('server_profile_default_values_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('runtime_attached') is False, 'runtime_attached must be False', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    d = j.get('defaults', {})
    require(d.get('level_on_server') == 1, 'level_on_server default must be 1', errs)
    require(d.get('tutorial_state', {}).get('completed') is False, 'tutorial.completed default must be False', errs)
    require(d.get('progression_state', {}).get('story_chapter') == 1, 'story_chapter default must be 1', errs)
    sb = d.get('server_bound_free_currencies', {})
    require(sb.get('gold') == 0 and sb.get('diamonds_free') == 0, 'free currencies must default to 0', errs)
    fi = j.get('forbidden_inheritance', {})
    for k in ('no_inherited_roster', 'no_inherited_inventory', 'no_inherited_free_currency',
              'no_inherited_progression', 'no_inherited_guild', 'no_inherited_arena_rank'):
        require(fi.get(k) is True, f'forbidden_inheritance.{k} must be True', errs)
    aw = j.get('account_wide_views_visible_per_server', {})
    require('paid_currency_balance_view' in aw, 'paid_currency_balance_view must be present', errs)
    bs = j.get('borea_safety', {})
    require(bs.get('borea_never_exposed_as_starter_hero') is True, 'borea_never_exposed_as_starter_hero', errs)
    require(bs.get('borea_never_appears_in_starter_roster_results') is True, 'borea_never_appears_in_starter_roster_results', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
