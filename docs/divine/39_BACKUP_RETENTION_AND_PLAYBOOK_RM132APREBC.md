# RM1.32-A-PRE-B/C — Write Safety Playbook + Backup Retention Policy

**Status:** ✅ **PASS** — Playbook delivered, prune helper delivered, retention exercised end-to-end on dummy `/tmp` directory (real backup root untouched). ZERO catalog mutations.

---

## 1. Files Created

| Path | Role |
|---|---|
| `/app/docs/divine/38_WRITE_ENABLED_AUTHORING_CLI_SAFETY_PLAYBOOK_RM132APREB.md` | Block A — operational playbook |
| `/app/backend/scripts/prune_hero_skill_kit_backups.py` | Block B — backup retention / prune helper |
| `/app/docs/divine/39_BACKUP_RETENTION_AND_PLAYBOOK_RM132APREBC.md` | This checkpoint |

## 2. Files Modified

**None.** No catalog, schema, baseline, route, loader, UI, asset, Character Bible, DB, or runtime file was touched.

## 3. Playbook Summary (Block A)

`38_WRITE_ENABLED_AUTHORING_CLI_SAFETY_PLAYBOOK_RM132APREB.md` (11 sections):

1. When the write-enabled CLI may be used (gating conditions)
2. Preconditions checklist
3. Required environment variables: `DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE`, `DIVINE_ALLOW_CATALOG_RESTORE`, `DIVINE_ALLOW_BACKUP_PRUNE`
4. Forbidden field categories: FROZEN (`final_numbers`, `runtime_attached`, `battle_runtime_attached`) and DANGEROUS (`release_group`, `divine_weapon_id`, `hero_id`, `skill_id`, `slot`, `status_tags`, `core_status_ids`, `core_effect_tags`)
5. SAFE_AUTHORING_FIELDS allowlist
6. Write flow (13-step pipeline: validator → backup → env → commit → re-validate → API smoke → UI safety → baseline regen)
7. Rollback flow (CLI auto-rollback + manual out-of-band rollback via restore helper)
8. Borea safety rules (non-negotiable)
9. Worked examples (safe dry-run, blocked commit, frozen field rejection, restore dry-run)
10. One-shot Emergent prompt pattern for future approved write tasks
11. Companion scripts read-only summary

## 4. Retention Script Summary (Block B)

**Script:** `/app/backend/scripts/prune_hero_skill_kit_backups.py`

### Behavior
- Default DRY-RUN.
- `--keep N` (default 10).
- `--commit` requires env var `DIVINE_ALLOW_BACKUP_PRUNE=YES_I_UNDERSTAND` (rejection exit 3 otherwise).
- `--backup-root` whitelist: `/app/backups/hero_skill_kits` or `/tmp` only (rejection exit 2 otherwise).
- `--keep < 1` → rejection exit 2 (refuses to prune everything).
- Only prunes directories that look like a valid backup: name starts with `backup_`, contains a parseable `MANIFEST.json`. Skips others with a warning.
- Sorts by `manifest.created_at_utc` (falls back to directory name, then mtime).
- Extra safety: refuses to delete the newest backup even if it qualified as prune-candidate.
- Prints what would be kept/pruned. Exit 0/1/2/3.

### Smoke results

| # | Command | Result |
|---|---|---|
| B1 | `--keep 10 --dry-run` (real root) | OK — 1 backup, keep=1, prune=0 |
| B2 | `--keep 0 --commit` (real root) | **REJECTED exit 2** (keep < 1) ✅ |
| B2b | `--keep 10 --commit` no env (real root) | **REJECTED exit 3** ✅ |
| B3 | Set up dummy `/tmp/rm132bc_prune_test/` with 5 fake backup dirs | OK |
| B4 | `--keep 2 --dry-run --backup-root /tmp/rm132bc_prune_test` | OK — keep 2 newest, plan-prune 3 oldest |
| B5 | `--keep 2 --commit --backup-root /tmp/rm132bc_prune_test` no env | **REJECTED exit 3** ✅ |
| B6 | `DIVINE_ALLOW_BACKUP_PRUNE=YES_I_UNDERSTAND --keep 2 --commit --backup-root /tmp/rm132bc_prune_test` | **OK — deleted 3, kept 2** ✅ |
| B7 | post-state of `/tmp/rm132bc_prune_test` | 2 dirs remaining (newest two) ✅ |

The real backup root `/app/backups/hero_skill_kits/` was **not modified** in this task (it contains only 1 backup, well under the `keep=10` threshold).

## 5. Restore Drill Results (Block C)

Latest manifest: `/app/backups/hero_skill_kits/backup_20260515T180215Z/MANIFEST.json`

| # | Command | Result |
|---|---|---|
| C1 | `restore_hero_skill_kit_catalogs.py --manifest <latest> --dry-run` | OK — integrity verified, 5/5 SHA256 match, no files restored |
| C2 | `restore_hero_skill_kit_catalogs.py --manifest <latest> --commit` no env | **REJECTED exit 3** ✅ |

No commit-restore was performed.

## 6. CLI Smoke Results (Block D)

