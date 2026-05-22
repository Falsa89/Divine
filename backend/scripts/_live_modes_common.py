#!/usr/bin/env python3
"""LIVE-MODES-RECONCILIATION-A — helper for live-mode validators."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

LIVE_MODES_DIR = Path('/app/data/design/live_modes')
SLC_DIR = Path('/app/data/design/server_lifecycle')
SAFETY_DIR = Path('/app/data/design/system_safety')


def load_json_at(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding='utf-8'))


def require(cond: bool, msg: str, errs: list) -> bool:
    if not cond:
        errs.append(msg)
        return False
    return True


def require_design_only_flags(j: dict, errs: list, name: str):
    require(j.get('design_only') is True, f'{name}: design_only must be True', errs)
    require(j.get('runtime_attached') is False, f'{name}: runtime_attached must be False', errs)
    require(j.get('battle_runtime_attached') is False, f'{name}: battle_runtime_attached must be False', errs)


def finish_result(name: str, errs: list, target_dir: Path, extra: dict | None = None) -> int:
    status = 'PASS' if not errs else 'FAIL'
    payload = {
        'task': name, 'status': status,
        'errors': errs, 'utc': datetime.now(timezone.utc).isoformat(),
        'design_only': True, 'no_db_write': True,
    }
    if extra:
        payload.update(extra)
    out = target_dir / f'_{name}_result.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    print(f'[{name}] {status} errors={len(errs)}')
    for e in errs:
        print(f'  - {e}')
    return 0 if status == 'PASS' else 1
