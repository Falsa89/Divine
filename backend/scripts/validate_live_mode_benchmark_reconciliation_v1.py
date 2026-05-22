#!/usr/bin/env python3
"""LIVE-MODES — validate divine_live_mode_benchmark_reconciliation_v1.json."""
from __future__ import annotations
import sys
sys.path.insert(0, '/app/backend/scripts')
from _live_modes_common import LIVE_MODES_DIR, load_json_at, require, require_design_only_flags, finish_result  # noqa: E402

NAME = 'live_mode_benchmark_reconciliation_v1'

EXPECTED_MAPPING = {
    1:  ('Giudizio di Asgard',          'not_present'),
    2:  ('Cammino dell’Ade',            'Hueco Mundo Attack'),
    3:  ('Scala dell’Olimpo',           'not_present'),
    4:  ('Sigilli degli Dei',           'not_present'),
    5:  ('Torre degli Inferi',          'not_bleach_online_but_Bleach_Brave_Souls_Senkaimon'),
    6:  ('Troni dell’Eclissi',          'not_present'),
    7:  ('Prove del Pantheon',          'not_present'),
    8:  ('Abisso del Colosso',          'not_present'),
    9:  ('Crepuscolo dei Titani',       'Void Region'),
    10: ('Giudizio delle Stirpi',       'Evil Spirit'),
    11: ('Fronti del Valhalla',         'Guild War'),
    12: ('Guerra dei Tre Troni',        'not_bleach'),
    13: ('Fame del Behemoth',           'not_present'),
    14: ('Furie del Pantheon',          'not_present'),
    15: ('Titanomachia',                'Protect Seireitei'),
    16: ('Assalto del Ragnarök',        'Ryoka Attack'),
}

REQUIRED_CORRECTIONS = {'Troni dell’Eclissi', 'Titanomachia', 'Giudizio di Asgard'}


def main() -> int:
    errs = []
    j = load_json_at(LIVE_MODES_DIR / 'divine_live_mode_benchmark_reconciliation_v1.json')
    require_design_only_flags(j, errs, NAME)
    modes = j.get('modes', [])
    require(len(modes) == 16, f'must have exactly 16 modes (got {len(modes)})', errs)
    ids_seen = []
    for m in modes:
        mid = m.get('id')
        name = m.get('name')
        ids_seen.append(mid)
        exp = EXPECTED_MAPPING.get(mid)
        if exp is None:
            errs.append(f'unexpected mode id={mid}')
            continue
        require(name == exp[0], f'mode {mid}: name mismatch “{name}” != “{exp[0]}”', errs)
        require(m.get('bleach_mapping') == exp[1], f'mode {mid} ({name}): bleach_mapping must be “{exp[1]}”, got “{m.get("bleach_mapping")}”', errs)
        # each mode must have mechanics list and risks_to_avoid list
        require(isinstance(m.get('mechanics'), list) and m['mechanics'], f'mode {mid} ({name}): mechanics must be non-empty list', errs)
        require(isinstance(m.get('risks_to_avoid'), list) and m['risks_to_avoid'], f'mode {mid} ({name}): risks_to_avoid must be non-empty list', errs)
    require(sorted(ids_seen) == list(range(1, 17)), f'ids must be exactly 1..16 (got {sorted(ids_seen)})', errs)
    # Corrections explicitly listed
    corr = {entry.get('mode') for entry in j.get('previous_wrong_mappings_to_correct', [])}
    missing_corrections = REQUIRED_CORRECTIONS - corr
    require(not missing_corrections, f'previous_wrong_mappings_to_correct missing: {sorted(missing_corrections)}', errs)
    return finish_result(NAME, errs, LIVE_MODES_DIR, {'mode_count': len(modes)})


if __name__ == '__main__':
    sys.exit(main())
