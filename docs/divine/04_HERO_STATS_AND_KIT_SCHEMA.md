# Hero Stats and Skill Kit Schema

> **Stato:** RM1.21-A — fondazione schema/design data. **Nessuna modifica runtime.** **Nessuna scrittura DB.**
> **Files associati:**
> - `data/design/hero_stats_schema.json` (v0.2)
> - `data/design/hero_skill_schema.json` (v0.2)
> - Cross-ref: `backend/data/character_bible.py`, `backend/battle_engine.py` (immutati).

---

## 1. Cosa fa RM1.21-A

Definisce la **fondazione professionale** per stats e skill kit dei 100 eroi launch + Borea, **senza toccare il runtime**. Output:

- Schema ufficiale stats con `key/display_name/description/type/default/tier/role_relevance/runtime_keys`.
- Role stat bias (priorità statistiche per ruolo).
- Rarity budget framework (moltiplicatori `stat_budget_x` per `native_rarity`).
- Skill schema con 4 slot canonici (`basic_attack`, `skill`, `ultimate_or_special`, `passive`) e mapping ai legacy slot runtime (`nad/sad/sp/passive`).
- Effect types completi (14 tipi) con flag `runtime_supported`.
- Role kit templates (9 ruoli) con identity, stat priorities, common skills, weakness, patterns.
- Rarity complexity rules (1★…6★) con limiti su skill/passive/effetti per skill.
- Esempi schema-validati per **Hoplite** e **Berserker**.

---

## 2. Stat Schema ufficiale (riepilogo)

13 stats, due tier:

### Core (5)
| key | display_name | default | scaling_with_level |
| --- | --- | --- | --- |
| `hp` | HP | 8000 | ✓ |
| `attack` | ATK | 1000 | ✓ |
| `defense` | DEF | 400 | ✓ |
| `speed` | Velocità | 100 | ✓ |
| `crit_rate` | Tasso Critico | 0.10 | ✗ |
| `crit_damage` | Danno Critico | 1.5 | ✗ |

### Advanced (7)
| key | display_name | default |
| --- | --- | --- |
| `effect_accuracy` | Precisione Effetti | 0.0 |
| `effect_resistance` | Resistenza Effetti | 0.0 |
| `healing_power` | Potere di Cura | 0.0 |
| `shield_power` | Potenza Scudo | 0.0 |
| `damage_reduction` | Riduzione Danni | 0.0 |
| `penetration` | Penetrazione | 0.05 |
| `dodge` | Schivata | 0.05 |

### Runtime keys (compat con `backend/battle_engine.py`)
- `attack` ↔ `physical_damage`/`magic_damage`
- `defense` ↔ `physical_defense`/`magic_defense`
- `crit_rate` ↔ `crit_chance`
- `dodge` ↔ `dodge_rate`
- `effect_accuracy` ↔ `hit_rate`
- `healing_power` ↔ `healing`

> Il runtime conserva il modello split-damage (phys/magic). Lo schema dichiara `attack/defense` come stats canoniche e `runtime_keys` come lane di proiezione, **senza forzare il runtime a cambiare**.

---

## 3. Role templates (9 ruoli)

| Role | Stat priorities | Identity |
| --- | --- | --- |
| **Tank** | hp, defense, damage_reduction, shield_power, effect_resistance | Soak damage, redirect threats, protect backline. |
| **DPS Melee** | attack, speed, crit_rate, crit_damage, penetration | Front-line burst & sustain damage. |
| **DPS Ranged** | attack, crit_rate, crit_damage, speed, penetration | Backline marksman, target priority. |
| **Mage AoE** | attack, effect_accuracy, speed, crit_rate | Caster ad area + DoT/debuff elementale. |
| **Assassin / Burst** | attack, crit_rate, crit_damage, penetration, speed, dodge | Single-target nuker + execute. |
| **Support / Buffer** | speed, shield_power, effect_resistance, hp | Team enabler. |
| **Healer** | healing_power, speed, hp, effect_resistance | Heal/cleanse/barrier. |
| **Control / Debuff** | effect_accuracy, speed, hp | Stun/slow/silence/debuff. |
| **Hybrid Special** | depends_on_kit | Iconic, rule-breaking (5★/6★). |

Ogni ruolo dichiara `weakness` e `patterns` di kit per slot (vedi JSON).

---

## 4. Rarity Stat Budget

| Native ★ | `stat_budget_x` | `max_stars` | Kit complexity |
| --- | --- | --- | --- |
| 1★ | 1.00 | 4★ | Basic + 0/1 passive semplice |
| 2★ | 1.30 | 6★ | Basic + 1 skill + 1 passive |
| 3★ | 1.65 | 8★ | Basic + skill + ultimate + 1 passive role-defining |
| 4★ | 2.05 | 10★ | 2 mecchaniche correlate, condizioni semplici |
| 5★ | 2.50 | 12★ | Kit completo, identity strong, sinergie |
| 6★ | 3.00 | 15★ | Iconic mechanic, kit firma |

> `stat_budget_x` è un **moltiplicatore astratto del budget statistiche totale**, distribuito secondo `role_stat_bias`. Non è il moltiplicatore HP. Numeri esatti finalizzati in RM1.21-B/C.

---

## 5. Skill Schema (4 slot canonici)

| slot | rarity_required | default_target | runtime_legacy |
| --- | --- | --- | --- |
| `basic_attack` | 1 | single_enemy | `nad` |
| `skill` | 2 | single_enemy | `sad` |
| `ultimate_or_special` | 3 | all_enemies | `sp` |
| `passive` | 1 | self | `passive` |

