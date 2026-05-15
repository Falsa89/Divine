# 28 — 5★ Legacy Status Tags Normalization Plan v1

**Task origin:** RM1.28-C  
**Status:** design-only / read-only / catalog-not-modified  
**Runtime:** NOT attached  
**Borea:** unchanged — hidden / pending / catalog-only

---

## 1. Context

After RM1.28-A (5★ passive_advanced source completion) and RM1.28-B
(5★ cross-link audit), the new `passive_advanced` slots are clean
(status_tags strictly within the approved status core whitelist).

However, the older 5★ slots (`basic`, `passive_base`, `skill_1`,
`skill_2`) — created earlier during the source conversion in RM1.26-B2 —
still contain **legacy / non-whitelist status_tags** that are mostly
category labels (e.g. `damage`, `buff`, `debuff`) or ambiguous concrete
tags (`dot`, `hot`, `shield`).

RM1.28-C is a **read-only plan**: it audits these tags, classifies them
into 4 buckets, and produces a JSON normalization plan. **It does NOT
modify the catalog.**

---

## 2. Audit results (snapshot)

| Metric | Value |
|---|---|
| 5★ entries scanned | 20 |
| Inspected slots (basic / passive_base / skill_1 / skill_2) | 80 |
| Total `status_tags` scanned | 121 |
| In approved whitelist | 10 |
| Legacy / non-whitelist | 111 |
| Distinct legacy tags | 12 |
| `passive_advanced` clean (RM1.28-A) | 20/20 |
| Borea / marchio_boreale leak in 5★ | **none** ✅ |
| Forbidden non-canonical IDs in 5★ | **none** ✅ |

---

## 3. Frequency & classification table

| Legacy tag | Freq | Bucket | Recommended action | Safe auto-fix |
|---|---:|---|---|:---:|
| `damage` | 52 | A. category_tag_keep_as_design_metadata | demote_to_design_taxonomy_field | ❌ |
| `buff` | 24 | A. category_tag_keep_as_design_metadata | demote_to_design_taxonomy_field | ❌ |
| `debuff` | 11 | A. category_tag_keep_as_design_metadata | demote_to_design_taxonomy_field | ❌ |
| `control` | 6 | A. category_tag_keep_as_design_metadata | demote_to_design_taxonomy_field | ❌ |
| `dot` | 5 | B. likely_status_mapping_needed | manual_context_mapping | ❌ |
| `heal` | 3 | A. category_tag_keep_as_design_metadata | manual_context_mapping | ❌ |
| `hot` | 3 | B. likely_status_mapping_needed | manual_context_mapping | ❌ |
| `conditional_bonus` | 2 | C. trigger_or_rule_tag_not_status | move_to_trigger_or_rule_field | ❌ |
| `shield` | 2 | B. likely_status_mapping_needed | manual_context_mapping | ❌ |
| `aura_debuff` | 1 | D. ambiguous_needs_manual_review | manual_review_required | ❌ |
| `debuff_aura` | 1 | D. ambiguous_needs_manual_review | manual_review_required | ❌ |
| `trigger` | 1 | C. trigger_or_rule_tag_not_status | move_to_trigger_or_rule_field | ❌ |

**Distribution per bucket:**
- A. category_tag_keep_as_design_metadata: **5 distinct tags** (~88 occurrences)
- B. likely_status_mapping_needed: **3 distinct tags** (~10 occurrences)
- C. trigger_or_rule_tag_not_status: **2 distinct tags** (~3 occurrences)
- D. ambiguous_needs_manual_review: **2 distinct tags** (~2 occurrences)
- E. forbidden_or_invalid: **0 distinct tags** ✅

---

## 4. Bucket explanations

- **A. category_tag_keep_as_design_metadata** — Generic taxonomy labels.
  Not status effects. Recommended: demote from `status_tags` to a new
  design-only field (e.g. `design_taxonomy_tags`) without rewriting them
  as approved statuses.
- **B. likely_status_mapping_needed** — Concrete but ambiguous tags. Each
  requires per-hero context mapping (e.g. `dot` on `egyptian_claw_of_sekhmet`
  likely → `burn`/`bleed`; `dot` on `cursed_pestilence_herald` likely →
  `poison`/`curse`).
- **C. trigger_or_rule_tag_not_status** — Belong in a `trigger` or `rule`
  field, not in `status_tags`. Recommended: move to existing
  `trigger`/`effect_summary`/`description` fields.
- **D. ambiguous_needs_manual_review** — Runtime meaning unclear; needs a
  manual decision per hero.
- **E. forbidden_or_invalid** — Hard fail if any 6★/Borea/DW/Domain
  marker leaks into 5★. **Zero occurrences detected.** ✅

---

## 5. Candidate mappings (informational, NOT auto-applied)

| Legacy tag | Candidate replacements (per identity) |
|---|---|
| `dot` | `burn`, `bleed`, `poison`, `curse`, `frostbite`, `shock` |
| `hot` | `regeneration`, `healing_up` |
| `heal` | `healing_up`, `regeneration`, OR move to `effect_kind:direct_heal` |
| `shield` | `physical_shield`, `magical_shield`, `hybrid_shield` |
| `aura_debuff` / `debuff_aura` | `vulnerability`, `def_down`, `speed_down`, `effect_accuracy_up` |

---

## 6. Safety guarantees of this plan

```json
{
  "catalog_only": true,
  "design_audit_only": true,
  "runtime_attached": false,
  "battle_runtime_attached": false,
  "db_write_allowed": false,
  "auto_fix_applied": false,
  "borea_activation_allowed": false,
  "do_not_treat_as_live_kit": true
}
```

- `hero_skill_kits_5star_full_v1.json` **NOT modified**
- `hero_skill_kits_6star_borea_v1.json` **NOT modified**
- Divine Weapon catalog/API/UI **NOT modified**
- `passive_advanced` (RM1.28-A) **clean and unchanged**
- No DB writes / migrations / seed
- No runtime, gacha, roster, Character Bible, asset, HP bar runtime touched
- `/api/heroes` count remains 100
- Borea & marchio_boreale absent from 5★

---

## 7. Recommended next task (only after explicit approval)

**RM1.28-D — 5★ Legacy Status Tags Controlled Normalization Patch**

Requires:
- explicit approval after reviewing this plan
- per-hero, per-slot manual mapping using the `candidate_mappings`
- preserve `passive_advanced` approved entries unchanged
- preserve `final_numbers=null`, `runtime_attached=false`,
  `battle_runtime_attached=false` everywhere
- no true Ultimate / Divine Weapon / Domain / Marchio Boreale introduced
  into 5★
- bucket A → demote to new `design_taxonomy_tags` field rather than
  rewriting as statuses
- bucket B → per-hero context mapping
- bucket C → move to `trigger`/`rule` fields
- bucket D → manual review per hero

---

## 8. Files

| Path | Type |
|---|---|
| `/app/backend/scripts/audit_5star_legacy_status_tags.py` | read-only audit + plan generator |
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_legacy_status_tags_normalization_plan_v1.json` | design-only plan (~28 KB) |
| `/app/docs/divine/28_5STAR_LEGACY_STATUS_TAGS_NORMALIZATION_PLAN.md` | this document |

## 9. Re-run command

```bash
python3 /app/backend/scripts/audit_5star_legacy_status_tags.py
```

Exit `0` if audit completes without structural error. Output includes
the human-readable report + writes/updates the plan JSON in-place.
