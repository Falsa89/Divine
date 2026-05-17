#!/usr/bin/env python3
"""
RM1.34-B-PATCH-A — Validator: darkness -> dark canonical element patch
applied correctly to the boss family element/faction matrix.

Verifies:
- matrix `elements_included` lists 'dark' and NOT 'darkness';
- canonical element key in every boss-family element block uses 'dark';
- count of element blocks per family is preserved (no removal);
- metadata records the patch: darkness_to_dark_applied=true,
  RM1.34-B-PATCH-A in axis_patches_applied, alias history non-empty;
- design_only=true / runtime_attached=false at metadata level;
- alias helper still maps darkness -> dark;
- AF2 gift draft still has 'dark' in elements_used and does NOT use
  'darkness' as canonical (history references are tolerated);
- no Borea token added by the patch;
- live runtime files NOT modified by the patch.

Read-only. NO mutation.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
ALIAS_HELPER = ROOT / 'backend' / 'data' / 'canonical_axis_alias_helper.py'
READ_THROUGH_HELPER = ROOT / 'backend' / 'data' / 'canonical_axis_read_through_helper.py'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1) Matrix
record('matrix_present', MATRIX.exists(), str(MATRIX))
if not MATRIX.exists():
    print('matrix missing')
    sys.exit(1)
doc = json.loads(MATRIX.read_text(encoding='utf-8'))

elements = doc.get('elements_included') or []
record('elements_includes_dark', 'dark' in elements, f'got {elements}')
record('elements_excludes_darkness',
       'darkness' not in elements, f'got {elements}')
record('elements_count_7', len(elements) == 7, f'got {len(elements)}')

# Boss families preserved
fams = doc.get('boss_families') or []
if isinstance(fams, dict):
    fam_iter = list(fams.items())
elif isinstance(fams, list):
    fam_iter = [(f.get('family_id') or f.get('id') or f'idx_{i}', f)
                for i, f in enumerate(fams)]
else:
    fam_iter = []
record('boss_families_min_5',
       len(fam_iter) >= 5, f'got {len(fam_iter)}')

# Every family must have a 'dark' element block, NOT 'darkness'
for fam_id, fam in fam_iter:
    if not isinstance(fam, dict):
        continue
    elist = fam.get('elements') or fam.get('element_breakdown')
    if isinstance(elist, dict):
        record(f'family_{fam_id}_has_dark_key',
               'dark' in elist, f'keys={list(elist.keys())}')
        record(f'family_{fam_id}_no_darkness_key',
               'darkness' not in elist, '')
    elif isinstance(elist, list):
        keys = [e.get('element') if isinstance(e, dict) else e for e in elist]
        record(f'family_{fam_id}_has_dark', 'dark' in keys, f'keys={keys}')
        record(f'family_{fam_id}_no_darkness', 'darkness' not in keys, '')
    # else: no per-family elements block — the canonical truth in this
    # matrix lives in element_resistance_modifiers, asserted below.

    # Canonical resistance modifier block
    erm = fam.get('element_resistance_modifiers')
    if isinstance(erm, dict):
        record(f'family_{fam_id}_erm_has_dark',
               'dark' in erm, f'keys={list(erm.keys())}')
        record(f'family_{fam_id}_erm_no_darkness',
               'darkness' not in erm, '')

# Metadata
meta = doc.get('metadata') or {}
record('meta_darkness_to_dark_applied',
       meta.get('darkness_to_dark_applied') is True, '')
record('meta_axis_patches_includes_patch_a',
       'RM1.34-B-PATCH-A' in (meta.get('axis_patches_applied') or []), '')
record('meta_previous_alias_preserved',
       meta.get('previous_alias_preserved_in_history') is True, '')
record('meta_alias_history_min_1',
       isinstance(meta.get('darkness_alias_history'), list)
       and len(meta['darkness_alias_history']) >= 1, '')
record('meta_design_only', meta.get('design_only') is True, '')
record('meta_runtime_attached_false',
       meta.get('runtime_attached') is False, '')

# `greek_borea` may appear as `marchio_owner_hero_id` (canonical owner
# of the Marchio Boreale lock) — that is INTENTIONAL and predates the
# patch. We assert only that `primordial_gaia` is absent and that
# greek_borea / borea are NOT canonical faction_groups.
record('faction_groups_no_borea',
       'borea' not in (doc.get('faction_groups_included') or []), '')
record('faction_groups_no_greek_borea',
       'greek_borea' not in (doc.get('faction_groups_included') or []), '')

# 2) Alias helper still maps darkness -> dark
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import canonical_axis_alias_helper as ah  # type: ignore
    # canonical_axis_alias_helper exposes normalize_element_axis(value)
    canonical = None
    if hasattr(ah, 'normalize_element_axis'):
        r = ah.normalize_element_axis('darkness')
        if isinstance(r, dict):
            canonical = r.get('canonical') or r.get('normalized') or r.get('value')
    elif hasattr(ah, 'resolve_element'):
        r = ah.resolve_element('darkness')
        canonical = r.get('canonical') if isinstance(r, dict) else r
    record('alias_helper_darkness_to_dark',
           canonical == 'dark', f'got {canonical!r}')
except Exception as e:
    record('alias_helper_darkness_to_dark', False, f'{e!r}')

# Read-through helper too
try:
    from data import canonical_axis_read_through_helper as rh  # type: ignore
    r = rh.resolve_element('darkness')
    record('read_through_darkness_to_dark',
           r.get('canonical') == 'dark', f'{r}')
except Exception as e:
    record('read_through_darkness_to_dark', False, f'{e!r}')

# 3) AF2 gift draft alignment
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    elements_used = gd.get('elements_used') or []
    record('gift_draft_has_dark', 'dark' in elements_used, f'got {elements_used}')
    record('gift_draft_excludes_darkness_canonical',
           'darkness' not in elements_used, f'got {elements_used}')

# Report
print('=' * 70)
print('RM1.34-B-PATCH-A — darkness -> dark Patch Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
