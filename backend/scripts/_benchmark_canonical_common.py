#!/usr/bin/env python3
"""Helper for benchmark canonical validators — read-only."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

CANON_DIR = Path('/app/data/design/benchmark_canonical')

MANDATORY_FLAGS = (
    ('design_only', True),
    ('runtime_attached', False),
    ('battle_runtime_attached', False),
    ('implementation_allowed_now', False),
)
MANDATORY_PACK = 'DIVINE_BENCHMARK_CANONICAL_SOURCE_PACK'


def load(name: str) -> dict:
    p = CANON_DIR / name
    if not p.exists():
        raise FileNotFoundError(str(p))
    return json.loads(p.read_text(encoding='utf-8'))


def require(cond: bool, msg: str, errs: list) -> bool:
    if not cond:
        errs.append(msg)
        return False
    return True


def check_mandatory_flags(j: dict, errs: list, label: str):
    for k, exp in MANDATORY_FLAGS:
        require(j.get(k) is exp, f'{label}: {k} must be {exp} (got {j.get(k)})', errs)
    require(j.get('source_pack') == MANDATORY_PACK, f'{label}: source_pack must be {MANDATORY_PACK}', errs)


def check_canonical_fields(entry: dict, label: str, errs: list, optional_inspiration: bool = False):
    """Generic canonical-entry checks."""
    for k in ('how_works_in_divine', 'do_not_import', 'runtime_status'):
        require(k in entry, f'{label}: missing field "{k}"', errs)
    require(isinstance(entry.get('how_works_in_divine'), list) and entry['how_works_in_divine'], f'{label}: how_works_in_divine must be non-empty list', errs)
    require(isinstance(entry.get('do_not_import'), list) and entry['do_not_import'], f'{label}: do_not_import must be non-empty list', errs)
    if not optional_inspiration:
        require(('import_from_benchmark' in entry) or ('benchmark_inspiration' in entry) or ('confirmed_benchmark' in entry),
                f'{label}: at least one of import_from_benchmark / benchmark_inspiration / confirmed_benchmark required', errs)


def finish(name: str, errs: list, extra: dict | None = None) -> int:
    status = 'PASS' if not errs else 'FAIL'
    payload = {
        'task': name, 'status': status, 'errors': errs,
        'utc': datetime.now(timezone.utc).isoformat(),
        'design_only': True, 'no_db_write': True,
    }
    if extra:
        payload.update(extra)
    (CANON_DIR / f'_{name}_result.json').write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{name}] {status} errors={len(errs)}')
    for e in errs:
        print(f'  - {e}')
    return 0 if status == 'PASS' else 1
