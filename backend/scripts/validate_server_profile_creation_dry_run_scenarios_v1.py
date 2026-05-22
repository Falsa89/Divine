#!/usr/bin/env python3
"""SLC-BE — Validate server_profile_creation_dry_run_scenarios_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import load_json, finish, require  # noqa: E402

NAME = 'slc_be_dry_run_scenarios_v1'
REQUIRED_NAMES = {
    'legacy_account_s1_existing_profile_loads_no_creation',
    'new_account_routed_to_s2_open',
    'new_account_target_closed_to_new_no_profile_rejected',
    'existing_account_target_closed_to_new_with_profile_loads',
    'new_account_auto_routed_to_newest_open_server',
    'newest_is_crowded_falls_back_to_newest_open_not_crowded',
    'merged_server_redirects_to_target',
    'archived_server_rejected',
    'paid_currency_visible_account_wide_view_per_server',
    'free_currency_starts_at_server_default_zero',
    'paid_cosmetic_owned_but_not_equippable_until_hero_exists_on_server',
    'borea_hidden_from_starter_flow_forbidden_in_starter_roster',
}


def main() -> int:
    errs = []
    j = load_json('server_profile_creation_dry_run_scenarios_v1.json')
    require(j.get('design_only') is True, 'design_only must be True', errs)
    require(j.get('db_write') is False, 'db_write must be False', errs)
    scenarios = j.get('scenarios', [])
    require(len(scenarios) >= 12, f'expected >=12 scenarios (got {len(scenarios)})', errs)
    names = {s.get('name') for s in scenarios}
    missing = REQUIRED_NAMES - names
    require(not missing, f'missing required scenarios: {sorted(missing)}', errs)
    ids = [s.get('id') for s in scenarios]
    require(len(set(ids)) == len(ids), 'duplicate scenario ids', errs)
    # Each scenario must have inputs + expected blocks with creates_profile=False on rejections
    for s in scenarios:
        nm = s.get('name', '?')
        require('inputs' in s, f'{nm}: missing inputs', errs)
        require('expected' in s, f'{nm}: missing expected', errs)
        exp = s.get('expected', {})
        if exp.get('action') == 'reject':
            require(exp.get('creates_profile') is False, f'{nm}: reject action must NOT create profile', errs)
    # Borea scenario must explicitly exclude Borea from starter roster
    sb = next((s for s in scenarios if s.get('name') == 'borea_hidden_from_starter_flow_forbidden_in_starter_roster'), None)
    require(sb is not None, 'borea-safety scenario missing', errs)
    if sb:
        exp = sb.get('expected', {})
        require(exp.get('starter_roster_includes_borea') is False, 'borea must not be in starter roster', errs)
        require(exp.get('starter_roster_includes_greek_borea') is False, 'greek_borea must not be in starter roster', errs)
        require(exp.get('starter_roster_includes_primordial_gaia') is False, 'primordial_gaia must not be in starter roster', errs)
    # safety flags
    require(j.get('safety', {}).get('no_db_write') is True, 'safety.no_db_write must be True', errs)
    require(j.get('safety', {}).get('second_server_opening_allowed') is False, 'safety.second_server_opening_allowed must be False', errs)
    return finish(NAME, errs, {'scenario_count': len(scenarios)})


if __name__ == '__main__':
    sys.exit(main())
