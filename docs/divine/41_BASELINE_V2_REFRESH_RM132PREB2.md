# RM1.32-PRE-B2 — Refresh Baseline v2 post-RM1.31-F Approved Safe Write

**Status:** ✅ **PASS** — Baseline v2 created, v1 preserved as historical anchor, diff-validator auto-detects latest, suite `--include-baseline-diff` now passes without `--allow-changed`. ZERO catalog/runtime/DB changes.

---

## 1. Files Created

| Path | Role |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132preb2_v2.json` | NEW baseline anchor (post-RM1.31-F approved state) |
| `/app/docs/divine/41_BASELINE_V2_REFRESH_RM132PREB2.md` | This checkpoint |

## 2. Files Modified

| Path | Change |
|---|---|
| `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py` | Added `find_latest_baseline()` helper; `--baseline` now defaults to auto-detected latest baseline by `generated_at_utc` timestamp |

No catalog data was modified. The historical baseline v1 file is **preserved** at:
`/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132pre_v1.json` (untouched).

## 3. Baseline v2 Summary

- **baseline_id**: `hero_skill_kit_catalog_baseline_rm132preb2_v2`
- **task_origin**: `RM1.32-PRE-B2`
- **supersedes**: `hero_skill_kit_catalog_baseline_rm132pre_v1`
- **generated_at_utc**: `2026-05-15T20:09:..Z` (latest)
- **purpose**: anchored on the approved post-RM1.31-F state where the 5★ catalog contains the safe-write `authoring_notes` on `greek_atalanta.skill_1`.

### Tracked files (5) with current SHA256 (post-RM1.31-F)

| File | SHA256 prefix | Note |
|---|---|---|
| `hero_skill_kits_5star_full_v1.json` | `fc87088e…` | **CHANGED** vs v1 (`d2e30f88…`), reflecting the approved RM1.31-F write |
| `hero_skill_kits_6star_borea_v1.json` | `4172da0d…` | unchanged |
| `divine_weapons_catalog_v1.json` | `e3ed42f5…` | unchanged |
| `hero_skill_kit_schema_v1.json` | `f5b30b6d…` | unchanged |
| `status_effect_catalog_v1.json` | `16441076…` | unchanged |

### Approved changes since v1 (recorded inside the v2 file)

```json
"approved_changes_since_v1": [
  {
    "task": "RM1.31-F",
    "file": ".../hero_skill_kits_5star_full_v1.json",
    "change_kind": "safe_authoring_field_write",
    "hero_id": "greek_atalanta",
    "slot": "skill_1",
    "field": "authoring_notes",
    "value_kind": "str",
    "value_preview": "RM1.31-F safe write test: authoring pipeline verified; no gameplay/runtime effect.",
    "also_added": "top-level last_safe_write provenance block (descriptive metadata only)"
  }
]
```

### Critical invariants recorded

`/api/heroes` expected=100, greek_borea hidden, legacy borea hidden, primordial_gaia hidden, 5★ no ultimate, 6★ all ultimate, 6★ all have divine_weapon_id, final_numbers null, runtime flags false, marchio_boreale Borea-only.

## 4. Diff-Validator Update Summary

- New helper `find_latest_baseline()` scans `/app/data/design/hero_skill_kits/` for files matching `hero_skill_kit_catalog_baseline_*.json`, picks the one with the highest `generated_at_utc` (falls back to lexically-greatest filename).
- `--baseline` argument now defaults to **None**; when omitted, the validator emits an informational line:
  ```
  i auto-detected latest baseline: hero_skill_kit_catalog_baseline_rm132preb2_v2.json
  ```
  and uses v2.
- Explicit `--baseline <path>` continues to work for v1 strict comparison or any other anchor.
- All other modes (`--summary-only`, `--allow-changed`) work identically with either baseline.

### Behavior matrix

| Invocation | Baseline used | Result |
|---|---|---|
| `validate_hero_skill_kit_catalog_baseline_diff.py` (no flag) | v2 (auto-latest) | PASS (5/5 unchanged) |
| `... --baseline <v2-path>` | v2 explicit | PASS (5/5 unchanged) |
| `... --baseline <v1-path>` | v1 strict | **FAIL** on 5★ checksum (expected — exit 1) |
| `... --baseline <v1-path> --allow-changed <5★>` | v1 + allow | PASS (4 unchanged + 1 allow-changed) |
| `... --baseline <v1-path> --summary-only` | v1 summary | PASS — shows `[DIFF] 5★` vs v1, `[same]` for the rest, no fail on diff |

## 5. Suite Runner Update Summary

No code change to `run_hero_skill_kit_validator_suite.py` was needed. The opt-in flag `--include-baseline-diff` invokes `validate_hero_skill_kit_catalog_baseline_diff.py` without arguments, which now auto-selects v2 and passes cleanly.

| Suite invocation | Result |
|---|---|
| `run_hero_skill_kit_validator_suite.py` (default) | PASS 12/12 |
| `run_hero_skill_kit_validator_suite.py --include-baseline-diff` | **PASS 13/13** (no `--allow-changed` needed) ✅ |

## 6. Validator / Baseline Results

| Run | Baseline | Result |
|---|---|---|
| diff-validator default | v2 (auto) | PASS — 5/5 unchanged |
| diff-validator `--baseline v2` | v2 | PASS — 5/5 unchanged |
| diff-validator `--baseline v1` strict | v1 | FAIL on 5★ (expected) — exit 1 |
| diff-validator `--baseline v1 --allow-changed <5★>` | v1 + allow | PASS — 4 unchanged + 1 allow-changed |
| diff-validator `--baseline v1 --summary-only` | v1 summary | Prints `[DIFF] 5★`, `[same]` 6★/DW/schema/baseline — no fail |
| suite default | n/a | PASS 12/12 |
| suite `--include-baseline-diff` | v2 (auto) | PASS 13/13 |

## 7. CLI Smoke Results

| Command | Result |
|---|---|
| `propose-update-field authoring_notes --commit` no env | REJECTED exit 10 ✅ |
| `show --hero-id borea` | REJECTED exit 3 ✅ |
| `show --hero-id greek_borea` | OK, "⚠ CATALOG-ONLY" flag preserved |

## 8. API Smoke Results — 12/12

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | 200 |
| `GET /api/heroes` | 200 (count=100) | 200 |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 | 200 (still exposes `authoring_notes`) |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | 404 |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | 404 |
| `GET /api/divine-weapons/catalogs/summary` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/borea` | 404 | 404 |

