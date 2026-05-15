# RM1.31 — Hero Skill Kit Authoring Tools Foundation — CHECKPOINT

**Status:** ✅ **PASS** — Three new READ/DRY-RUN-only authoring tools delivered. ZERO catalog/runtime/DB/UI mutations. Validator suite green 12/12.

---

## 1. Scripts Created

| Path | Purpose |
|---|---|
| `/app/backend/scripts/hero_skill_kit_authoring_cli.py` | RM1.31-A authoring CLI (READ/DRY-RUN-only, 7 subcommands) |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | RM1.31-B single-command validator suite runner |
| `/app/backend/scripts/validate_status_resolver_contract.py` | RM1.31-C status-resolver contract validator (5★/6★ ↔ RM1.25-B) |

No catalog data was modified (SHA256 prefixes preserved after the run: 5★ `f20216c0…`, 6★ `4172da0d…`, DW `e3ed42f5…`).

## 2. RM1.31-A Authoring CLI — Available Commands

All commands are **READ + DRY-RUN-only**. The module declares:
> `RM1.31-A authoring CLI is READ/DRY-RUN-only and must not mutate catalog data.`

| Command | Purpose | Safety |
|---|---|---|
| `summary` | Print 5★/6★/DW counts + top-level safety flags + Borea visibility warning | read-only |
| `list --rarity 5\|6` | List all canonical heroes with slot summary | read-only |
| `show --hero-id <id>` | Detailed kit summary; rejects legacy `borea`, flags `greek_borea` as catalog-only | read-only |
| `validate-dry-run --hero-id <id>` | Single-hero structural validation (no writes) | dry-run |
| `propose-add-slot --hero-id <id> --slot <s> --dry-run` | Reports whether slot would be allowed; rejects 5★ ultimate | dry-run, no write |
| `propose-update-field --hero-id <id> --slot <s> --field <f> --value <v> --dry-run` | Reports schema compliance; **freezes** `final_numbers`, `runtime_attached`, `battle_runtime_attached` | dry-run, no write |
| `export-report --out <path>` | Writes a read-only JSON snapshot to `/app/backend/reports` or `/tmp` ONLY; rejects any other path | write to safe report dir only |

### Verified rejections (exit codes)

| Command | Expected | Observed |
|---|---|---|
| `show --hero-id borea` | REJECTED | exit 3 ✅ |
| `propose-add-slot --hero-id greek_atalanta --slot ultimate --dry-run` | REJECTED (5★ cannot have ultimate) | exit 6 ✅ |
| `propose-update-field --field final_numbers --dry-run` | REJECTED (frozen field) | exit 7 ✅ |
| `export-report --out /app/data/design/x.json` | REJECTED (unsafe path) | exit 8 ✅ |

## 3. RM1.31-B Validator Suite Runner — Usage

```
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --json-out /tmp/suite.json
```

Runs 11 required validators + 1 optional (RM1.31-C). Exit 0 only when every required validator passes.

### Result

```
Overall: PASS  (pass=12, fail=0, miss=0)
```

| Task | Script | Result |
|---|---|---|
| RM1.28-A | validate_5star_passive_advanced_source.py | ✅ PASS |
| RM1.28-B | audit_5star_skill_kits_crosslinks.py | ✅ PASS |
| RM1.28-C | audit_5star_legacy_status_tags.py | ✅ PASS |
| RM1.28-D | validate_5star_legacy_status_tags_normalized.py | ✅ PASS |
| RM1.28-E | validate_5star_manual_review_residuals_resolved.py | ✅ PASS |
| RM1.29 | audit_6star_skill_kits_crosslinks.py | ✅ PASS |
| RM1.30-A | validate_6star_catalog_safety_metadata.py | ✅ PASS |
| RM1.30-B | audit_6star_effect_tags_taxonomy.py | ✅ PASS |
| RM1.30-C | audit_hero_skill_kit_catalog_consolidation.py | ✅ PASS |
| RM1.27-A | validate_divine_weapon_catalog.py | ✅ PASS |
| RM1.27-D | audit_divine_weapon_crosslinks.py | ✅ PASS |
| **RM1.31-C** | **validate_status_resolver_contract.py** | ✅ **PASS (NEW)** |

## 4. RM1.31-C Status Resolver Contract Validator

**Source of truth:** `/app/data/design/skill_status_vfx_catalogs/status_effect_catalog_v1.json` (40 status IDs).

### Result — PASS

| Check | Result |
|---|---|
| Status catalog file exists & parses | ✅ |
| 39 mandatory core statuses present | **39/39** ✅ |
| `marchio_boreale` declared as unique-personal in catalog | ✅ |
| `domain_effect` declared (design-only) | ✅ |
| 5★ status references (status_tags + status_interactions) | **143 refs / 29 unique**, all resolved ✅ |
| 6★ status references (core_status_ids + status_tags + status_interactions) | **197 refs / 30 unique**, all resolved ✅ |
| `marchio_boreale` leak in non-Borea | **0** ✅ |
| Forbidden / unknown status refs | **0** ✅ |

