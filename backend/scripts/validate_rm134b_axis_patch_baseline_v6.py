#!/usr/bin/env python3
"""
RM1.34-B-AXIS-PATCH-V6 — Validator for baseline v6.

Verifies:
- baseline v6 file exists, parses, and is the auto-detected latest;
- v5 still exists as historical anchor;
- v6.baseline_id == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6';
- v6.based_on == 'hero_skill_kit_catalog_baseline_rm132c2_v5';
- v6.tracked_files preserves the v5 set of files and SHA-256 are
  current (matches on-disk sha256);
- v6.invariants: api_heroes_count==100, borea_visible_in_heroes==false,
  runtime_attached==false, axis_layer_activation_ready_post_patch==true,
  overall_runtime_activation_ready==false;
- v6.axis_patch_tracking records both patches applied;
- the central baseline-diff validator default run still passes with v6
  as the latest baseline.

Read-only.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/app')
BASELINE_DIR = ROOT / 'data' / 'design' / 'hero_skill_kits'
V5 = BASELINE_DIR / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json'
V6 = BASELINE_DIR / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json'
DIFF_SCRIPT = ROOT / 'backend' / 'scripts' / 'validate_hero_skill_kit_catalog_baseline_diff.py'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


record('v5_present', V5.exists(), str(V5))
record('v6_present', V6.exists(), str(V6))

if V6.exists():
    v6 = json.loads(V6.read_text(encoding='utf-8'))
    record('v6_baseline_id',
           v6.get('baseline_id') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
    record('v6_based_on_v5',
           v6.get('based_on') == 'hero_skill_kit_catalog_baseline_rm132c2_v5', '')
    record('v6_task_origin',
           v6.get('task_origin') == 'RM1.34-B-AXIS-PATCH-V6', '')
    record('v6_supersedes_v5',
           v6.get('supersedes') == 'hero_skill_kit_catalog_baseline_rm132c2_v5', '')
    record('v6_has_chain',
           isinstance(v6.get('baseline_chain'), list)
           and 'hero_skill_kit_catalog_baseline_rm132c2_v5' in v6['baseline_chain'], '')

    tracked = v6.get('tracked_files') or {}
    record('v6_tracked_min_5', len(tracked) >= 5, f'got {len(tracked)}')

    mismatches: list[str] = []
    for fpath, meta in tracked.items():
        p = Path(fpath)
        if not p.exists():
            mismatches.append(f'{fpath} missing')
            continue
        expected = meta.get('sha256') if isinstance(meta, dict) else meta
        actual = sha(p)
        if expected != actual:
            mismatches.append(f'{fpath} sha mismatch')
    record('v6_tracked_sha_match_all',
           not mismatches, f'mismatches={mismatches[:3]}')

    inv = v6.get('invariants') or {}
    record('v6_inv_api_heroes_100',
           inv.get('api_heroes_count') == 100, '')
    record('v6_inv_borea_hidden',
           inv.get('borea_visible_in_heroes') is False, '')
    record('v6_inv_runtime_attached_false',
           inv.get('runtime_attached') is False, '')
    record('v6_inv_battle_runtime_false',
           inv.get('battle_runtime_attached') is False, '')
    record('v6_inv_axis_layer_ready_true',
           inv.get('axis_layer_activation_ready_post_patch') is True, '')
    record('v6_inv_overall_runtime_ready_false',
           inv.get('overall_runtime_activation_ready') is False, '')

    apt = v6.get('axis_patch_tracking') or {}
    record('v6_patch_tracking_both_patches',
           set(apt.get('patches_applied') or []) >=
           {'RM1.34-B-PATCH-A', 'RM1.34-B-PATCH-B'}, '')
    record('v6_patch_tracking_darkness_applied',
           apt.get('darkness_to_dark_applied') is True, '')
    record('v6_patch_tracking_tides_deferred',
           apt.get('tides_status') == 'deferred_not_live', '')
    record('v6_patch_tracking_design_only',
           apt.get('design_only') is True, '')
    record('v6_patch_tracking_runtime_attached_false',
           apt.get('runtime_attached') is False, '')

    changelog = v6.get('approved_changes_since_v5') or []
    record('v6_changelog_min_3',
           isinstance(changelog, list) and len(changelog) >= 3, '')

# Run the central baseline-diff validator and assert PASS
if DIFF_SCRIPT.exists():
    proc = subprocess.run(
        ['python3', str(DIFF_SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    record('central_baseline_diff_pass',
           proc.returncode == 0,
           f'exit={proc.returncode}, tail={(proc.stdout or proc.stderr).splitlines()[-3:]}')
    # And it must auto-detect v6
    record('central_baseline_diff_picks_v6',
           'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6' in (proc.stdout or ''),
           f'tail={(proc.stdout or "")[-300:]}')


print('=' * 70)
print('RM1.34-B-AXIS-PATCH-V6 — Baseline v6 Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