## 9. UI Safety Audit

| File | non-GET fetch | runtime-verb Pressables |
|---|---|---|
| `frontend/app/hero-skill-kits-catalog.tsx` | NONE ✅ | NONE ✅ |
| `frontend/app/divine-weapons-catalog.tsx` | NONE ✅ | NONE ✅ |

## 10. `/api/heroes` Safety Check

| Check | Result |
|---|---|
| Total heroes count | **100** ✅ (unchanged) |
| `greek_borea` visible | ❌ NOT VISIBLE ✅ |
| Legacy `borea` visible | ❌ NOT VISIBLE ✅ |
| `primordial_gaia` visible | ❌ NOT VISIBLE ✅ |

## 11. Borea Safety Confirmation

- `greek_borea` catalog-only / launch_extra_premium / `divine_weapon_id` preserved.
- Legacy `borea` forbidden in CLI and absent from API.
- `marchio_boreale` Borea-only (6 occurrences, 0 leaks).
- No Borea visibility flip in this task.

## 12. Runtime / DB / Gacha / Roster / Catalog Safety

ZERO modifications to:
- catalog data (5★ `fc87088e…` unchanged since RM1.31-F; 6★ `4172da0d…`, DW `e3ed42f5…` unchanged since RM1.30-A)
- `battle_engine.py`, `combat.tsx`, HP bar / status / VFX / Divine Weapon runtime
- gacha / summon / roster / visibility logic
- MongoDB / migrations / seed
- Character Bible / assets
- API routes / loaders / UI files
- `divine_weapon_id`, `release_group`, `final_numbers`
- `runtime_attached`, `battle_runtime_attached` flags
- baseline v1 file (preserved, untouched)

Only changes to disk: new baseline v2 JSON, diff-validator script update, this checkpoint doc.

## 13. Warnings / Discrepancies

**None blocking.**

Informational:
1. Baseline v1 is intentionally preserved as a historical anchor. Future approved tasks may continue to reference v1 for archival diffs (e.g. via `--summary-only`).
2. The auto-detect rule prefers the highest `generated_at_utc`. If a hand-edited or back-dated baseline ever appears, lexical/timestamp fallback applies.
3. The 5★ change vs v1 (`d2e30f88…` → `fc87088e…`) is approved and tracked in `approved_changes_since_v1` inside v2; it represents the single RM1.31-F safe write only.

## 14. Recommendation — Final Status

✅ **ACCEPT — RM1.32-PRE-B2 PASS.**

- All acceptance criteria met.
- Baseline v2 is the new approved anchor. v1 remains preserved.
- Diff-validator auto-detects v2 by default and supports explicit `--baseline <v1>` for historical comparison.
- Suite runner `--include-baseline-diff` now passes cleanly without `--allow-changed`.
- ZERO catalog/runtime/DB changes; `/api/heroes` count remains 100; Borea remains hidden.

## 15. Suggested Next Tasks (prioritized)

| Priority | ID | Task | Safety |
|---|---|---|---|
| 🟢 P0 | **RM1.31-F-B (opt)** | Negative-rollback drill: force a validator-failing edit on a `/tmp` catalog clone to exercise STEP 4/4 auto-rollback end-to-end. | HIGHEST |
| 🟢 P0 | **RM1.32-A-PRE-D (opt)** | Add `--json-out` flag to `prune_hero_skill_kit_backups.py` for CI consumption. | HIGHEST |
| 🟢 P0 | **RM1.32-PRE-B3 (opt)** | Add a small `list-baselines` helper to the diff-validator that prints all detected baselines with their `generated_at_utc` and tracked counts. | HIGHEST |
| 🟡 P1 | **RM1.32-A** | Balance Pass Foundation 5★ — design-data writes for `final_numbers` per slot, behind feature flag, NOT runtime-hooked. Requires its own dedicated baseline v3 regeneration. | MEDIUM |
| 🟠 P2 | **RM1.33-A** | Runtime Adapter Skeleton — `SKILL_KIT_RUNTIME_ENABLED=false`, battle_engine read-only adapter scaffold. Full QA gate. | LOW |

Borea activation remains an isolated, separate task.
