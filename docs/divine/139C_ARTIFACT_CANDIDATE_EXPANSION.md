# 139C — PROJECT_Q Track C: Artifact Candidate Expansion (Design-Only)

## Verdict
`TRACK_C_ARTIFACT_CANDIDATE_EXPANSION_READY`

## Marker JSON
`/app/data/design/artifacts/project_q_artifact_candidate_expansion_v1.json`

## Validator
`/app/backend/scripts/validate_project_q_artifact_candidate_expansion_v1.py` → **[PASS]**

## Candidati (8, tutti `status = design_only`, copertura 5 fazioni e 4/6 categorie)
| artifact_id | name | rarity | faction | category | bonus | obtain |
|---|---|---:|---|---|---|---|
| art_sacred_cup | Sacred Cup | 6 | celtic | vessel_relic | hp_pct +1.5% | artifact_summon_banner |
| art_norse_horn | Gjallarhorn Echo | 5 | norse | banner_relic | speed_pct +1.0% | artifact_summon_banner |
| art_greek_aegis_icon | Aegis Icon | 5 | greek | icon_relic | def_pct +1.5% | event_reward |
| art_egyptian_ankh_glyph | Ankh Glyph | 5 | egyptian | glyph_relic | hp_pct +1.0% | event_reward |
| art_japanese_mirror_relic | Yata-no-Kagami Echo | 6 | japanese | icon_relic | crit_pct +0.5% | artifact_summon_banner |
| art_primordial_void_vessel | Void Vessel | 6 | primordial | vessel_relic | atk_pct +1.0% | event_reward |
| art_norse_runestone_glyph | Bind Rune Glyph | 4 | norse | glyph_relic | def_pct +0.5% | event_reward |
| art_celtic_oak_banner | Sacred Oak Banner | 4 | celtic | banner_relic | hp_pct +0.5% | event_reward |

## Categorie deliberatamente differite
- `weapon_relic`, `armor_relic` — riservate al prossimo batch per evitare confusione semantica con equipment/divine weapon.

## Invariants verificati per ciascun candidato
- `is_equipment == false` ✅
- `occupies_gear_slot == false` ✅
- `is_divine_weapon == false` ✅
- `status == "design_only"` ✅
- `obtainment_source != "hero_summon_banner"` ✅
- `value_pct ∈ [0, 1.5]` ✅
- Top-4 theoretical bonus (4 artifact simultaneamente attivi) ≤ master cap 5.0% ✅

## Side effects
Nessuno. Lista esiste solo come JSON design-only.
