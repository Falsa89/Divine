# RM1.32-A-PRE — Backup + Restore + Write-Enabled CLI Foundation

**Status:** ✅ **PASS** — Safe write foundation delivered. ZERO catalog mutations performed. All gates verified active.

---

## 1. Files Created

| Path | Role |
|---|---|
| `/app/backend/scripts/backup_hero_skill_kit_catalogs.py` | Block A — timestamped backup helper + MANIFEST.json |
| `/app/backend/scripts/restore_hero_skill_kit_catalogs.py` | Block B — restore helper with env-gated `--commit` and auto-rollback |
| `/app/docs/divine/37_BACKUP_RESTORE_WRITE_CLI_FOUNDATION_RM132APRE.md` | This checkpoint |
| **Backup files** | `/app/backups/hero_skill_kits/backup_20260515T180215Z/*` (5 catalog files + `MANIFEST.json`) |

## 2. Files Modified

| Path | Change |
|---|---|
| `/app/backend/scripts/hero_skill_kit_authoring_cli.py` | Block C — added guarded `--commit` skeleton, env-var gate, frozen/dangerous field gates, auto-backup hook, validator-after-write hook description, rollback-on-failure description |

No catalog data file was modified. No runtime / DB / API / UI file was modified.

## 3. Backup Helper Summary (Block A)

**Script:** `/app/backend/scripts/backup_hero_skill_kit_catalogs.py`

### Behavior
- Backs up 5 catalog files into `/app/backups/hero_skill_kits/backup_<UTC-timestamp>/`:
  1. `hero_skill_kits_5star_full_v1.json`
  2. `hero_skill_kits_6star_borea_v1.json`
  3. `divine_weapons_catalog_v1.json`
  4. `hero_skill_kit_schema_v1.json`
  5. `hero_skill_kit_catalog_baseline_rm132pre_v1.json`
- Writes `MANIFEST.json` with backup_id, created_at_utc, source_path, backup_path, sha256, size_bytes for each file, plus task/reason.
- Verifies post-copy SHA256 matches source SHA256 (fail-fast on copy corruption).
- Flags: `--dry-run`, `--reason <text>`, `--out-dir <path>` (restricted to `/app/backups/hero_skill_kits` or `/tmp`; rejects anywhere else with exit 2).
- Prints `BACKUP_MANIFEST_PATH=<path>` line on real run (machine-grepable).

### Smoke results
- `--dry-run --reason RM1.32-A-PRE` → **OK** (5 files planned, no write).
- Real run `--reason RM1.32-A-PRE` → **OK**, manifest at:
  `/app/backups/hero_skill_kits/backup_20260515T180215Z/MANIFEST.json` (2099 bytes).

## 4. Restore Helper Summary (Block B)

**Script:** `/app/backend/scripts/restore_hero_skill_kit_catalogs.py`

### Behavior
- Input: `--manifest <path>` (must be under `/app/backups/hero_skill_kits` or `/tmp`).
- Default mode: `--dry-run` (no writes).
- `--commit` requires env var **`DIVINE_ALLOW_CATALOG_RESTORE=YES_I_UNDERSTAND`** (rejection exit 3 otherwise).
- On `--commit`:
  1. Verify every backup file's SHA256 matches the manifest.
  2. Run `backup_hero_skill_kit_catalogs.py --reason pre_restore_RM1.32-A-PRE` → pre-restore safety net.
  3. Copy backup files over source paths.
  4. Run `run_hero_skill_kit_validator_suite.py --include-baseline-diff`.
  5. If validator fails → AUTO-ROLLBACK by restoring from the pre-restore manifest.
- **For RM1.32-A-PRE, this helper was exercised only in `--dry-run` and in `--commit WITHOUT env var` (rejection path).** No real restore was performed.

### Smoke results
- `--manifest <path> --dry-run` → **OK** (5 files, integrity verified, no write).
- `--manifest <path> --commit` (no env var set) → **REJECTED exit 3** as expected.

## 5. Authoring CLI Write Foundation Summary (Block C)

**Script:** `/app/backend/scripts/hero_skill_kit_authoring_cli.py` (`propose-update-field` command).

### Field categorization
| Class | Examples | Outcome on `--commit` |
|---|---|---|
| **FROZEN** | `final_numbers`, `runtime_attached`, `battle_runtime_attached` | exit 7 — always rejected |
| **DANGEROUS** | `release_group`, `divine_weapon_id`, `hero_id`, `skill_id`, `slot`, `status_tags`, `core_status_ids`, `core_effect_tags` | exit 9 — always rejected at foundation stage |
| **SAFE_AUTHORING_FIELDS** | `notes`, `design_notes`, `authoring_notes`, `todo`, `todo_metadata`, `comment`, `design_comment` | gated by env var + auto-backup |
| any other | e.g. typo | rejected on commit (exit 11) |

