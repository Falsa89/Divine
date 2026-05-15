# RM1.32-A-PRE-B — Write-Enabled Authoring CLI Safety Playbook

**Audience:** Future maintainers running an approved catalog-write task.
**Scope:** Hero Skill Kit / Divine Weapon catalogs.
**Status:** Operational playbook (read-only document). Does NOT authorize any specific write task — each write task must come with its own scoped approval.

---

## 1. When the write-enabled CLI MAY be used

Only when ALL of the following are true:

1. There is an **explicit, scoped task approval** (an Emergent prompt or written instruction) naming:
   - the file(s) to change,
   - the field(s) to change,
   - the expected before/after values.
2. The target field is in **SAFE_AUTHORING_FIELDS** (see §6).
3. The user has been informed that the catalog will mutate.
4. A backup has been created **before** the write.
5. The validator suite is green **before** the write and is rerun **after**.
6. The baseline diff is regenerated only when the change is authorized.

If any item is missing, do NOT use the commit path.

## 2. Required preconditions (checklist)

```
[ ] Approved task prompt clearly references the catalog file path(s).
[ ] Approved task lists the exact field(s) to change.
[ ] Field is in SAFE_AUTHORING_FIELDS.
[ ] Pre-write backup created and BACKUP_MANIFEST_PATH captured.
[ ] Validator suite PASS before any write.
[ ] Borea visibility unchanged.
[ ] /api/heroes count = 100 prior to write.
[ ] No runtime/DB changes in scope.
```

## 3. Required environment variables

| Operation | Env var | Required value |
|---|---|---|
| CLI commit (`propose-update-field --commit`) | `DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE` | `YES_I_UNDERSTAND` |
| Restore commit (`restore_hero_skill_kit_catalogs.py --commit`) | `DIVINE_ALLOW_CATALOG_RESTORE` | `YES_I_UNDERSTAND` |
| Backup prune commit (`prune_hero_skill_kit_backups.py --commit`) | `DIVINE_ALLOW_BACKUP_PRUNE` | `YES_I_UNDERSTAND` |

Without the env var the corresponding `--commit` operation is rejected with a clear exit code (3 / 10 / 3 respectively).

## 4. Forbidden field categories

### FROZEN (always rejected, exit 7)

These will only be modified by a future runtime/balance task with its own dedicated approval and pipeline. The current CLI rejects them unconditionally:

- `final_numbers`
- `runtime_attached`
- `battle_runtime_attached`

### DANGEROUS (always rejected at foundation stage, exit 9)

These cannot be edited via the foundation CLI. A change must come through a dedicated, schema-aware task:

- `release_group`
- `divine_weapon_id`
- `hero_id`
- `skill_id`
- `slot`
- `status_tags`
- `core_status_ids`
- `core_effect_tags`

### Anything not in SAFE_AUTHORING_FIELDS

Rejected on `--commit` with exit 11. Allowed in `--dry-run` to inspect what would happen, but cannot be written.

## 5. SAFE_AUTHORING_FIELDS

These are the only fields the foundation CLI is willing to consider for a real write (in a future approved task):

- `notes`
- `design_notes`
- `authoring_notes`
- `todo`
- `todo_metadata`
- `comment`
- `design_comment`

> Note: RM1.32-A-PRE intentionally stops the commit path at STEP 1/4 (auto-backup). The actual write (STEP 2/4) is a no-op. The first task that turns STEP 2/4 from no-op into a real, scoped write will be RM1.31-F (or its successor) and will require explicit user approval.

## 6. Write flow (the only acceptable shape)

```
0. Read approved task prompt.
1. Run validator suite (--include-baseline-diff). Must be PASS.
2. Snapshot current /api/heroes count (must be 100).
3. Run backup helper:
      python3 backup_hero_skill_kit_catalogs.py --reason <task_id>
      capture BACKUP_MANIFEST_PATH.
4. Set env var (only for this shell session):
      export DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE=YES_I_UNDERSTAND
5. Run the CLI commit (for SAFE_AUTHORING_FIELDS only):
      python3 hero_skill_kit_authoring_cli.py propose-update-field \
        --hero-id <id> --slot <s> --field <f> --value <v> --commit
6. The CLI auto-backs-up again as STEP 1/4 (defense-in-depth).
7. (FUTURE / RM1.31-F+) Actual write is performed.
8. Run validator suite WITH --include-baseline-diff and --allow-changed
   for the catalog file. Must be PASS.
9. Run API smoke and UI safety re-check.
10. Confirm /api/heroes count still = 100 and Borea still hidden.
11. Update baseline (NEW baseline_v<n+1>) ONLY IF the change is approved
    and persistent.
12. Unset env var: unset DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE
13. Write a checkpoint doc summarizing what changed.
```

## 7. Rollback flow

If validator suite fails after a real write:

