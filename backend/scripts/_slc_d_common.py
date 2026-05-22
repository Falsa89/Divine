#!/usr/bin/env python3
"""Shared helpers for SLC-D validators — design-only / read-only."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

SLC_DIR = Path('/app/data/design/server_lifecycle')
SAFETY_DIR = Path('/app/data/design/system_safety')
CANON_DIR = Path('/app/data/design/benchmark_canonical')


def load(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding='utf-8'))


def require(cond: bool, msg: str, errs: list) -> bool:
    if not cond:
        errs.append(msg)
        return False
    return True


def require_design_only(j: dict, errs: list, label: str):
    for k, exp in (('design_only', True), ('runtime_attached', False),
                    ('battle_runtime_attached', False), ('merge_execution_allowed', False),
                    ('db_write', False)):
        require(j.get(k) is exp, f'{label}: {k} must be {exp} (got {j.get(k)})', errs)


def finish(name: str, errs: list, target_dir: Path = SLC_DIR, extra: dict | None = None) -> int:
    status = 'PASS' if not errs else 'FAIL'
    payload = {'task': name, 'status': status, 'errors': errs,
               'utc': datetime.now(timezone.utc).isoformat(),
               'design_only': True, 'no_db_write': True}
    if extra:
        payload.update(extra)
    (target_dir / f'_{name}_result.json').write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{name}] {status} errors={len(errs)}')
    for e in errs:
        print(f'  - {e}')
    return 0 if status == 'PASS' else 1
