# 119C — V5 BLOCK C — ROSTER VISIBILITY VALIDATOR EXTENSION V2

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V5`  
**Block**: C — `ROSTER_VISIBILITY_VALIDATOR_EXTENSION_V2`  
**Verdict**: 🟢 `BLOCK_C_ROSTER_VISIBILITY_VALIDATOR_V2_READY`  
**Modalità**: SUITE EXTENSION ONLY (no runtime mutation)

---

## 1. Relazione V1 ↔ V2

**V2 è superset di V1**: include tutti i 7 invariants V1 + 5 nuovi check più granulari.

V1 resta nella suite per backward compatibility + quick smoke; V2 è il check più profondo.

---

## 2. V2 invariants (11 totali)

| ID | Check | Origin |
|---|---|---|
| INV2_HEROES_COUNT | `/api/heroes` count == 100 | V1 |
| INV2_GAIA_404 | `/api/heroes/primordial_gaia` HTTP 404 | V1 |
| INV2_BOREA_200_INERT | `/api/heroes/borea` HTTP 200 + `is_obtainable False` | V1 |
| INV2_GREEK_BOREA_200_INERT | `/api/heroes/greek_borea` HTTP 200 + `is_obtainable False` | V1 |
| **INV2_BOREA_NOT_IN_BATTLE_PICKER** | heroes con `is_obtainable=True` non includono borea/greek_borea | 🆕 V2 |
| **INV2_BOREA_NOT_IN_GACHA_BANNER_POOL** | gacha pool non include borea/greek_borea (heuristic) | 🆕 V2 |
| **INV2_LEGACY_PLACEHOLDERS_HIDDEN** | nessun hero con name `PLACEHOLDER_/TODO/TEST` | 🆕 V2 |
| **INV2_HERO_RARITY_DISTRIBUTION_SANE** | ≥ 4 rarity distinct | 🆕 V2 |
| **INV2_HERO_ELEMENT_DISTRIBUTION_SANE** | ≥ 4 element distinct | 🆕 V2 |
| INV2_DRIFT_DOCS_KNOWN | drift docs canonical rule_id valid | V1 |
| INV2_CHARACTER_BIBLE_FILES_PRESENT | sanctuary.py + heroes.py present | V1 |

---

## 3. Script

- **Path**: `/app/backend/scripts/validate_roster_visibility_invariants_v2.py`
- **Behavior**: read-only HTTP smoke + JSON parse + drift marker check
- **DB writes**: 0
- **Suite registration**: OPTIONAL come `V5-ROSTER-VISIBILITY-INVARIANTS-V2`

---

## 4. Verdict

🟢 **`BLOCK_C_ROSTER_VISIBILITY_VALIDATOR_V2_READY`**
