#!/usr/bin/env python3
"""SLC-A: Validate server-age calendar schema + example entries (read-only)."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path('/app/data/design/server_lifecycle')
OUT = Path(ROOT, '_validate_server_age_calendar_schema_v1_result.json')
SCHEMA = ROOT / 'server_age_calendar_schema_v1.json'
EXAMPLE = ROOT / 'server_age_calendar_example_first_180_days_v1.json'
VALID_TYPES = None  # filled from schema
VALID_REC = {'must_catch_up','optional_catch_up','compress','skip'}
BOREA = {'borea','greek_borea','primordial_gaia'}


def main():
    errs=[]
    if not SCHEMA.exists(): errs.append('schema:missing'); print('FAIL'); return 2
    if not EXAMPLE.exists(): errs.append('example:missing'); print('FAIL'); return 2
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    global VALID_TYPES
    VALID_TYPES = set(schema.get('event_types') or [])
    for k in (VALID_REC):
        if k not in (schema.get('recovery_classes') or []):
            errs.append(f'schema:missing_recovery_class:{k}')
    if not schema.get('design_only'): errs.append('schema:not_design_only')
    if schema.get('runtime_attached'): errs.append('schema:runtime_attached')
    if schema.get('battle_runtime_attached'): errs.append('schema:battle_attached')
    forbidden = set(schema.get('forbidden_hero_ids_in_banner') or [])
    for b in BOREA:
        if b not in forbidden: errs.append(f'schema:borea_not_forbidden:{b}')

    entries = example.get('entries') or []
    if len(entries) < 10: errs.append(f'example:too_few_entries:{len(entries)}')
    seen_ids=set(); must_count=0; skip_count=0; compress_count=0
    for e in entries:
        eid = e.get('entry_id','?')
        if not re.match(r'^cal_[a-z0-9_]+$', eid): errs.append(f'example:bad_entry_id:{eid}')
        if eid in seen_ids: errs.append(f'example:dup_id:{eid}')
        seen_ids.add(eid)
        if e.get('event_type') not in VALID_TYPES: errs.append(f'example:bad_event_type:{eid}:{e.get("event_type")}')
        if e.get('recovery_class') not in VALID_REC: errs.append(f'example:bad_recovery_class:{eid}:{e.get("recovery_class")}')
        if e.get('design_only') is not True: errs.append(f'example:not_design_only:{eid}')
        if e.get('runtime_attached') is not False: errs.append(f'example:runtime_attached:{eid}')
        if e.get('battle_runtime_attached') is not False: errs.append(f'example:battle_attached:{eid}')
        s = e.get('server_day_start'); en = e.get('server_day_end')
        if not (isinstance(s,int) and isinstance(en,int) and en >= s):
            errs.append(f'example:bad_day_range:{eid}')
        bid = (e.get('banner_id') or '').lower()
        for b in BOREA:
            if b in bid: errs.append(f'example:borea_in_banner:{eid}:{bid}')
        if e.get('recovery_class') == 'must_catch_up': must_count += 1
        if e.get('recovery_class') == 'skip': skip_count += 1
        if e.get('recovery_class') == 'compress': compress_count += 1
        # consistency: skip must imply can_be_skipped=true and not has_unique_hero
        if e.get('recovery_class') == 'skip' and e.get('has_unique_hero'):
            errs.append(f'example:skip_has_unique_hero:{eid}')
        # must_catch_up should not be can_be_skipped=true (you can still compress but not skip)
        if e.get('recovery_class') == 'must_catch_up' and e.get('can_be_skipped'):
            errs.append(f'example:must_catch_up_but_can_be_skipped:{eid}')
    if must_count < 4: errs.append(f'example:must_catch_up_too_few:{must_count}')
    if skip_count < 1: errs.append(f'example:skip_missing')
    if compress_count < 1: errs.append(f'example:compress_missing')

    out = {
        'task_origin':'SLC-A-VALIDATE-CALENDAR-SCHEMA',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'entries_count': len(entries),
        'must_catch_up_count': must_count,
        'compress_count': compress_count,
        'skip_count': skip_count,
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} entries={len(entries)} must={must_count} compress={compress_count} skip={skip_count} errors={len(errs)}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
