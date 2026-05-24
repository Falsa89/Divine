#!/usr/bin/env python3
"""PROJECT_Q Track E — dry-run import script (default mode: DRY-RUN).

Usage:
    python3 import_project_q_artifact_bible_dry_run_v1.py             # dry-run
    python3 import_project_q_artifact_bible_dry_run_v1.py --apply     # GATED on all 5 ARTIFACT_* signatures
    python3 import_project_q_artifact_bible_dry_run_v1.py --rollback  # GATED on import marker presence
"""
import argparse, json, os, sys
from pathlib import Path

CAND = Path('/app/data/design/artifacts/project_q_artifact_candidate_expansion_v1.json')
SCHEMA = Path('/app/data/design/artifacts/artifact_bible_schema_v1.json')
REQ_SIGS = ('ARTIFACT_USER_APPROVAL', 'ARTIFACT_ECONOMY_APPROVAL', 'ARTIFACT_BALANCE_APPROVAL', 'ARTIFACT_QA_APPROVAL', 'ARTIFACT_IMPORT_LIVE_OK')
FORBIDDEN_IN_FIELDS = ('is_equipment', 'occupies_gear_slot', 'is_divine_weapon')
MASTER_CAP_PCT = 5.0
PER_ART_MAX_PCT = 1.5


def _validate(art):
    errs = []
    if not isinstance(art.get('artifact_id'), str) or not art['artifact_id'].startswith('art_'):
        errs.append('artifact_id missing or wrong prefix')
    if not isinstance(art.get('name'), str) or len(art.get('name', '')) > 64: errs.append('name')
    if not isinstance(art.get('rarity'), int) or not (1 <= art['rarity'] <= 6): errs.append('rarity')
    if art.get('linked_faction') not in {'greek', 'norse', 'egyptian', 'japanese', 'celtic', 'primordial', 'crossfaction'}: errs.append('linked_faction')
    if art.get('collection_category') not in {'weapon_relic', 'armor_relic', 'icon_relic', 'glyph_relic', 'vessel_relic', 'banner_relic'}: errs.append('collection_category')
    if art.get('obtainment_source') == 'hero_summon_banner': errs.append('obtainment_source must NOT be hero_summon_banner')
    for k in FORBIDDEN_IN_FIELDS:
        if art.get(k) is not False: errs.append(f'{k} must be false')
    bonus = art.get('global_roster_account_bonus') or {}
    v = float(bonus.get('value_pct', 0.0))
    if v < 0 or v > PER_ART_MAX_PCT: errs.append(f'value_pct {v} out of bounds (max {PER_ART_MAX_PCT})')
    if v > MASTER_CAP_PCT: errs.append('master cap exceeded')
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--rollback', action='store_true')
    args = ap.parse_args(argv)

    if not CAND.exists(): print('[ABORT] candidate file missing'); return 2
    data = json.loads(CAND.read_text())
    arts = data.get('candidates') or []
    print(f'[INFO] loaded {len(arts)} candidates')
    pass_n = 0; fail_n = 0
    for art in arts:
        errs = _validate(art)
        if errs:
            fail_n += 1
            print(f'  [FAIL] {art.get("artifact_id")}: {errs}')
        else:
            pass_n += 1
    print(f'[INFO] schema+invariants: {pass_n} PASS / {fail_n} FAIL')

    if args.apply:
        missing = [s for s in REQ_SIGS if os.environ.get(s, '').strip().lower() != 'true']
        if missing:
            print(f'[ABORT] --apply requires all 5 ARTIFACT_* signatures; missing: {missing}')
            return 3
        print('[OK] all 5 signatures present — would write to MongoDB (mongodb://localhost:27017 db=divine_waifus collection=artifacts)')
        print('[STOP] live write intentionally NOT executed in this PROJECT_Q deliverable; this is the dry-run script')
        return 0
    if args.rollback:
        print('[INFO] rollback target: documents in artifacts collection with artifact_id in batch (8)')
        print('[STOP] rollback intentionally NOT executed in this PROJECT_Q deliverable; this is the dry-run script')
        return 0
    print('[DRY-RUN] no DB writes performed; pass --apply (with signatures) or --rollback for live ops')
    return 0


if __name__ == '__main__': sys.exit(main())
