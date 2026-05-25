#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track A validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/batch1_v2/track_a_findings_confirmation_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_BATCH_1_V2_FINDINGS_CONFIRMATION_AND_SCOPE_LOCK_READY'
    assert len(d['confirmed_findings']) >= 8
    sc = d['scope_constraints']
    for k in ('frontend_only', 'no_db_writes', 'no_backend_route_changes',
              'no_iap_implementation', 'no_hero_deletion', 'no_flag_flips',
              'no_rate_changes', 'no_price_changes', 'no_reward_changes'):
        assert sc[k] is True, f'scope constraint {k} must be True'
    assert sc['battle_engine_md5_pre'] == '151ca35ad3bc35f0a6209cb3744ed440'
    assert sc['backend_env_md5_pre'] == 'ff60bbb79efa329b71aa8ed351ea89b3'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] BATCH1-V2 Track A \u2014 findings={len(d['confirmed_findings'])}")
    return 0
if __name__ == '__main__': sys.exit(main())
