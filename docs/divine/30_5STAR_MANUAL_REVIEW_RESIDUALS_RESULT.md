# 30 — 5★ Manual Review Residuals Resolution Result

**Task origin:** RM1.28-E  
**Status:** design-only / 5 target slots resolved / read-only fields enriched  
**Runtime:** NOT attached  
**Borea:** unchanged — hidden / pending / catalog-only

---

## 1. Decisions per target slot

All 5 RM1.28-D residuals were resolved cleanly from each slot's
`design_summary` text — **no guessing**.

| # | hero_id.slot | legacy tag (RM1.28-D) | design_summary | RM1.28-E decision | New `status_tags` |
|---|---|---|---|---|---|
| 1 | `celtic_mist_banshee.passive_base` | `aura_debuff` | *"Aumenta effect_accuracy e riduce speed nemica."* | mapped per text | **`effect_accuracy_up`, `speed_down`** |
| 2 | `cursed_pestilence_herald.passive_base` | `debuff_aura` | *"Nemici con DoT ricevono meno cure."* | mapped per text | **`healing_reduction`** |
| 3 | `creature_crimson_phoenix.skill_1` | `hot` | *"Danno fuoco e HoT su sé stessa."* | HoT = healing-over-time | **`regeneration`** |
| 4 | `creature_lernaean_hydra.skill_2` | `hot` | *"Colpisce 3 nemici e ottiene HoT."* | HoT su self | **`regeneration`** |
| 5 | `egyptian_claw_of_sekhmet.skill_1` | `dot` | *"Danno forte e burn al bersaglio."* | legacy "dot" = alias del `burn` esplicito | **`burn`** |

Tutti i 5 → `manual_review_required` chiuso (`false`), nota dettagliata aggiunta a `normalization_notes`, history aggiunta a `normalization_metadata.rm128e_resolution_history`.

## 2. Before / After

| Metric | Before | After |
|---|---:|---:|
| Slot flagged `manual_review_required` | 5 | **0** |
| RM1.28-E target resolved | 0/5 | **5/5** |
| `passive_advanced` approved | 20/20 | 20/20 |
| `skill_2.is_true_ultimate=false` | 20/20 | 20/20 |
| Legacy tags in `status_tags` (catalog-wide) | 0 | **0** |
| `final_numbers=null` ovunque | ✓ | ✓ |
| `runtime_attached=false` ovunque | ✓ | ✓ |
| `/api/heroes` count | 100 | 100 |

## 3. Files & idempotenza

- `resolve_5star_manual_review_residuals.py` — patch script idempotente (re-run = 0 modifiche).
- `validate_5star_manual_review_residuals_resolved.py` — post-patch validator.
- `hero_skill_kits_5star_full_v1.json` — solo i 5 slot target modificati.
- `passive_advanced` **EXACTLY** preservato.

## 4. Safety

- `battle_engine.py` / `combat.tsx` / HP bar runtime / gacha / roster / Character Bible / asset → **non toccati**
- DB / migrations / seed → **0 writes**
- 6★ catalog / Divine Weapon catalog → **non toccati**
- Borea / Marchio Boreale / true Ultimate / Divine Weapon / Domain → **non introdotti in 5★**
- Plan RM1.28-C → preservato

## 5. Re-run

```bash
python3 /app/backend/scripts/resolve_5star_manual_review_residuals.py
python3 /app/backend/scripts/validate_5star_manual_review_residuals_resolved.py
```
