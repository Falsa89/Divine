#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _benchmark_canonical_common import load, finish, require, check_mandatory_flags  # noqa: E402

NAME = 'slc_f_next_checkpoint_canonical_v1'
REQUIRED_OUTPUTS = {
    'server-aware route patch matrix',
    'per-route risk classification',
    'server-bound/account-wide collection mapping',
    'pseudo-diff / patch contract only',
    'dry-run resolver simulation for account_id + server_id',
    'protected-file no-diff audit',
    'DB no-write audit',
    'future phase recommendations',
}


def main() -> int:
    errs = []
    j = load('slc_f_next_checkpoint_canonical_v1.json')
    check_mandatory_flags(j, errs, NAME)
    require(j.get('execute_now') is False, 'execute_now must be False', errs)
    require(j.get('checkpoint') == 'SLC-F route patch dry-run', f'checkpoint label mismatch (got {j.get("checkpoint")})', errs)
    outs = set(j.get('required_outputs', []))
    missing = REQUIRED_OUTPUTS - outs
    require(not missing, f'required_outputs missing: {sorted(missing)}', errs)
    hg = j.get('hard_guardrails', {})
    for k in ('runtime_patch', 'db_writes', 'migrations', 'route_creation',
              'auth_runtime_change', 'ui', 'second_server_opening',
              'battle_engine_changes', 'battle_core_changes', 'combat_tsx_changes',
              'affinity_gift_spend_changes', 'af2n_stage4_changes'):
        require(hg.get(k) is False, f'hard_guardrails.{k} must be False', errs)
    acc = j.get('acceptance', {})
    for k in ('route_patch_applied', 'db_write', 'migration_applied', 'second_server_opening_allowed'):
        require(acc.get(k) is False, f'acceptance.{k} must be False', errs)
    require(acc.get('future_feature_flags_remain_false') is True, 'acceptance.future_feature_flags_remain_false must be True', errs)
    return finish(NAME, errs)


if __name__ == '__main__':
    sys.exit(main())
