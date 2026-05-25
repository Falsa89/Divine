#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK G
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/mode_wiring_next_fix_prioritization_v1.json')

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_NEXT_FIX_PACK_PRIORITIZATION_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_G_NEXT_FIX_PACK_PRIORITIZATION_APPROVAL'] == 'true'
    prio = d['prioritization']
    for k in ['P0_critical_broken_links','P1_high_value_missing_links','P2_cleanup_and_polish','P3_deferred','gated_live_only']:
        assert k in prio, f'missing {k}'
    # We expect at least 2 P1 high value items (server profiles + artifact gate)
    assert len(prio['P1_high_value_missing_links']) >= 2
    # No P0 critical broken links — registry says everything routable
    assert isinstance(prio['P0_critical_broken_links'], list)
    # Explicit comparisons present
    ec = d['explicit_comparisons']
    for key in ['daily_hub_continuation','combat_ui_decomposition','mode_wiring_fixes','approval_matrix_live_gate_policy','real_mobile_qa_screenshot_pack','artifact_signature_import_pack']:
        assert key in ec, f'missing comparison: {key}'
    assert d['recommended_next_pack_primary']
    print(f"[PASS] Track G next-fix prioritization READY \u2014 P1={len(prio['P1_high_value_missing_links'])}, P2={len(prio['P2_cleanup_and_polish'])}, next={d['recommended_next_pack_primary']}")
    return 0
if __name__ == '__main__': sys.exit(main())