| # | Command | Result |
|---|---|---|
| D-CLI-1 | CLI `summary` | OK (5★=20, 6★=13, DW=13, safety flags False) |
| D-CLI-2 | CLI `show --hero-id borea` | REJECTED exit 3 ✅ |
| D-CLI-3 | CLI `propose-update-field authoring_notes --dry-run` | OK no write |
| D-CLI-4 | CLI `propose-update-field authoring_notes --commit` no env | REJECTED exit 10 ✅ |
| D-CLI-5 | CLI `propose-update-field final_numbers --commit` | REJECTED exit 7 (FROZEN) ✅ |

## 7. Validator / Suite / Baseline Results

```
Suite default:                 PASS  (pass=12, fail=0, miss=0)
Suite --include-baseline-diff: PASS  (pass=13, fail=0, miss=0)
Baseline diff direct:          PASS  (5/5 tracked files unchanged)
```

Catalog SHA256 prefixes (unchanged):
- 5★ `d2e30f88…`
- 6★ `4172da0d…`
- DW `e3ed42f5…`

## 8. API Smoke Results (Block E) — 12/12

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | 200 |
| `GET /api/heroes` | 200 (count=100) | 200 |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | 404 |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | 404 |
| `GET /api/divine-weapons/catalogs/summary` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/borea` | 404 | 404 |

## 9. UI Safety Audit (Block F)

| File | non-GET fetch | runtime-verb Pressables |
|---|---|---|
| `frontend/app/hero-skill-kits-catalog.tsx` | ❌ NONE | ❌ NONE |
| `frontend/app/divine-weapons-catalog.tsx` | ❌ NONE | ❌ NONE |

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
- No Borea visibility flip.

## 12. Runtime / DB / Gacha / Roster / Catalog Safety Confirmation

ZERO modifications to:
- catalog data (3 SHA256 unchanged)
- `battle_engine.py`, `combat.tsx`, HP bar / status / VFX / Divine Weapon runtime
- gacha / summon / roster / visibility logic
- MongoDB / migrations / seed
- Character Bible / assets
- API routes / loaders / UI files
- `divine_weapon_id`, `release_group`, `final_numbers`
- `runtime_attached`, `battle_runtime_attached` flags

Only changes to disk: `38_…PLAYBOOK…md`, `prune_hero_skill_kit_backups.py`, and this checkpoint. Dummy `/tmp/rm132bc_prune_test/` was used and partially deleted as part of the commit-prune end-to-end test (intentional, isolated to /tmp).

## 13. Backup Directory State

```
/app/backups/hero_skill_kits/
└── backup_20260515T180215Z/      (unchanged from RM1.32-A-PRE)
    ├── MANIFEST.json
    ├── hero_skill_kits_5star_full_v1.json
    ├── hero_skill_kits_6star_borea_v1.json
    ├── divine_weapons_catalog_v1.json
    ├── hero_skill_kit_schema_v1.json
    └── hero_skill_kit_catalog_baseline_rm132pre_v1.json
```

1 real backup directory present. With `keep=10` the retention policy would prune **0** real backups.

## 14. Warnings / Discrepancies

**None blocking.**

Informational:
1. The prune commit path was exercised **only against dummy `/tmp/rm132bc_prune_test/`** dirs. The real backup root has 1 dir and is not affected by the default `keep=10` policy.
2. The playbook is binding only when an explicit, scoped catalog-write task arrives. Until then, the foundation stays in dry-run / commit-skeleton mode (STEP 2/4 still no-op in CLI).
3. `/tmp/rm132bc_prune_test/` was deliberately left in place with its 2 newest dummy dirs; it can be cleaned up at any time without consequence.

## 15. Recommendation — Final Status

✅ **ACCEPT — RM1.32-A-PRE-B/C PASS.**

- All acceptance criteria are met.
- Operational playbook published.
- Backup retention helper delivered and verified end-to-end (dry-run + rejection + env-gated commit on dummy dirs).
- Real catalogs, baseline, and backups unchanged.
- Full regression suite green; `/api/heroes` = 100; Borea remains hidden.

## 16. Suggested Next Tasks (prioritized)

| Priority | ID | Task | Safety |
|---|---|---|---|
| 🟢 P0 | **RM1.31-F (opt)** | Real STEP 2/4 implementation: actual safe write of SAFE_AUTHORING_FIELDS in a single approved test (e.g. add `authoring_notes` to one hero), with full backup → write → validator → rollback exercised. Strictly opt-in. | HIGH (gated) |
| 🟢 P0 | **RM1.32-A-PRE-D (opt)** | Add a `--json-out` flag to `prune_hero_skill_kit_backups.py` for CI consumption. | HIGHEST |
| 🟢 P0 | **RM1.32-A-PRE-E (opt)** | Schedule documentation (cron / pre-commit example) for periodic backup + prune. Documentation only, no service install. | HIGHEST |
| 🟡 P1 | **RM1.32-A** | Balance Pass Foundation 5★ — design-data writes for `final_numbers` per slot, behind feature flag, NOT runtime-hooked. Requires its own dedicated baseline regeneration. | MEDIUM |
| 🟠 P2 | **RM1.33-A** | Runtime Adapter Skeleton — `SKILL_KIT_RUNTIME_ENABLED=false`, battle_engine read-only adapter scaffold. Requires full QA before any flag flip. | LOW (full QA gate) |

Borea activation remains an isolated, separate task.
