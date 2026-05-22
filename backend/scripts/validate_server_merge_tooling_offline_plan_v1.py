#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require, require_design_only  # noqa: E402
NAME = 'server_merge_tooling_offline_plan_v1'
REQUIRED_TOOLS = {'merge_eligibility_evaluator','merge_group_planner','conflict_resolution_resolver',
                  'recovery_season_planner','calendar_harmonizer','offline_simulator',
                  'risk_classifier','abort_rollback_planner'}
REQUIRED_PHASES = {'design_freeze','eligibility_evaluation','group_planning','conflict_resolution_plan',
                   'recovery_season_plan','calendar_harmonization','dry_run_simulation',
                   'approval_gate_user_explicit','controlled_execution_outside_slc_d','post_merge_audit'}


def main() -> int:
    errs = []
    j = load(SLC_DIR / 'server_merge_tooling_offline_plan_v1.json')
    require_design_only(j, errs, NAME)
    require(j.get('second_server_opening_allowed') is False, 'second_server_opening_allowed must be False', errs)
    require(j.get('route_patch_applied') is False, 'route_patch_applied must be False', errs)
    tools = {t.get('name') for t in j.get('tooling_components', [])}
    require(REQUIRED_TOOLS <= tools, f'tooling_components missing: {sorted(REQUIRED_TOOLS - tools)}', errs)
    for t in j.get('tooling_components', []):
        require(t.get('runtime') is False and t.get('reads_only') is True, f'tool {t.get("name")} must be offline/reads-only', errs)
    hg = j.get('hard_guardrails', {})
    for k in ('db_writes','migrations','runtime_route_patch','auth_runtime_change','server_selection_runtime',
              'second_server_opening','merge_execution','live_server_redirect','ui_implementation',
              'battle_engine_changes','battle_core_changes','combat_tsx_changes',
              'affinity_gift_spend_changes','af2n_stage4_changes','redis_runtime_changes',
              'set_server_profiles_runtime_enabled','set_second_server_opening_enabled'):
        require(hg.get(k) is False, f'hard_guardrails.{k} must be False', errs)
    phases = set(j.get('required_phases', []))
    require(REQUIRED_PHASES <= phases, f'required_phases missing: {sorted(REQUIRED_PHASES - phases)}', errs)
    return finish(NAME, errs, extra={'tool_count': len(tools)})


if __name__ == '__main__':
    sys.exit(main())