### Schema campi Skill
`id`, `name`, `description`, `type`, `target_type`, `damage_type`, `scaling_stat`, `multiplier`, `cooldown_turns`, `energy_cost`, `effects[]`, `animation_state`, `tags[]`, `unlock_condition`, `ignores_taunt`, `ignores_dodge`.

### Targeting rules (riferite al runtime esistente)
- **Default single-target**: Tank-first → nemico vivo più vicino (Manhattan, ties via index). Vedi `backend/battle_engine.py:select_default_single_target`.
- **Taunt priority**: massima sui single-target salvo `ignores_taunt=true`.
- **AoE taunt-immune**: target_type AoE/row/column/all_enemies/area NON intercettati da taunt.

---

## 6. Effect Types (14)

`damage`, `heal`, `shield`, `taunt`, `dot` (subtypes: burn/bleed/poison), `hot`, `buff`, `debuff` (legacy: weaken/defense_break/slow), `control` (subtypes: stun/freeze/silence/root), `cleanse` (legacy: purify), `revive` (5★+), `damage_reduction`, `mark`, `execute` (5★+, legacy: death_mark.instant_kill_chance), `summon_or_proxy` (5★+).

Ogni effect type dichiara `runtime_supported: true|false` e, dove utile, `runtime_keys_compat` per il mapping verso `ELEMENT_SKILLS`/`PASSIVE_SKILLS` esistenti.

---

## 7. Rarity Complexity (limiti hard)

| ★ | active | passive | eff/skill | ultimate | adv. cond. | iconic req. | text max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1★ | 1 | 1 | 1 | ✗ | ✗ | ✗ | 2 lines |
| 2★ | 1 | 1 | 1 | ✗ | ✗ | ✗ | 3 lines |
| 3★ | 1 | 1 | 2 | ✓ | ✗ | ✗ | 4 lines |
| 4★ | 2 | 1 | 2 | ✓ | ✓ | ✗ | 5 lines |
| 5★ | 2 | 2 | 3 | ✓ | ✓ | ✗ | 6 lines |
| 6★ | 2 | 2 | 3 | ✓ | ✓ | **✓** | 8 lines |

---

## 8. Esempi schema-validati

### 8.1 `greek_hoplite` — Tank / earth / 3★
- **Design intent**: tank base difensivo, taunt + DR + AoE armor break.
- **Kit (4 skill)**:
  - `basic_attack` → **Lancia Falangita**: damage single, 1.0× ATK, mapping `ELEMENT_SKILLS.earth.nad`.
  - `skill` → **Guardia di Falange**: taunt single-enemy 2 turni + damage_reduction 25% self 2 turni, CD 3.
  - `ultimate_or_special` → **Collasso Tettonico**: damage AoE 4.0× ATK + debuff defense -40% 3 turni, CD 5, energy 100. Mapping `ELEMENT_SKILLS.earth.sp`.
  - `passive` → **Resistenza Stoica**: damage_reduction +10% always-on + buff effect_resistance +0.15 always-on. Mapping ≈ `PASSIVE_SKILLS[3..4]`.
- **Asset note**: hit/death assets pending; UI/Battle contract OK.

### 8.2 `norse_berserker` — DPS Melee / fire / 3★
- **Design intent**: rage scaling sotto 50% HP, burn DoT su skill e ultimate.
- **Kit (4 skill)**:
  - `basic_attack` → **Colpo d'Ascia**: damage 1.1× ATK. Mapping `ELEMENT_SKILLS.fire.nad`.
  - `skill` → **Fendente Infuocato**: damage 2.5× ATK + DoT burn 5% target max_hp/turno × 3, CD 3. Mapping `ELEMENT_SKILLS.fire.sad`.
  - `ultimate_or_special` → **Tempesta Infernale**: AoE damage 5.0× ATK + DoT burn 8% × 3, CD 5, energy 100. Mapping `ELEMENT_SKILLS.fire.sp`.
  - `passive` → **Furia del Berserker**: trigger `self_hp_below_percent < 0.5` → +25% attack + +0.10 crit_rate fino a fine battaglia. Mapping ≈ `PASSIVE_SKILLS[4]` (Frenesia).
- **Asset note**: Battle runtime completo, death visually verified in Combat QA Lab.

> Entrambi gli esempi sono **schema-data only**: lo schema è abbastanza espressivo da rappresentare il runtime corrente di Hoplite/Berserker senza modificare nulla. Non sostituiscono `ELEMENT_SKILLS`/`PASSIVE_SKILLS` in `backend/battle_engine.py`.

---

## 9. Cosa **NON** fa RM1.21-A

- ❌ Non importa eroi nel DB.
- ❌ Non modifica `backend/battle_engine.py`, `ELEMENT_SKILLS`, `PASSIVE_SKILLS`.
- ❌ Non assegna numeri finali ai 101 eroi.
- ❌ Non modifica gacha, hero collection, battle picker, frontend UI.
- ❌ Non sovrascrive Character Bible.
- ❌ Non esegue `--apply` di nessuno script roster (RM1.20-A/B).

---

## 10. Next Phase Recommendation

- **RM1.21-B**: assegnare kit ufficiali per la batch dei 12 eroi **6★** (incluso Borea), seguendo `role_kit_templates` + `rarity_complexity[6]`. Solo schema-data (`data/design/heroes_kits_6star.json`), nessun import DB.
- **RM1.21-C**: stessa cosa per i 20 eroi **5★**.
- **RM1.21-D**: 24 eroi **4★**.
- **RM1.21-E**: 24 eroi **3★** (Hoplite/Berserker già esemplificati).
- **RM1.21-F**: 12 eroi **2★** + 8 eroi **1★**.

L'apply DB resta gated da RM1.20-C (filtri runtime) + env var di conferma.
