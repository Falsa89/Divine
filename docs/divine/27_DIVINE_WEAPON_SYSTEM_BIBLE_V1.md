# 27 — Divine Weapon System Bible v1

**Task origin:** RM1.27-A  
**Status:** design-only / catalog-only / read-only / inert  
**Runtime:** NOT attached to battle engine, HP bar, VFX runtime, status runtime, gacha, roster, or DB.  
**Borea:** remains hidden / pending_assets / catalog-only. `borea_activation_allowed = false`.

---

## 1. Scope

This Bible defines the canonical design contract for **Divine Weapons** — unique, hero-exclusive relics tied to the 6★ native heroes of Divine Waifus. The v1 foundation covers:

- 12 **launch_base** Divine Weapons (Athena, Artemis, Gaia, Nyx, Raijin, Susanoo, Amaterasu, Sekhmet, Tiamat, Isis, Morrigan, Pestilence Horseman)
- 1 **launch_extra_premium** Divine Weapon (Borea — catalog-only, not activated)

No runtime activation. No balance numbers. No DB. No sprite sheets.

---

## 2. Hard safety contract

Every record carries safety flags equivalent to:

```json
{
  "catalog_only": true,
  "runtime_attached": false,
  "battle_runtime_attached": false,
  "hp_bar_runtime_attached": false,
  "vfx_runtime_attached": false,
  "gacha_attached": false,
  "roster_activation_attached": false,
  "borea_activation_allowed": false,
  "balance_values_finalized": false,
  "do_not_treat_as_live_power": true
}
```

Do not modify: `battle_engine.py`, `combat.tsx`, `HPBar.tsx`, gacha, summon, roster, Character Bible, hero DB records, `user_heroes`, assets, status runtime, VFX runtime, HP bar runtime, battle runtime, Borea activation, economy/currency systems, or the existing 6★ hero skill kit catalog.

---

## 3. Identity & exclusivity

- Every Divine Weapon is **exclusive to one hero**: `exclusive_to_hero = true`.
- `native_rarity_required = 6` on all records.
- `weapon_type = divine_relic` on all records.
- `catalog_status = catalog_only` at this stage.

---

## 4. ID convention & overrides vs RM1.27-A prompt

IDs are preserved from the already-existing 6★ hero skill kit catalog (`hero_skill_kits_6star_borea_v1.json`) wherever they already exist. The RM1.27-A prompt suggested two alternative IDs; the Bible documents the preserved canonical IDs:

| hero_id | RM1.27-A prompt suggested | **Preserved canonical** |
|---|---|---|
| `greek_athena` | `athena_aegis` | **`aegis_of_athena`** |
| `egyptian_isis` | `isis_sacred_tyet` | **`isis_sacred_tyet_knot`** |

All other 11 IDs match the prompt 1:1.

---

## 5. Progression states

Every Divine Weapon has exactly 7 progression states:

| order | state_key | display (it) | gameplay bonus | battle presence |
|---|---|---|---|---|
| 0 | `sealed` | Sigillata | ❌ | ❌ |
| 1 | `dormant` | Dormiente | ✅ | ✅ |
| 2 | `awakened` | Risvegliata | ✅ | ✅ |
| 3 | `empowered` | Rafforzata | ✅ | ✅ |
| 4 | `blessed` | Benedetta | ✅ | ✅ |
| 5 | `ascendant` | Ascendente | ✅ | ✅ |
| 6 | `divine` | Divina | ✅ | ✅ |

Hard rules:
- `sealed` = no gameplay bonus AND no Divine Presence Layer.
- `dormant+` = gameplay/design hook AND Divine Presence Layer metadata.

---

## 6. Unlock requirements (seal break)

Every record carries:

- `initial_state = sealed`
- `break_seal_required = true`
- `required_hero_star_level = 10`
- `requires_dedicated_materials = true`
- `requires_gold = true`
- `requires_duplicate_materials = true`

No numbers are finalized. `final_numbers = null` everywhere.

---

## 7. Material requirements

Quantities and min star levels are intentionally **null** at v1 foundation. Supported material types:

- `same_element_copy` — used in low/mid steps
- `specific_hero_copy` — used in high steps
- `event_limited_substitute` — reserved
- `dedicated_currency` — reserved
- `gold` — reserved

Copies are mandatory in controlled measure. No live economy hooks yet.

---

## 8. Hooks (effect / skill / status / vfx)

