#!/usr/bin/env python3
"""LIVE-MODES — validate sanctuary_housing_dimora_divina_design_note_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'sanctuary_housing_dimora_divina_note_v1'

REQUIRED_BONUS_RULES = {
    'cosmetic/global cap resolver', 'PvP caps stricter than PvE',
    'no infinite stacking', 'paid furniture ownership may be account-wide',
    'equipped state and bonuses server-bound',
}


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'sanctuary_housing_dimora_divina_design_note_v1.json')
    require_design_only_flags(j, errs, NAME)
    require(j.get('name') == 'Santuario — Dimora Divina', f'name must be “Santuario — Dimora Divina” (got {j.get("name")})', errs)
    require(isinstance(j.get('features'), list) and j['features'], 'features required', errs)
    rules = j.get('bonus_rules', [])
    joined = ' '.join(rules)
    for tok in REQUIRED_BONUS_RULES:
        require(tok in joined, f'bonus_rules missing token: {tok}', errs)
    # No runtime fields
    forbidden_runtime_keys = {'runtime', 'route_implementation', 'db_collection', 'mongo_path', 'feature_flag_value'}
    intruders = forbidden_runtime_keys & set(j.keys())
    require(not intruders, f'sanctuary housing must be design-only; runtime keys found: {intruders}', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR)


if __name__ == '__main__':
    sys.exit(main())
