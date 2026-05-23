#!/usr/bin/env python3
# SLC-H SERVER STATUS CONTRACT VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_h_server_status_contract_v1_result.json'
SRC = DESIGN_DIR / 'slc_h_server_status_contract_v1.json'
FLOW = DESIGN_DIR / 'slc_h_future_flow_contract_v1.json'
UI = DESIGN_DIR / 'slc_h_ui_handoff_notes_v1.json'

REQUIRED_STATUSES = {'planned','open','crowded','closed_to_new','merge_pending','merged','archived'}
REQUIRED_FLOW_IDS = {'FR-001','FR-002','FR-003','FR-004','FR-005','FR-006','FR-007','FR-008'}

def main():
    errs = []
    if not SRC.exists():
        errs.append('status_contract_missing')
    else:
        d = json.loads(SRC.read_text())
        if d.get('design_only') is not True: errs.append('design_only_not_true')
        statuses = {s.get('status') for s in (d.get('statuses') or [])}
        for r in REQUIRED_STATUSES:
            if r not in statuses: errs.append(f'status_missing:{r}')
        # forbidden transitions present
        forbidden = d.get('transitions_forbidden') or []
        if not any(t == ['merged','open'] for t in forbidden): errs.append('forbidden_transition_missing:merged_to_open')
        if not any(t == ['archived','open'] for t in forbidden): errs.append('forbidden_transition_missing:archived_to_open')
        # AF2-N safety
        af = d.get('af2n_safety') or {}
        if af.get('server_status_change_MUST_NOT_change_cap') != 50000: errs.append('af2n_cap_invariant_missing')
        if af.get('server_status_change_MUST_NOT_change_allowlist') != 2500: errs.append('af2n_allowlist_invariant_missing')
        # Borea safety
        bs = d.get('borea_safety') or {}
        if bs.get('server_status_change_MUST_NOT_affect_borea_visibility') is not True: errs.append('borea_safety_missing')
        if bs.get('primordial_gaia_MUST_remain_404') is not True: errs.append('primordial_gaia_invariant_missing')

    if not FLOW.exists():
        errs.append('flow_contract_missing')
    else:
        f = json.loads(FLOW.read_text())
        ids = {r.get('id') for r in (f.get('flow_rules') or [])}
        for r in REQUIRED_FLOW_IDS:
            if r not in ids: errs.append(f'flow_rule_missing:{r}')
        tree = f.get('selection_decision_tree') or []
        if not any('second_server_locked' in s for s in tree): errs.append('decision_tree_missing_second_server_locked')
        if not any('route_patch_not_applied' in s for s in tree): errs.append('decision_tree_missing_route_patch_not_applied')
        if not any('server_profiles_runtime_disabled' in s for s in tree): errs.append('decision_tree_missing_server_profiles_runtime_disabled')

    if not UI.exists():
        errs.append('ui_handoff_notes_missing')
    else:
        u = json.loads(UI.read_text())
        if u.get('ui_implemented') is not False: errs.append('ui_implemented_not_false')
        if u.get('copy_language') != 'it_IT': errs.append('copy_language_not_it_IT')
        screens = {s.get('screen') for s in (u.get('target_screens') or [])}
        for s in ('server_selection_list','server_profile_card_detail','new_server_warning_dialog','paid_currency_display_warning'):
            if s not in screens: errs.append(f'ui_screen_missing:{s}')
        hard = u.get('hard_ui_no_go') or []
        if not any('NO live screen implementation' in h for h in hard): errs.append('hard_ui_no_go_live_screen_missing')
        if not any('NO route registration' in h for h in hard): errs.append('hard_ui_no_go_route_registration_missing')

    out = {'task_origin':'SLC-H-SERVER-STATUS-CONTRACT','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'errors':errs,'verdict':'PASS' if not errs else 'FAIL'}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-H-SERVER-STATUS-CONTRACT {out['verdict']} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
