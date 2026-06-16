#!/usr/bin/env python3
"""
Pack 126 — Validator: before/after state has no mutation post-preview.
Reads two snapshots (before and after) from backend/scripts/reports and
compares totals.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = REPO_ROOT / 'backend' / 'scripts' / 'reports'


def main() -> int:
    errors = []
    before = sorted(REPORTS.glob('pack_126_state_before_*.json'))
    after = sorted(REPORTS.glob('pack_126_state_after_*.json'))
    if not before:
        errors.append('no before snapshot found (pack_126_state_before_*.json). Use qa_state_capture.py --label before')
        return _emit(errors, {})
    if not after:
        # not blocker; mark as NEEDS_DEVICE_CONFIRMATION
        print('NOTE  no after snapshot yet — NEEDS_DEVICE_CONFIRMATION after device QA preview')
        return _emit_partial(errors)
    b = json.loads(before[-1].read_text(encoding='utf-8'))
    a = json.loads(after[-1].read_text(encoding='utf-8'))
    detail = {'before': before[-1].name, 'after': after[-1].name}
    # Allow only seed-related changes if label after is 'after_seed'.
    if a.get('label', '').startswith('after_seed'):
        # Seed phase: expect user_heroes_count >= before. NO change to total_exp/gold/diamonds.
        if a['user_heroes_total_exp'] != b['user_heroes_total_exp']:
            errors.append(f'total_exp changed during seed: {b["user_heroes_total_exp"]} -> {a["user_heroes_total_exp"]}')
        if a['user'].get('gold') != b['user'].get('gold'):
            errors.append(f'gold changed during seed: {b["user"]["gold"]} -> {a["user"]["gold"]}')
        if a['user'].get('diamonds') != b['user'].get('diamonds'):
            errors.append('diamonds mutated')
        if a['user_heroes_count'] < b['user_heroes_count']:
            errors.append('user_heroes_count DECREASED during seed (unexpected)')
        else:
            print(f"OK    seed phase: heroes {b['user_heroes_count']} -> {a['user_heroes_count']}, exp/gold/diamonds invariati")
    else:
        # After preview: STRICT equality on user/state.
        for k in ('user_heroes_count', 'user_heroes_total_exp', 'user_heroes_total_levels', 'user_heroes_total_power'):
            if a.get(k) != b.get(k):
                errors.append(f'{k} mutated: {b.get(k)} -> {a.get(k)}')
        for k in ('exp', 'level', 'gold', 'diamonds', 'energy'):
            if (a.get('user') or {}).get(k) != (b.get('user') or {}).get(k):
                errors.append(f'user.{k} mutated: {(b.get("user") or {}).get(k)} -> {(a.get("user") or {}).get(k)}')
        if not errors:
            print('OK    post-preview state strictly equal to pre-preview')
    return _emit(errors, detail)


def _emit(errors, detail=None):
    print('\n' + '='*72)
    print('Pack 126 — no mutation before/after')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_NO_MUTATION_BEFORE_AFTER', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'detail': detail or {}}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_no_mutation_before_after_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  before/after invariants respected')
    return 0


def _emit_partial(errors):
    report = {'pack': 'PRE_QA_PACK_126_NO_MUTATION_BEFORE_AFTER', 'status': 'NEEDS_DEVICE_CONFIRMATION', 'errors': errors, 'note': 'after-preview snapshot pending device QA'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_no_mutation_before_after_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('NEEDS_DEVICE_CONFIRMATION (no after-preview snapshot yet)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
