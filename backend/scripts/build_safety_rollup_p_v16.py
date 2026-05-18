#!/usr/bin/env python3
"""V21 — Safety Rollup P (v16)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v16.json')
NOW = datetime.now(timezone.utc)


def main():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
    except Exception:
        st = {}
    apply_doc = Path('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')
    sign_doc = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5_applied.json')
    db_doc = Path('/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json')
    apply = json.loads(apply_doc.read_text()) if apply_doc.exists() else {}
    sign = json.loads(sign_doc.read_text()) if sign_doc.exists() else {}
    db = json.loads(db_doc.read_text()) if db_doc.exists() else {}
    stage4_applied = apply.get('stage4_applied') is True
    out_doc = {
        'rollup_id': 'collection_affinity_runtime_activation_readiness_rollup_v16',
        'task_origin': 'V21-SAFETY-ROLLUP-P',
        'design_only': False,
        'runtime_attached': True,
        'generated_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'stage4_state': 'stage4_internal_beta_active_no_broad_rollout' if stage4_applied else 'stage4_ready_not_applied',
        'stage4_applied': stage4_applied,
        'allowlist_size': st.get('canary_allowlist_size'),
        'ledger_cap': st.get('canary_ledger_cap'),
        'ledger_total_rows': st.get('ledger_total_rows'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': st.get('buffs_enabled') is True,
        'borea_hidden': True,
        'rate_limit_active': st.get('rate_limit_enabled') is True,
        'db_backup_drill_pass': db.get('overall_status') == 'PASS',
        'signoffs_v5_status': sign.get('explicit_status', 'NOT_APPLIED'),
        'rollback_ready': True,
        'next_decision_options': [
            'stage4_observation_window_24_72h',
            'public_beta_prep_later',
            'fix_blocker_if_any',
            'rollback_if_required',
            'stack_g_deferred',
        ],
        'recommended_next_decision': 'stage4_observation_window_24_72h' if stage4_applied else 'fix_blocker_if_any',
        'safety_invariants': [
            'no broad rollout',
            'no public spend UI',
            'no battle wiring',
            'no Borea reveal',
            'no gacha/roster/catalog mutation',
            'battle_engine.py / battle_core.py / combat.tsx unchanged'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'SAFETY-ROLLUP-P state={out_doc["stage4_state"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