## 5. Safety Guarantees

- ❌ No catalog data mutated (5★, 6★, DW SHA256 unchanged).
- ❌ No MongoDB writes.
- ❌ No DB schema changes.
- ❌ No runtime import from battle engine.
- ❌ No Borea visibility change (`greek_borea` remains catalog-only; legacy `borea` rejected by CLI and API).
- ❌ No Character Bible mutation.
- ❌ No asset mutation.
- ❌ No API route changes (loader/routes unchanged).
- ❌ No UI changes (`hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx` unchanged).
- ❌ No `final_numbers`, `runtime_attached`, `battle_runtime_attached` flips.

The CLI explicitly freezes `final_numbers`, `runtime_attached`, `battle_runtime_attached`. Any `propose-update-field` referencing those returns exit code **7** and exits without action.

## 6. What is Still NOT Implemented (by design)

- Real write-enabled authoring (any catalog mutation) — deferred to a future task that must include explicit user approval, backup mechanism, and post-write validators.
- Runtime adapter to battle engine — gated behind `SKILL_KIT_RUNTIME_ENABLED=false` feature flag (does not exist yet).
- Balance pass / `final_numbers` finalization — separate task.
- Borea activation in gacha/roster/`/api/heroes` — strictly separate, isolated task.
- Status icon / VFX runtime binding — RM1.25-B catalog stays design-only.

## 7. Future Steps — Write-Enabled Authoring Tools

When time comes to allow real writes, prerequisites are:

1. Backup mechanism (`.bak` copy of the catalog under `/app/backups/hero_skill_kits/`).
2. Post-write validator suite run with auto-rollback on FAIL.
3. CLI flag `--commit` distinct from `--dry-run`; commit must require both `--commit` AND an environment variable confirmation (`AUTHORING_COMMIT_ALLOWED=true`).
4. Status reference must pass `validate_status_resolver_contract.py` after edit.
5. Divine Weapon cross-link must remain valid after 6★ edit.
6. Forbidden fields (`final_numbers`, `runtime_attached`, `battle_runtime_attached`) remain frozen unless a balance/runtime task explicitly unlocks them.
7. Audit log file under `/app/backend/reports/authoring_audit.log`.

## 8. Future Steps — Runtime Adapter

Already documented in `hero_skill_kit_authoring_readiness_plan_v1.json` (RM1.30-C):
- Final balance numbers attached per slot.
- Cooldown/chance/duration finalized.
- Status runtime resolver (currently design-only).
- HP bar status icon renderer + asset bindings.
- VFX runtime mapping.
- `battle_engine` adapter.
- API/runtime contract document.
- Mobile QA pass.
- Feature flag `SKILL_KIT_RUNTIME_ENABLED=false` with rollback.
- Borea activation MUST remain a separate task.

## 9. Borea Safety

| Check | Result |
|---|---|
| `greek_borea` exactly once in 6★ catalog | ✅ |
| `release_group == launch_extra_premium` | ✅ |
| `divine_weapon_id == borea_wings_of_the_north_wind` | ✅ |
| CLI `show --hero-id borea` | REJECTED (legacy/forbidden alias) ✅ |
| CLI `show --hero-id greek_borea` | OK, flagged "⚠ CATALOG-ONLY" ✅ |
| `marchio_boreale` only on greek_borea (status resolver verified) | ✅ |
| `greek_borea` in `/api/heroes` | NOT VISIBLE ✅ |
| Legacy `borea` in `/api/heroes` | NOT VISIBLE ✅ |

## 10. Re-run Commands

```bash
# CLI (READ/DRY-RUN-only)
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py summary
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py list --rarity 5
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py list --rarity 6
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py show --hero-id greek_athena
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py show --hero-id greek_borea
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py show --hero-id borea            # rejects
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py validate-dry-run --hero-id greek_atalanta
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py propose-add-slot --hero-id greek_atalanta --slot ultimate --dry-run   # rejects
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py propose-update-field --hero-id greek_atalanta --slot skill_1 --field final_numbers --value '{}' --dry-run   # rejects
python3 /app/backend/scripts/hero_skill_kit_authoring_cli.py export-report --out /tmp/cli_export.json

# Status resolver
python3 /app/backend/scripts/validate_status_resolver_contract.py

# Whole validator suite
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --json-out /tmp/suite_report.json
```

---

### Notes on doc numbering

Doc number 35 used; no conflict with the existing sequence (`33_…`, `34_HERO_SKILL_KIT_CATALOG_FINAL_CHECKPOINT_RM130C.md`).
