# RM1.32-PRE — Catalog Baseline + Metadata Harmonization + Diff Safety Foundation

**Status:** ✅ **PASS** — Metadata-only 5★ harmonization, immutable baseline snapshot, diff-validator, opt-in suite integration. ZERO skill content / runtime / DB / Borea changes.

Covers blocks: **RM1.31-D** (5★ top-level metadata) + **RM1.32-PRE** (baseline snapshot + diff-validator + suite integration).

---

## 1. Files created

| Path | Role |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132pre_v1.json` | Immutable baseline snapshot (SHA256 of 5 tracked files + invariants) |
| `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py` | Diff-validator script (strict / `--allow-changed` / `--summary-only` modes) |
| `/app/docs/divine/36_CATALOG_BASELINE_DIFF_SAFETY_RM132PRE.md` | This checkpoint |

## 2. Files modified

| Path | Change | Scope |
|---|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json` | Added top-level `"battle_runtime_attached": false` and informational `safety_metadata_harmonization` block | **Metadata-only.** No skill content / slot / status / effect tag / `divine_weapon_id` / Borea visibility changed. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Added `--include-baseline-diff` opt-in flag | Script-only, no breaking change. Default behavior unchanged. |

No other file touched. NO DB writes. NO runtime files. NO UI. NO routes/loaders. NO Character Bible. NO assets.

## 3. Block A — 5★ Metadata Harmonization Summary

**Before** (top-level):
```json
{
  "catalog_id": "hero_skill_kits_5star_full_v1",
  "runtime_attached": false,
  "balance_values_finalized": false,
  "do_not_treat_as_live_kit": true,
  ...
}
```

**After** (top-level):
```json
{
  "catalog_id": "hero_skill_kits_5star_full_v1",
  "runtime_attached": false,
  "battle_runtime_attached": false,          // ADDED — mirrors RM1.30-A 6★
  "balance_values_finalized": false,
  "do_not_treat_as_live_kit": true,
  "safety_metadata_harmonization": {          // ADDED — informational tracking
    "task": "RM1.31-D/RM1.32-PRE",
    "applied_change": "Added top-level battle_runtime_attached=false to mirror RM1.30-A 6★ convention. NO 5★ skill content / slot / status / effect tag / divine_weapon_id / Borea visibility changed.",
    "no_skill_content_change": true,
    "no_slot_change": true,
    "no_status_or_effect_tag_change": true,
    "no_divine_weapon_id_change": true,
    "no_borea_visibility_change": true
  },
  ...
}
```

API response `GET /api/hero-skill-kits/catalogs/5star` now returns `battle_runtime_attached: False` (the route already enforced false; now the catalog data declares it too, matching the 6★ convention).

## 4. Block B — Baseline Snapshot Summary

**File:** `/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132pre_v1.json` (3.4 KB).

**Tracked files (5) with SHA256 prefixes (post-patch state):**

| File | SHA256 prefix |
|---|---|
| `hero_skill_kits_5star_full_v1.json` | `d2e30f88…` |
| `hero_skill_kits_6star_borea_v1.json` | `4172da0d…` |
| `divine_weapons_catalog_v1.json` | `e3ed42f5…` |
| `hero_skill_kit_schema_v1.json` | `f5b30b6d…` |
| `status_effect_catalog_v1.json` | `16441076…` |

**Counts recorded:** 5★=20, 6★=13, DW=13.

**Critical invariants recorded:** `/api/heroes` expected=100, greek_borea hidden, legacy borea hidden, primordial_gaia hidden, 5★ no ultimate, 6★ all ultimate, 6★ all have divine_weapon_id, final_numbers null, runtime flags false, marchio_boreale Borea-only.

**Top-level catalog flags recorded** for both 5★ and 6★: `runtime_attached=false`, `battle_runtime_attached=false`, `balance_values_finalized=false`, `do_not_treat_as_live_kit=true`.

> The baseline is **immutable** for diff detection of unauthorized changes. Future approved tasks that legitimately mutate catalogs must generate a NEW baseline (e.g. `_baseline_rm132a_v2`).

## 5. Block C — Diff Validator Behavior & Commands

**Script:** `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py`

### Modes

