#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track G validator (audit-only).
# Verifica master backlog + feature completeness gap matrix.
import json, sys
from pathlib import Path
BL = Path('/app/data/design/audit/full_repo/master_fix_backlog_and_batching_plan_v1.json')
GM = Path('/app/data/design/audit/full_repo/feature_completeness_gap_matrix_v1.json')
ALLOWED_STATES = {
    'PRESENT_LIVE', 'PRESENT_LOCKED_PREVIEW', 'PRESENT_BACKEND_ONLY',
    'PRESENT_FRONTEND_ONLY', 'PRESENT_LEGACY', 'PRESENT_DEV_ONLY',
    'PARTIAL', 'MISSING', 'DEFERRED_BY_DESIGN', 'NEEDS_DECISION',
}
ALLOWED_PRIO = {'P0', 'P1', 'P2', 'P3'}
FIELDS = ('feature_id', 'product_area', 'expected_final_state',
          'current_code_state', 'frontend_route', 'backend_endpoint',
          'data_collection', 'live_mutation', 'player_visible', 'risk',
          'missing_parts', 'decision_needed', 'recommended_pack', 'priority')

def main():
    b = json.loads(BL.read_text())
    g = json.loads(GM.read_text())
    assert b['verdict'] == 'TRACK_G_MASTER_FIX_BACKLOG_AND_BATCHING_PLAN_READY'
    assert g['verdict'] == 'TRACK_G_FEATURE_COMPLETENESS_GAP_MATRIX_READY'
    assert len(b['backlog']) >= 20
    prios = {it['priority'] for it in b['backlog']}
    assert prios.issubset(ALLOWED_PRIO)
    # P0 deve includere almeno gacha/artifact/soul-forge lock packs
    p0_ids = {it['pack_id'] for it in b['backlog'] if it['priority'] == 'P0'}
    for must in ('PROJECT_GACHA_RATE_SANITY_FIX_OR_LOCK_PACK',
                 'PROJECT_ARTIFACT_CONSTELLATION_SURFACE_LOCK_PACK'):
        assert must in p0_ids, f'missing P0 pack: {must}'
    # Sequence ordinata e popolata
    assert len(b['recommended_pack_sequence']) >= 8
    assert len(b['batching_proposal']) >= 4
    # GAP MATRIX checks
    feats = g['features']
    assert len(feats) >= 30
    seen_ids = set()
    for f in feats:
        for k in FIELDS:
            assert k in f, f'missing {k} in {f.get("feature_id")}'
        assert f['expected_final_state'] in ALLOWED_STATES, f['expected_final_state']
        assert f['current_code_state'] in ALLOWED_STATES, f['current_code_state']
        assert f['priority'] in ALLOWED_PRIO
        assert f['feature_id'] not in seen_ids, f'duplicate {f["feature_id"]}'
        seen_ids.add(f['feature_id'])
    # Areas of interest minimi
    must_features = {
        'GACHA_SUMMON', 'ARTIFACTS', 'CONSTELLATIONS', 'SHOP', 'IAP',
        'VIP', 'BATTLE_PASS', 'HOUSING', 'STATUS_SYSTEM',
        'ROSTER_OWNED_LEGACY', 'SERVER_SELECTION', 'ANNOUNCEMENTS_NEWS',
        'MAINTENANCE_NOTICE', 'PATCH_NOTES', 'RED_DOT_NOTIFICATIONS',
        'PUSH_NOTIFICATIONS', 'LOGIN_AUTH', 'EVENTS', 'ACHIEVEMENTS',
        'MAIL_INBOX_REWARDS', 'EXCLUSIVE_ITEMS', 'SOUL_FORGE',
    }
    missing = must_features - seen_ids
    assert not missing, f'gap matrix missing required features: {missing}'
    # No mutations
    assert b['db_writes'] == 0 and g['db_writes'] == 0
    assert b['backend_changes'] == 0 and g['backend_changes'] == 0
    print(f"[PASS] FULL-REPO Track G \u2014 backlog={len(b['backlog'])} features={len(feats)} P0_packs={len(p0_ids)}")
    return 0
if __name__ == '__main__': sys.exit(main())
