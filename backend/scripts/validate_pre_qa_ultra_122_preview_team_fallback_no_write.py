#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_preview_team_fallback_no_write.

Verifica che il preview team fallback policy JSON esista e sia onesto:
  - enabled_only_for_preview=true
  - persistent=false
  - db_write=false
  - reward_allowed=false
  - progress_allowed=false
  - account_roster_mutation=false
  - live_mode_allowed=false
  - banner_required=true
  - allowed_modes copre 5 mode
  - fail_closed_conditions presenti
  - wiring_status dichiarato esplicitamente (true/false), no fake PASS.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
POLICY = os.path.join(R, 'data', 'design', 'vertical_slice_qa',
                      'ultra_122_preview_team_fallback_policy_v1.json')

REQUIRED_FALSE = ['persistent', 'db_write', 'reward_allowed',
                  'progress_allowed', 'account_roster_mutation',
                  'live_mode_allowed']
REQUIRED_TRUE = ['enabled_only_for_preview', 'banner_required']
REQUIRED_MODES = {'story', 'tower', 'training', 'arena', 'boss'}


def main() -> int:
    if not os.path.exists(POLICY):
        print(f'[v122_preview_team_fallback_no_write] FAIL policy missing: {POLICY}')
        return 1
    p = json.load(open(POLICY, encoding='utf-8'))
    failures = []
    for k in REQUIRED_FALSE:
        if p.get(k) is not False:
            failures.append(f'{k} != false')
    for k in REQUIRED_TRUE:
        if p.get(k) is not True:
            failures.append(f'{k} != true')
    if set(p.get('allowed_modes') or []) != REQUIRED_MODES:
        failures.append(f'allowed_modes != {REQUIRED_MODES}')
    if not p.get('fail_closed_conditions'):
        failures.append('fail_closed_conditions vuoto')
    ws = p.get('wiring_status_in_122') or {}
    # Wiring status DEVE essere dichiarato esplicitamente (true o false)
    if 'runtime_wiring_implemented_in_122' not in ws:
        failures.append('wiring_status_in_122.runtime_wiring_implemented_in_122 mancante')
    if failures:
        print('[v122_preview_team_fallback_no_write] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1
    wired = ws.get('runtime_wiring_implemented_in_122')
    print(f'[v122_preview_team_fallback_no_write] OK policy_safe=true runtime_wired={wired}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