| Mode | Behavior |
|---|---|
| default (strict) | Recompute SHA256 of all tracked files. Fail if any checksum differs from baseline. |
| `--allow-changed <path>` (repeatable) | Allow listed files to differ without failing. Useful during approved mutation tasks. |
| `--summary-only` | Print baseline vs current checksums side-by-side. Does not fail on diff, but still fails on invariant violations. |

### Always-enforced invariants (regardless of mode)

- 5★ entries = 20, 6★ entries = 13, DW records = 13.
- Per slot (5★+6★): `final_numbers=null`, `runtime_attached!=true`, `battle_runtime_attached!=true`.
- No legacy `borea` / `primordial_gaia` / wrong alias in any catalog.
- No `marchio_boreale` leak in non-Borea 6★ entries.
- Catalog top-level `runtime_attached=false` and `battle_runtime_attached=false` for BOTH 5★ and 6★ (the RM1.31-D harmonization is enforced here).

### Sample commands

```bash
# Strict diff (default)
python3 /app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py

# Allow specific files to differ during an approved mutation task
python3 /app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py \
    --allow-changed /app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json

# Inspection-only output, never fail on diff
python3 /app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py --summary-only
```

### Result against current state

```
PASS: RM1.32-PRE — Catalog Baseline Diff Validator
  tracked files unchanged:  5/5
  Invariants:               5★=20, 6★=13, DW=13
  final_numbers / runtime flags: clean across 5★+6★ slots
  Marchio Boreale leak:     0 in non-Borea
  Forbidden hero IDs:       0 (borea / primordial_gaia / aliases)
```

## 6. Block D — Suite Runner Integration

**Script:** `/app/backend/scripts/run_hero_skill_kit_validator_suite.py`

- Added `--include-baseline-diff` opt-in flag (default OFF).
- **Default behavior preserved**: future approved mutations will not accidentally trip the suite because diff is not run by default.
- When flag is on, runs `validate_hero_skill_kit_catalog_baseline_diff.py` as a required item.
- Run with `--include-baseline-diff` → 13/13 PASS (12 standard + 1 baseline diff).
- Run without flag → 12/12 PASS (unchanged from RM1.31).

## 7. Validator / Audit Results — 13/13 PASS

```
Overall (default mode):                 PASS  (pass=12, fail=0, miss=0)
Overall (--include-baseline-diff):      PASS  (pass=13, fail=0, miss=0)
```

| Task | Script | Default | --include-baseline-diff |
|---|---|:-:|:-:|
| RM1.28-A | validate_5star_passive_advanced_source.py | ✅ | ✅ |
| RM1.28-B | audit_5star_skill_kits_crosslinks.py | ✅ | ✅ |
| RM1.28-C | audit_5star_legacy_status_tags.py | ✅ | ✅ |
| RM1.28-D | validate_5star_legacy_status_tags_normalized.py | ✅ | ✅ |
| RM1.28-E | validate_5star_manual_review_residuals_resolved.py | ✅ | ✅ |
| RM1.29 | audit_6star_skill_kits_crosslinks.py | ✅ | ✅ |
| RM1.30-A | validate_6star_catalog_safety_metadata.py | ✅ | ✅ |
| RM1.30-B | audit_6star_effect_tags_taxonomy.py | ✅ | ✅ |
| RM1.30-C | audit_hero_skill_kit_catalog_consolidation.py | ✅ | ✅ |
| RM1.27-A | validate_divine_weapon_catalog.py | ✅ | ✅ |
| RM1.27-D | audit_divine_weapon_crosslinks.py | ✅ | ✅ |
| RM1.31-C | validate_status_resolver_contract.py | ✅ | ✅ |
| **RM1.32-PRE** | **validate_hero_skill_kit_catalog_baseline_diff.py** | — | ✅ **NEW** |

## 8. CLI Safety Smoke (Block F)

| Command | Result |
|---|---|
| `summary` | ✅ now shows **5★ `battle_runtime_attached = False`** (was `<missing>`) |
| `show --hero-id borea` | ✅ REJECTED exit 3 |
| `show --hero-id greek_borea` | ✅ catalog-only flag preserved |

