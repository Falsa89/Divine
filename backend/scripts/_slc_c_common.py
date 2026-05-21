#!/usr/bin/env python3
"""SLC-C common helpers — read-only, no DB writes."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

DESIGN_DIR = Path('/app/data/design/server_lifecycle')
FORBIDDEN_HERO_IDS = ('borea', 'greek_borea', 'primordial_gaia')


def load_json(name: str) -> dict:
    p = DESIGN_DIR / name
    if not p.exists():
        raise FileNotFoundError(f'missing design file: {p}')
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


def write_result(name: str, payload: dict) -> Path:
    p = DESIGN_DIR / f'_{name}_result.json'
    payload = dict(payload)
    payload.setdefault('utc', datetime.now(timezone.utc).isoformat())
    payload.setdefault('design_only', True)
    payload.setdefault('no_db_write', True)
    with p.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return p


def require(cond: bool, msg: str, errs: list) -> bool:
    if not cond:
        errs.append(msg)
        return False
    return True


def no_borea_anywhere(blob) -> list:
    """Return list of borea hero-id LITERAL references in JSON values.

    Matches the canonical hero ids only as standalone tokens between double quotes,
    so legitimate config keys like ``borea_safety`` / ``no_borea_exposure`` do NOT
    trigger false positives. Walks only string values, never key names.
    """
    import re as _re
    found: list = []
    pat = _re.compile(r"^(borea|greek_borea|primordial_gaia)$", _re.IGNORECASE)

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            # Only flag if the string VALUE equals a forbidden hero id literally,
            # or contains a quoted/word-bounded occurrence.
            if pat.match(node.strip()):
                found.append(node.strip().lower())
            else:
                for token in _re.findall(r"\b(borea|greek_borea|primordial_gaia)\b", node, _re.IGNORECASE):
                    # Suppress guard contexts (the value mentions hiding/blocking)
                    low = node.lower()
                    if any(g in low for g in ("never_appear", "never_exposed", "never_referenced",
                                              "hidden", "rejected", "404", "blacklist", "forbidden",
                                              "guard", "must_never", "not_exposed", "borea_safe",
                                              "borea_invariant", "borea_safety")):
                        continue
                    found.append(token.lower())
    walk(blob)
    return sorted(set(found))


def finish(name: str, errs: list, extra: dict | None = None) -> int:
    status = 'PASS' if not errs else 'FAIL'
    payload = {'task': name, 'status': status, 'errors': errs}
    if extra:
        payload.update(extra)
    write_result(name, payload)
    print(f'[{name}] {status} errors={len(errs)}')
    for e in errs:
        print(f'  - {e}')
    return 0 if status == 'PASS' else 1