### `--commit` flow (guarded skeleton)
1. Print mandatory warning that commit path is a guarded skeleton in RM1.32-A-PRE.
2. Check env var **`DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE=YES_I_UNDERSTAND`**; reject (exit 10) otherwise.
3. Reject if field is FROZEN (exit 7) or DANGEROUS (exit 9).
4. Reject if field is not in SAFE_AUTHORING_FIELDS allowlist (exit 11).
5. STEP 1/4: invoke `backup_hero_skill_kit_catalogs.py --reason cli_commit_RM1.32-A-PRE` (real backup).
6. STEP 2/4: WOULD WRITE — **intentionally skipped** in this task. The skeleton ends here.
7. STEP 3/4: WOULD RUN `run_hero_skill_kit_validator_suite.py --include-baseline-diff`.
8. STEP 4/4: WOULD AUTO-ROLLBACK to the pre-write backup if any validator fails.

Read-only and dry-run subcommands (`summary`, `list`, `show`, `validate-dry-run`, `propose-add-slot --dry-run`, `export-report`) continue to behave exactly as in RM1.31-A.

## 6. Commands Run & Results

| # | Command | Result |
|---|---|---|
| B1 | `backup_hero_skill_kit_catalogs.py --dry-run --reason RM1.32-A-PRE` | OK (5 files planned) |
| B2 | `backup_hero_skill_kit_catalogs.py --reason RM1.32-A-PRE` | OK — manifest `/app/backups/hero_skill_kits/backup_20260515T180215Z/MANIFEST.json` |
| B3 | `restore_hero_skill_kit_catalogs.py --manifest <m> --dry-run` | OK (integrity verified, no write) |
| B4 | `restore_hero_skill_kit_catalogs.py --manifest <m> --commit` (no env) | **REJECTED exit 3** ✅ |
| C1 | CLI `summary` | OK (5★ 20, 6★ 13, DW 13, all safety flags False) |
| C2 | CLI `show --hero-id borea` | **REJECTED exit 3** ✅ |
| C3 | CLI `show --hero-id greek_borea` | OK (catalog-only flag) |
| C4 | CLI `propose-update-field authoring_notes --dry-run` | OK (no write) |
| C5 | CLI `propose-update-field authoring_notes --commit` (no env) | **REJECTED exit 10** ✅ |
| C6 | CLI `propose-update-field final_numbers --commit` | **REJECTED exit 7** ✅ (FROZEN) |
| C7 | CLI `propose-update-field core_status_ids --commit` | **REJECTED exit 9** ✅ (DANGEROUS) |
| D1 | suite default | **PASS 12/12** |
| D2 | suite `--include-baseline-diff` | **PASS 13/13** |
| D3 | baseline diff direct | **PASS** (5/5 tracked unchanged) |

## 7. Validator / Suite / Baseline Results

```
default mode:                  PASS  (pass=12, fail=0, miss=0)
--include-baseline-diff:       PASS  (pass=13, fail=0, miss=0)
baseline diff direct:          PASS  (5/5 tracked files unchanged)
```

Tracked catalog SHA256 prefixes unchanged after this task:
- 5★ `d2e30f88…`
- 6★ `4172da0d…`
- DW `e3ed42f5…`
- schema `f5b30b6d…`
- baseline `f75d20aa…`

## 8. API Smoke Results — 12/12

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | 200 ✅ |
| `GET /api/heroes` | 200 (count=100) | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | 404 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | 404 ✅ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | 200 ✅ |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | 200 ✅ |
| `GET /api/divine-weapons/catalogs/by-hero/borea` | 404 | 404 ✅ |

## 9. UI Safety Audit

| File | non-GET fetch | runtime-verb Pressables |
|---|---|---|
| `frontend/app/hero-skill-kits-catalog.tsx` | ❌ NONE ✅ | ❌ NONE ✅ |
| `frontend/app/divine-weapons-catalog.tsx` | ❌ NONE ✅ | ❌ NONE ✅ |

Descriptive false-positives (no-op): `ultimate` x3, `borea` x1+12, `divine weapon` x1, `attiva` x2 (label, not button).

## 10. `/api/heroes` Safety Check