```
1. The CLI auto-rollback logic will restore from the pre-write backup
   manifest (STEP 4/4 in the commit pipeline).
2. Re-run validator suite (--include-baseline-diff). Must be PASS.
3. Run API smoke and UI safety re-check.
4. Confirm /api/heroes count = 100 and Borea hidden.
5. Document the failure in the next checkpoint doc.
```

Manual rollback (out-of-band emergency):

```
1. Set env var:
      export DIVINE_ALLOW_CATALOG_RESTORE=YES_I_UNDERSTAND
2. Run:
      python3 restore_hero_skill_kit_catalogs.py \
        --manifest <pre_write_BACKUP_MANIFEST_PATH> --commit
3. The restore helper itself creates a pre-restore backup,
   restores, runs the suite, and auto-rolls back if the suite fails.
4. Unset env var.
```

## 8. Borea safety rules (NON-NEGOTIABLE)

- `greek_borea` MUST remain **catalog-only / launch_extra_premium** and **hidden from `/api/heroes`**.
- Legacy `borea` hero_id MUST remain **forbidden** in CLI and absent from API.
- `primordial_gaia` MUST remain absent from API and catalog.
- `marchio_boreale` MUST remain exclusively on `greek_borea` (0 leaks in non-Borea).
- `divine_weapon_id = borea_wings_of_the_north_wind` MUST NOT be renamed.
- Borea activation in gacha/roster/runtime is an **isolated, separate task**. It must NOT be bundled with any catalog-edit task.

## 9. Examples

### 9.1 Safe dry-run
```
$ python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py \
    propose-update-field --hero-id greek_atalanta --slot skill_1 \
    --field authoring_notes --value "QA note" --dry-run
[DRY-RUN] propose-update-field hero=greek_atalanta slot=skill_1 field=authoring_notes value='QA note'
  WOULD CHECK: schema compliance for field "authoring_notes" against hero_skill_kit_schema_v1.
  NOTE: no write performed. CLI is dry-run-only.
```

### 9.2 Commit blocked without env var
```
$ python3 hero_skill_kit_authoring_cli.py propose-update-field \
    --hero-id greek_atalanta --slot skill_1 --field authoring_notes \
    --value "blocked commit" --commit
[COMMIT] ...
  REJECTED: --commit requires env var DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE=YES_I_UNDERSTAND (got None).
exit code 10
```

### 9.3 Frozen field rejected
```
$ python3 hero_skill_kit_authoring_cli.py propose-update-field \
    --hero-id greek_atalanta --slot skill_1 --field final_numbers \
    --value "{}" --commit
  REJECTED: field "final_numbers" is FROZEN in the catalog-only stage.
exit code 7
```

### 9.4 Restore dry-run
```
$ LATEST=$(ls -t /app/backups/hero_skill_kits/*/MANIFEST.json | head -1)
$ python3 restore_hero_skill_kit_catalogs.py --manifest "$LATEST" --dry-run
  backup integrity: OK (all checksums match)
  mode            : DRY-RUN (no files restored)
```

## 10. One-shot Emergent prompt pattern for future approved write tasks

When the user wants to perform a real catalog write through the authoring CLI:

```
TASK RM1.31-F — <descriptive title>

Scope:
  - target catalog file: <path>
  - target hero: <hero_id>
  - target slot: <slot>
  - target field: <field>  (must be in SAFE_AUTHORING_FIELDS)
  - expected before: <value-before>
  - expected after:  <value-after>

Required:
  - run validator suite --include-baseline-diff (must be PASS) before any write
  - backup with reason "RM1.31-F:<short-id>"
  - export DIVINE_ALLOW_SKILL_KIT_AUTHORING_WRITE=YES_I_UNDERSTAND
  - run propose-update-field --commit
  - run validator suite --include-baseline-diff --allow-changed <catalog-file>
  - run API smoke + UI safety
  - confirm /api/heroes count = 100, Borea hidden
  - regenerate baseline v<n+1> if change is persistent
  - write checkpoint doc

Forbidden:
  - any change to FROZEN or DANGEROUS fields
  - any Borea visibility change
  - any DB / runtime / API route / UI mutation
```

## 11. Companion scripts (read-only summary)

| Script | Purpose |
|---|---|
| `/app/backend/scripts/backup_hero_skill_kit_catalogs.py` | Create timestamped backup + MANIFEST.json |
| `/app/backend/scripts/restore_hero_skill_kit_catalogs.py` | Restore from manifest (env-gated commit + auto-rollback) |
| `/app/backend/scripts/prune_hero_skill_kit_backups.py` | Keep N most-recent backups; env-gated commit |
| `/app/backend/scripts/hero_skill_kit_authoring_cli.py` | Read / dry-run / guarded commit CLI |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Validator suite runner (12 + optional baseline diff) |
| `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py` | Baseline SHA256 + invariants diff |
| `/app/backend/scripts/validate_status_resolver_contract.py` | RM1.31-C status contract validator |

---

This playbook is binding for any future catalog-write task. Failing to follow it on a real write must trigger an immediate rollback and a postmortem doc.