Every hook is **inert** and tied to a `state_required`. No numeric values.  
`final_numbers = null`. `runtime_attached = false`.

State gating rules:
- `ultimate_signature_upgrade` hooks: only from `ascendant` or `divine`.
- `domain_interaction` hooks: only from `ascendant` or `divine`.
- Personal statuses remain `source_locked = true`.

Borea's `Marchio Boreale` is:
- `status_id = marchio_boreale`
- `hook_type = personal_status_enhancement`
- `source_locked = true`
- `state_required = dormant`
- `runtime_attached = false`
- Not usable by other heroes.

---

## 9. Divine Presence Layer (metadata only)

The Divine Presence Layer is **metadata** for a future lightweight persistent battle VFX layer. It is **not** a physical weapon animation, and **does not** require new sprite sheets.

Contract:
```json
{
  "enabled": true,
  "enabled_from_state": "dormant",
  "disabled_in_state": "sealed",
  "layer_type": "persistent_lightweight_battle_vfx",
  "is_physical_weapon_animation": false,
  "requires_new_sprite_sheet": false,
  "runtime_attached": false
}
```

Intensity ramps `sealed=none → dormant=minimal → ... → divine=premium_controlled`.

Readability rules (must NOT obscure): HP bar, status icons, character sprite. Must NOT look like a status/buff, a domain, or a skill cast. Must remain mobile-readable.

---

## 10. Divine Presence Identity

| hero_id | hero_accent_type | element_color_family |
|---|---|---|
| greek_athena | `aegis_geometric_glow` | `sacred_white_gold` |
| greek_artemis | `lunar_wind_crescent` | `lunar_wind` |
| greek_gaia | `primordial_roots_glow` | `earth_green_gold` |
| primordial_nyx | `starry_night_shadow` | `night_shadow` |
| japanese_raijin | `thunder_drum_sparks` | `lightning_yellow_blue` |
| japanese_susanoo | `storm_blade_wind` | `lightning_yellow_blue` |
| japanese_amaterasu | `solar_mirror_radiance` | `solar_gold` |
| egyptian_sekhmet | `solar_lioness_heat` | `solar_heat` |
| mesopotamian_tiamat | `abyssal_primordial_water` | `abyssal_blue` |
| egyptian_isis | `sacred_tyet_light` | `light_gold` |
| celtic_morrigan | `raven_omen_shadow` | `dark_violet` |
| cursed_pestilence_horseman | `controlled_plague_miasma` | `dark_violet` |
| greek_borea | `north_wind_frost_aura` | `frost_wind` |

---

## 11. UI Presentation contract

Every record exposes:

```json
{
  "show_in_hero_detail": true,
  "show_as_separate_tab": true,
  "tab_label": "Arma Divina",
  "show_lore": true,
  "show_unlock_requirement": true,
  "show_active_effects": true,
  "show_locked_effect_preview": true,
  "show_divine_presence_preview": true,
  "sealed_state_message": "Effetti attivi: nessuno.",
  "sealed_presence_message": "Presenza Divina in battaglia: non attiva.",
  "locked_until_message": "Richiede eroe a 10★ e materiali dedicati per rompere il sigillo."
}
```

---

## 12. Borea

- `hero_id = greek_borea` (NOT legacy `borea`)
- `divine_weapon_id = borea_wings_of_the_north_wind`
- `release_group = launch_extra_premium`
- `catalog_status = catalog_only`
- `borea_activation_allowed = false`
- Roster / gacha / battle visibility unchanged. Borea remains hidden / pending_assets.

---

## 13. Validator

Location: `/app/backend/scripts/validate_divine_weapon_catalog.py`

Runs 32 checks (counts, IDs, native_rarity, exclusivity, sealed/dormant logic, 10★ seal break, Divine Presence Layer flags, Borea safety, no legacy borea, etc.). Returns exit 0 on PASS, 1 on FAIL.

Command:

```bash
python /app/backend/scripts/validate_divine_weapon_catalog.py
```

---

## 14. Out-of-scope at v1

- No connection to battle runtime, HP bar runtime, status runtime, VFX runtime.
- No final balance numbers.
- No DB write, no migration.
- No sprite sheet asset (the Divine Presence Layer does not require new sprite sheets).
- No gacha entry, no roster activation.
- No Borea activation.
- No modification to existing 6★ skill kit catalog.