| Check | Result |
|---|---|
| Total heroes count | **100** ✅ (unchanged) |
| `greek_borea` visible | ❌ NOT VISIBLE ✅ |
| Legacy `borea` visible | ❌ NOT VISIBLE ✅ |
| `primordial_gaia` visible | ❌ NOT VISIBLE ✅ |

## 11. Borea Safety Confirmation

- `greek_borea` remains **catalog-only / launch_extra_premium / hidden** from `/api/heroes`/gacha/roster/runtime.
- Legacy `borea` continues to be **forbidden** in CLI and absent from API.
- `marchio_boreale` total occurrences = 6, all on `greek_borea`, **0 leak**.
- `divine_weapon_id = borea_wings_of_the_north_wind` unchanged.

## 12. Runtime / DB / Gacha / Roster / Catalog Safety Confirmation

ZERO modifications to:
- catalog data files (SHA256 unchanged for 5★, 6★, DW, schema, baseline)
- `battle_engine.py`, `combat.tsx`, HP bar runtime, status runtime, VFX runtime, Divine Weapon runtime
- gacha / summon / roster / visibility logic
- MongoDB / migrations / seed
- Character Bible / assets
- API routes / loaders / UI files
- `divine_weapon_id`, `release_group`, `final_numbers`
- `runtime_attached`, `battle_runtime_attached` at slot or entry level
- 5★ top-level flags (unchanged since RM1.32-PRE)
- Borea visibility

Only changes to disk: scripts under `/app/backend/scripts/`, doc under `/app/docs/divine/`, and the new backup directory under `/app/backups/hero_skill_kits/`. None of these touch catalog data or runtime.

## 13. Backup Manifest Path(s)

| Backup ID | Manifest path |
|---|---|
| `backup_20260515T180215Z` | `/app/backups/hero_skill_kits/backup_20260515T180215Z/MANIFEST.json` (2099 bytes) |

Files in backup: 5 (5★ catalog, 6★ catalog, DW catalog, schema, baseline). Each verified by SHA256 post-copy.

## 14. Warnings / Discrepancies

**None blocking.**

Informational:
1. The CLI `--commit` path is intentionally a **guarded skeleton** in RM1.32-A-PRE: even when both the env var is set AND a SAFE_AUTHORING_FIELD is targeted, STEP 2/4 (the actual write) is a deliberate no-op. The real write logic is deferred to a future, explicitly-approved task.
2. The restore helper's `--commit` path is fully implemented but was NOT exercised in this task (only the rejection path was). Real restore will be exercised in a future approved scenario.
3. The new backup directory `/app/backups/hero_skill_kits/backup_20260515T180215Z/` contains copies of the catalogs but does NOT count as a catalog mutation: the originals are untouched (verified by post-task SHA256 comparison against the RM1.32-PRE baseline).

## 15. Recommendation — Final Status

✅ **ACCEPT — RM1.32-A-PRE PASS.**

- All 32 acceptance criteria of the prompt are met.
- Safe-write foundation (backup + restore + guarded CLI commit) in place.
- All gates (env var, FROZEN, DANGEROUS, allowlist) verified active via end-to-end smoke.
- ZERO catalog mutation; full regression suite green; `/api/heroes` count unchanged at 100; Borea remains hidden.

## 16. Suggested Next Tasks (prioritized by safety/value)

| Priority | ID | Task | Safety |
|---|---|---|---|
| 🟢 P0 | **RM1.32-A-PRE-B (opt)** | Documentation / playbook: "How to safely use the write-enabled CLI when an approved task arrives" — pre-commit checklist, env-var procedures, manifest hygiene. | HIGHEST |
| 🟢 P0 | **RM1.32-A-PRE-C (opt)** | Backup retention policy script (keep N most-recent backups under `/app/backups/hero_skill_kits/`, prune older) — read-only directory management. | HIGHEST |
| 🟢 P0 | **RM1.31-F (opt)** | Implement STEP 2/4 of the CLI commit path: real safe write for SAFE_AUTHORING_FIELDS only, with backup→write→validator→rollback fully exercised on a single test field. Strictly opt-in, requires explicit user approval. | HIGH (gated) |
| 🟡 P1 | **RM1.32-A** | Balance Pass Foundation 5★ — design-data writes for `final_numbers` per slot, BEHIND feature flag, NOT runtime-hooked. Requires its own dedicated baseline regeneration. | MEDIUM |
| 🟠 P2 | **RM1.33-A** | Runtime Adapter Skeleton — `SKILL_KIT_RUNTIME_ENABLED=false`, battle_engine read-only adapter scaffold. Requires full QA before any flag flip. | LOW (full QA gate) |

Borea activation remains an isolated, separate task.
