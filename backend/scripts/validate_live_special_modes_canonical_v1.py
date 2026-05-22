#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags, check_canonical_fields  # noqa: E402

NAME = 'live_special_modes_canonical_v1'
EXPECTED_NAMES = [
    'Giudizio di Asgard', 'Cammino dell\u2019Ade', 'Scala dell\u2019Olimpo',
    'Sigilli degli Dei', 'Torre degli Inferi', 'Troni dell\u2019Eclissi',
    'Prove del Pantheon', 'Abisso del Colosso', 'Crepuscolo dei Titani',
    'Giudizio delle Stirpi', 'Fronti del Valhalla', 'Guerra dei Tre Troni',
    'Fame del Behemoth', 'Furie del Pantheon', 'Titanomachia', 'Assalto del Ragnar\u00f6k',
]


def main() -> int:
    errs = []
    j = load('live_special_modes_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    modes = j.get('modes', [])
    require(len(modes) == 16, f'must have exactly 16 modes (got {len(modes)})', errs)
    ids = [m.get('id') for m in modes]
    require(sorted(ids) == list(range(1, 17)), f'ids must be 1..16 (got {sorted(ids)})', errs)
    names = [m.get('name') for m in modes]
    for n in EXPECTED_NAMES:
        require(n in names, f'missing mode name: {n}', errs)
    for m in modes:
        check_canonical_fields(m, f'mode “{m.get("name")}”', errs)
    # Scrigni dell’Elisio in additional_modes
    add = j.get('additional_modes', [])
    require(any(a.get('name') == 'Scrigni dell\u2019Elisio' for a in add), 'additional_modes must include Scrigni dell\u2019Elisio', errs)
    return finish(NAME, errs, {'mode_count': len(modes)})


if __name__ == '__main__':
    sys.exit(main())