## 9. API Smoke Results (Block G) — 12/12

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | 200 |
| `GET /api/heroes` | 200 (count=100) | 200 |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 (catalog-only) | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | 404 |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | 404 |
| `GET /api/divine-weapons/catalogs/summary` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/borea` | 404 | 404 |

The `GET /api/hero-skill-kits/catalogs/5star` body now contains `"battle_runtime_attached": false` at the top level (sourced from the patched catalog).

## 10. UI Safety Audit (Block H)

| File | non-GET fetch | runtime-verb Pressables |
|---|---|---|
| `frontend/app/hero-skill-kits-catalog.tsx` | ❌ NONE ✅ | ❌ NONE ✅ |
| `frontend/app/divine-weapons-catalog.tsx` | ❌ NONE ✅ | ❌ NONE ✅ |

## 11. `/api/heroes` Safety Check

| Check | Result |
|---|---|
| Total heroes count | **100** ✅ (unchanged) |
| `greek_borea` visible | ❌ NOT VISIBLE ✅ |
| Legacy `borea` visible | ❌ NOT VISIBLE ✅ |
| `primordial_gaia` visible | ❌ NOT VISIBLE ✅ |

## 12. Borea Safety Confirmation

- `greek_borea` remains catalog-only / `launch_extra_premium`.
- `divine_weapon_id = borea_wings_of_the_north_wind` unchanged.
- `marchio_boreale` total occurrences = 6, all on `greek_borea`, 0 leak.
- Legacy `borea` absent from any catalog AND `/api/heroes` AND CLI (rejected by `show`/`propose-*`).
- Diff-validator additionally enforces zero Borea leak as an always-on invariant.

## 13. Runtime / DB / Gacha / Roster Safety Confirmation

ZERO modifications to:
- `backend/battle_engine.py`, `frontend/app/combat.tsx`, HP bar runtime
- status runtime, VFX runtime, Divine Weapon runtime
- gacha / summon logic
- roster / visibility logic
- MongoDB / migrations / seed
- Character Bible
- assets
- API routes/loaders (only the *suite runner script* gained a new opt-in flag)
- UI files
- `divine_weapon_id`, `release_group`, `final_numbers`
- `runtime_attached`, `battle_runtime_attached` at slot/entry level

## 14. Warnings / Discrepancies

**None blocking.**

Informational notes:
1. The 5★ catalog SHA256 changed from `f20216c0…` (pre-patch) to `d2e30f88…` (post-patch). This is **expected** and reflected in the new baseline.
2. The diff-validator default mode is intentionally **strict**. Any future approved catalog write must either (a) be explicitly allowed via `--allow-changed`, or (b) regenerate the baseline.
3. The `--include-baseline-diff` suite flag is **opt-in by design** so that an approved mutation task does not accidentally trip the suite.

## 15. Recommendation — Final Status

✅ **ACCEPT — RM1.32-PRE PASS.**

- All 26 acceptance criteria of the prompt are met.
- 5★ catalog metadata harmonized to mirror 6★ convention (RM1.31-D).
- Immutable baseline snapshot in place; diff-validator passes against current state.
- Suite runner gained safe opt-in `--include-baseline-diff` without breaking the default flow.
- `/api/heroes` count remains **100**, Borea remains hidden/catalog-only, full regression green.

## 16. Suggested Next Tasks (prioritized)

| Priority | ID | Task | Safety |
|---|---|---|---|
| 🟢 P0 | **RM1.31-E (opt)** | Write-enabled authoring CLI v0 (`--commit` + `AUTHORING_COMMIT_ALLOWED=true` env-var + `.bak` backup + post-write validator suite + auto-rollback) | HIGH (gated) |
| 🟢 P0 | **RM1.32-A pre** | Backup-and-restore helper script for `/app/backups/hero_skill_kits/` (foundation only, no use yet) | HIGHEST |
| 🟡 P1 | **RM1.32-A** | Balance Pass Foundation 5★ — design-data writes for `final_numbers` per slot, behind feature flag, NO runtime hook | MEDIUM |
| 🟠 P2 | **RM1.33-A** | Runtime Adapter Skeleton — `SKILL_KIT_RUNTIME_ENABLED=false`, battle_engine read-only adapter scaffold | LOW (full QA gate) |
| 🟢 P0 | **RM1.32-PRE-B** | Add baseline diff to a CI/pre-commit hook documentation (no runtime change) | HIGHEST |

Borea activation remains an isolated, separate task.
