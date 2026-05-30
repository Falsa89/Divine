# 202 — PROJECT_HERO_GEAR_PROGRESSION_BIBLE

**Pack ID:** `PROJECT_HERO_GEAR_PROGRESSION_BIBLE_PACK`
**Sentinella:** `v21`
**Public Sync Tag:** `PUBLIC_SYNC_TAG_RESYNC_v21_HERO_GEAR_PROGRESSION_BIBLE`
**Data UTC:** 2026-05-30
**Priorità:** P1 (design-lock prima di qualsiasi runtime upgrade)
**Verdict locale:** `PROJECT_HERO_GEAR_PROGRESSION_BIBLE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

---

## Conferma: DESIGN-ONLY (zero runtime change)
Questo pack **NON tocca** runtime: no hero upgrade, no gear upgrade, no Gemme/Rune, no Artifact/DW bonuses, no combat/battle_engine, no hero stats, no Character Bible, no gacha/pity, no Shop/BP/VIP/IAP unlock, no Artifact unhide, no server profiles live, no DB writes, no player data mutation, no economy live, no Tower/Guide/Home/Menu runtime, no final art/audio.

## Schema canonico (locked)

### Layer Hero (Track B + C)
| Layer | Axis | Stato runtime |
|---|---|---|
| **Hero Level** | XP lineare | present |
| **Hero Elevation / Quality Frame** | cornice colore E1..E7 + qualità +1/+2/+3 (NUOVO, separato da Star Up/Ascension) | design-only |
| **Star Up** | stelle/rarità via duplicati/frammenti | present |
| **Ascension** | breakthrough cap unlock via materiali ruolo/elemento | partial |
| **Skill Upgrade** | level Q/U via skill books | present |
| **Costellazioni** | endgame long-term duplicati/frammenti | design-only frozen |
| **Reincarnation** | endgame reset + carryover | design-only |

### Gear (Track D)
- **Gear Level cap canonico = +50** (non +20 legacy)
- **Stages**: early `0..10` → mid `11..20` → late `21..35` → endgame `36..50`
- **6 slot**: weapon / armor / helm / boots / gloves / accessory
- **Qualities**: common → mythic
- **Forge subsystems (design-only)**: enhance / fusion / reforge / enchant
- **Sockets per quality**: common=0, uncommon=1, rare=1, epic=2, legendary=3, mythic=4

### Gemme (Track E)
- **Gemme = socket-in-gear**, NON sull'eroe
- 6 famiglie (atk/hp/def/crit/speed/elemental) × tiers T1..T5
- Fusion design-only: 3×Tn → 1×T(n+1)

### Rune (Track F) ⭐
- **Rune = nome canonico unificato del layer hero-equipped**: `scroll` / `talismano` / `pergamena` / `sigillo` sono **ALIAS della stessa cosa**, non sistemi separati
- 4 slot per eroe (rune_1..rune_4)
- 6 famiglie (scroll_offensive, scroll_defensive, talisman_support, talisman_elemental, sigillo_role, sigillo_synergy)
- Tiers R1..R5 + set bonus 2/4 pezzi

### Artifact vs Divine Weapon (Track G)
| Sistema | Scope | Equip |
|---|---|---|
| **Artifact** | `global_account_roster` | **NON** equip su eroe (catalog read-only, mutations HTTP 423) |
| **Divine Weapon** | `per_hero_6star_only` | **character-bound**, separato da gear/gem/rune/artifact |

### Separazione 4-way (matrice DISTINCT)
gear ↔ gem ↔ rune ↔ artifact ↔ divine_weapon → **tutte DISTINCT** (vedi Track G).

## Material source mapping (Track H)
14 categorie mappate. Mode→material map:
- `tower_of_the_hells` → ascension_role + gear_pieces
- `material_raid_design_only` → ascension role/element + gear_enhance_stones
- `gem_dungeon_design_only` → gem_shards
- `rune_dungeon_design_only` → rune_scroll_drops
- `endgame_raid_design_only` → forge_reforge + fusion_catalysts

**Prerequisiti prima del runtime Material Raid**: elevation+gear_cap_50 runtime + BP delta contract.

## BP Delta integration contract (Track I)
- **Trigger layers**: tutti i 13 layer (hero + gear + gem + rune + artifact + DW)
- **Recompute strategy** design-only: `BP attivo = sum(per_hero_active_power)` con snapshot dei layer attivi
- **Overlay +BP/-BP runtime**: DEFERRED a `PROJECT_ACTIVE_BATTLE_POWER_DELTA_OVERLAY_PACK_FUTURE`

## Future runtime pack order (Track J — 11 fasi)
1. `PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PACK`
2. `PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK`
3. `PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PACK`
4. `PROJECT_GEM_SOCKET_RUNTIME_PACK`
5. `PROJECT_RUNE_SCROLL_TALISMAN_RUNTIME_PACK`
6. `PROJECT_MATERIAL_RAID_RUNTIME_PACK`
7. `PROJECT_ACTIVE_BATTLE_POWER_DELTA_OVERLAY_RUNTIME_PACK`
8. `PROJECT_DIVINE_WEAPON_6STAR_RUNTIME_PACK`
9. `PROJECT_ARTIFACT_GLOBAL_LIVE_APPLY_PACK`
10. `PROJECT_COSTELLAZIONI_RUNTIME_PACK`
11. `PROJECT_REINCARNATION_RUNTIME_PACK`

### Release gates
- Nessun runtime pack mergeato senza Bible PASS public-verified
- Nessun runtime pack può rompere combat formula / battle_engine (MD5 invariant)
- Ogni runtime pack deve avere Guide entry + Tutorial entry + material source mapping coerente con Track H

## File creati (12)
- 10 JSON tracks (A→J) in `data/design/hero_gear_progression_bible/`
- 1 proof marker JSON
- 1 doc `202_HERO_GEAR_PROGRESSION_BIBLE.md`
- 1 validator OPTIONAL `validate_project_hero_gear_progression_bible_v1.py`
- 1 tupla aggiunta nel suite runner (sentinel v21, count = 1)

## Risk / Debt
1. **Gear cap legacy +20 nel runtime esistente** → richiederà `PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK` per migrare hardcode numbers
2. **Hero Elevation / Quality Frame** completamente nuovo → richiede roll-out fasato in Phase 1
3. **Rune unification**: codice/UI legacy potrebbe usare termini diversi (scroll/talisman) → richiederà alias compatibility layer
4. **Artifact mutations HTTP 423**: ancora chiuse fino a `PROJECT_ARTIFACT_GLOBAL_LIVE_APPLY_PACK` (Phase 9)
5. **Material sources per Gem/Rune/Forge dungeon**: tutti design-only; richiedono runtime pack dedicati
6. **BP Delta overlay**: feature futura, nessun overlay runtime in questo pack
7. **9 OPTIONAL validator legacy MD5 invariant** ancora falliscono dal pack `PROJECT_HOME_MENU_REWIRING` (autorizzato), NON regressioni di questo pack

## Istruzioni Save to GitHub
1. Premere "Save to GitHub"
2. Verificare pubblicamente:
   - 11 JSON in `data/design/hero_gear_progression_bible/`
   - validator `validate_project_hero_gear_progression_bible_v1.py`
   - tupla `PROJECT-HERO-GEAR-PROGRESSION-BIBLE` nel suite runner
   - doc `202_HERO_GEAR_PROGRESSION_BIBLE.md`
3. Dopo verifica → promuovere a `PROJECT_HERO_GEAR_PROGRESSION_BIBLE_COMPLETE_PUBLIC_REPO_VERIFIED`
