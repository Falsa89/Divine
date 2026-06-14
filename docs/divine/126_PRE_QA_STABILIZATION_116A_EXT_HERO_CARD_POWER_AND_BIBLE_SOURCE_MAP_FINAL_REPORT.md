# 126_PRE_QA_STABILIZATION_116A_EXT_HERO_CARD_POWER_AND_BIBLE_SOURCE_MAP_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_116A_EXT_HERO_CARD_POWER_AND_BIBLE_SOURCE_MAP_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-116A-EXT): `05511cbf779ad567795025b94856fbdaa947f31b`
- Pack 116A-EXT commit:    `f30bfe11d4e3419d6e2349731eb3f424875a2550`
- Report/self-ref:         `0ce087f8a2f7d1d61f069731ed6303042ebb20e7`

> **Commit policy** (preservata da 115F/116A FIX-A): MAI `git add -A` / `git add .`. Tutti i file aggiunti con `git add -- <path>` esplicito.

## Scope / files changed
**Created**:
- `data/design/battle_power/battle_power_bonus_source_map_v1.json` — source-of-truth map (design-only, read-only, 4 sezioni, 21 entries totali, 22 Bible citate).
- `backend/scripts/validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py` — validator 116A-EXT (11 check).
- `docs/divine/126_PRE_QA_STABILIZATION_116A_EXT_HERO_CARD_POWER_AND_BIBLE_SOURCE_MAP_FINAL_REPORT.md` — questo file.

**Modified**:
- `backend/utils/battle_power.py` — semantica `active_power_sources_now` / `deferred_canonical_power_sources` / `excluded_from_current_formula_only` (NO change numerico).
- `backend/server.py` — `/api/user/heroes` server-scoped: arricchimento `power`/`battle_power_formula_version`/`battle_power_source` + batch-load `db.heroes.find({"id": {"$in": [...]}})` (elimina N+1 storico).
- `backend/routes/hero_progression.py` — `/api/hero/full-detail/{user_hero_id}` ora usa `compute_hero_battle_power_v1` come fonte di `power` (no piu' `calculate_hero_power` legacy player-facing).
- `backend/scripts/run_pre_qa_safety_validator_suite.py` — registrato 116A-EXT come 17ª voce.
- `frontend/app/(tabs)/heroes.tsx` — badge `⚡ <power>` sulla card (con fallback `—`); aggiunto sort "Potenza"; nessuna chiamata N+1 (power letto da payload `/api/user/heroes`).

**Untouched** (vincoli rispettati):
- Bible esistenti sotto `data/design/**`: **0 file modificati** (solo letti/citati nel source map).
- `battle_engine.py`, combat runtime, tower runtime, gacha rates, Character Bible, skill catalog data: **untouched**.
- `frontend/app/(tabs)/home.tsx`, `(tabs)/battle.tsx`, `hero-detail.tsx`: invariati rispetto a Pack 116A.
- Pack 115F / 116A FIX-A repo hygiene: **0 .pyc / 0 __pycache__ tracciati nel git index**.

## Source map design-only (`battle_power_bonus_source_map_v1.json`)

**Scope dichiarato**: `design_only_read_only` · `is_runtime=false` · `do_not_use_for_runtime_resolution=true` · `non_authoritative_for_balance=true` · `battle_power_formula_version=battle_power_v1_preqa_derived`.

### Sezione `active_power_sources_now` (4 sources — attivi nel calcolo 116A)
| source_id | battle_power_role | Bible ref |
|---|---|---|
| `hero_base_stats` | primary_additive_base | `hero_stats_schema.json` |
| `hero_level` | multiplicative_5pct_per_level | `hero_gear_progression_bible/B_*.json` |
| `hero_rarity_native` | multiplicative_20pct_per_rarity | `hero_stats_schema.json` |
| `hero_stars_user` | additive_star_bonus_capped (+3% per stella, capped +15%) | `B_*.json`, `I_bp_delta_*.json` |

### Sezione `deferred_canonical_power_sources` (13 sources — canoniche, future Pack 117+)
| source_id | Bible ref |
|---|---|
| `ascension` | `B_*.json`, `I_bp_delta_*.json` |
| `skill_upgrade_non_final_numbers` | `B_*.json` (NB: `skill_package.*.final_numbers` resta foundation_draft preview-only per Pack 115G) |
| `hero_elevation_quality_frame` | `B_*.json` |
| `constellations` | (legacy GET HTTP 423 da Pack 115G) |
| `reincarnation` | `B_*.json` |
| `gear_level` | `D_gear_progression_bible_v1.json` |
| `gear_quality_fusion` | `D_*.json` |
| `gem_socket` | `E_gem_socket_system_bible_v1.json` |
| `rune_equip` | `F_rune_scroll_talisman_system_bible_v1.json` |
| `artifact_global` | `artifacts/*` + `G_artifact_divine_weapon_separation_rules_v1.json` |
| `divine_weapon` | `divine_weapons/*` + `G_*.json` |
| `team_synergy` | `team_synergies_v2_initial_10.json`, `synergy_codex_ui_requirements.json`, `backend/utils/team_synergy_v2_calculator.py`, `backend/synergy_system.py` |
| `cosmetics_skins_titles_capped` | `cosmetics/*` (6 Bible) |

### Sezione `non_power_or_display_only_sources` (4 sources)
`skin_pure_display`, `title_decorative_only`, `hero_class`, `hero_element`.

### Sezione `unknown_requires_source_confirmation` (3 sources, richiedono chiarimento GM)
`guild_or_server_bonus`, `affinity_or_sanctuary_bonus`, `prestige_or_account_wide_bonus`.

## Backend changes

### `backend/utils/battle_power.py` — semantic refinement (NO change numerico)
- Aggiunti simboli: `BATTLE_POWER_ACTIVE_POWER_SOURCES_NOW` (4), `BATTLE_POWER_DEFERRED_CANONICAL_POWER_SOURCES` (13), `BATTLE_POWER_EXCLUDED_FROM_CURRENT_FORMULA_ONLY` (alias di `BATTLE_POWER_EXCLUDED_SOURCES`), `BATTLE_POWER_BONUS_SOURCE_MAP_PATH`.
- `build_battle_power_metadata()` espone: `active_power_sources_now`, `deferred_canonical_power_sources`, `excluded_from_current_formula_only`, `bonus_source_map_path` accanto ai campi legacy (`excluded_power_sources`, `included_hero_fields`, `included_user_hero_fields`) preservati per backward compat con validator 116A.
- **NESSUN cambiamento alla funzione `compute_hero_battle_power_v1`**.

### `backend/server.py` — `/api/user/heroes?server_id=...`
- Aggiunto batch-load: `await db.heroes.find({"id": {"$in": [...]}}).to_list(2000)` → **elimina N+1 storico** (era `find_one` per ogni `user_hero`).
- Per ogni entry: arricchito con `"power": compute_hero_battle_power_v1(hero, uh)`, `"battle_power_formula_version": "battle_power_v1_preqa_derived"`, `"battle_power_source": "derived_read_only"`.
- **Solo branch server-scoped** modificato; il branch account-wide-legacy-DEPRECATED resta intoccato (per design — le UI player-facing devono passare server_id).

### `backend/routes/hero_progression.py` — `/api/hero/full-detail/{user_hero_id}`
- Import: `from utils.battle_power import compute_hero_battle_power_v1 as _compute_hero_bp_v1, BATTLE_POWER_FORMULA_VERSION as _BP_FORMULA_VERSION_116A, BATTLE_POWER_SOURCE as _BP_SOURCE_116A`.
- Response: `"power": _compute_hero_bp_v1(hero, uh)`, `"battle_power_formula_version": _BP_FORMULA_VERSION_116A`, `"battle_power_source": _BP_SOURCE_116A`.
- **`calculate_hero_power` legacy NON e' piu' la fonte finale player-facing in questa route**.

## Frontend changes

### `frontend/app/(tabs)/heroes.tsx`
- Badge compatto sulla card eroe: `⚡ <power>` con `Number(h.power).toLocaleString()` quando `power > 0`, fallback `⚡ —` (`\u2014`) altrimenti. **Mai falso `0`.**
- Sort "Potenza" aggiunto: usa `h.power` dal payload (no chiamate N+1). Eroi senza power valido (fallback) finiscono in coda.
- Stili: `cardPower`, `cardPowerIcon`, `cardPowerVal`, `cardPowerEmpty` (8pt scale, COLORS.gold).
- **No chiamate `apiCall` dentro il render della card** (verificato dal validator check [7] via bracket-matched scan).

## Validator results

### `python3 backend/scripts/validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py`
**PASS — 11/11**:
1. `[1] source map present + valid JSON OK`
2. `[2] source map has 4 canonical sections with required fields OK`
3. `[3] source map cites all required Bibles + all references resolvable OK` (22 Bible verificate)
4. `[4] utility battle_power.py exposes active/deferred + bonus_source_map_path OK`
5. `[5] /api/user/heroes server-scoped enriched with power (batch-load, no N+1) OK`
6. `[6] hero/full-detail uses compute_hero_battle_power_v1 as power source OK`
7. `[7] heroes.tsx card: ⚡ badge + fallback '—' + no N+1 OK`
8. `[8] pre-QA safety suite registers 116A-EXT validator OK`
9. `[9] no out-of-scope imports across pack-116A-EXT scoped files OK`
10. `[10] no runtime writes to battle_power_bonus_source_map OK`
11. `[11] runtime metadata endpoint shows active/deferred semantics OK` *(backend up)*

### `python3 backend/scripts/validate_pre_qa_stabilization_116a_battle_power_foundation.py`
**PASS — 11/11** (compat preserved da Pack 116A originale).

### `python3 backend/scripts/validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py`
**PASS — 7/7**.

### `python3 backend/scripts/sweep_repo_hygiene.py`
`clean = true` · `tracked __pycache__ = 0` · `tracked .pyc = 0`.

### `python3 backend/scripts/run_pre_qa_safety_validator_suite.py`
**PASS — 17/17** (verdict: `PRE_QA_SAFETY_SUITE_PASS`):

| # | Entry | Stato |
|---|---|---|
| 1–14 | Pack 113 → 115F | PASS *(invariati)* |
| 15 | Validator 115G Skill/Artifact Semantic Cleanup | PASS |
| 16 | Validator 116A Battle Power Foundation | PASS |
| 17 | **Validator 116A-EXT Hero Card Power + Bible Source Map** | **PASS** |

Totali: 17 · PASS: 17 · FAIL: 0 · SKIPPED: 0 · backend_up: true.

## Curl evidence (backend up, test user effimero `qa116aext_<timestamp>@test.com`)

```
# Setup user + PSP + starter heroes (read-only flow esistente)
POST /api/register                       -> 200 (token issued)
POST /api/psp/ensure?server_id=s1        -> 200 (PSP created)
POST /api/psp/starter/claim?server_id=s1 -> 200 (3 starter user_heroes created)

# Endpoint evidence
GET /api/user/heroes?server_id=s1        -> HTTP 200
  count: 3
  hero[0]: power=312, formula=battle_power_v1_preqa_derived,
           source=derived_read_only, name="Recluta di Falange", lv=1, stars=1
  hero[1]: power=312, name="Arciera di Bosco", lv=1, stars=1
  hero[2]: power=312, name="Accolita del Santuario", lv=1, stars=1

GET /api/hero/full-detail/<user_hero_id> -> HTTP 200
  power=312, formula=battle_power_v1_preqa_derived,
  source=derived_read_only, name="Recluta di Falange", level=1, stars=1

GET /api/battle-power/metadata           -> HTTP 200
  active_power_sources_now:        ['hero_base_stats', 'hero_level',
                                    'hero_rarity_native', 'hero_stars_user']
  deferred_canonical_power_sources: 13 entries
                                    ['ascension', 'skill_upgrade_non_final_numbers',
                                     'hero_elevation_quality_frame', 'constellations',
                                     'reincarnation', 'gear_level', 'gear_quality_fusion',
                                     'gem_socket', 'rune_equip', 'artifact_global',
                                     'divine_weapon', 'team_synergy',
                                     'cosmetics_skins_titles_capped']
  excluded_from_current_formula_only count: 14
  bonus_source_map_path:           data/design/battle_power/battle_power_bonus_source_map_v1.json
```

> **Verifica numerica diretta** (read-only DB query): per uno user con 353 user_heroes a level=100 stars=12, `compute_hero_battle_power_v1` produce `power_116a = 38460`. Coerente con la formula 116A (no balance final).

## Frontend smoke
- Expo Metro: `Web Bundled 28139ms ... 2767 modules` → bundle servito su `:3000` con HTTP 200.
- Nessun crash da `Cannot read property` sul card render (selettori difensivi `typeof h.power === 'number' && h.power > 0`).

## Safety invariants (preservate)
- DB writes: **0** (helper puro + arricchimento read-only su path GET; nessun `$set`/`$inc`/`insert_one`/`update_one`/`delete_one`).
- Reward live: **false**. Gacha live: **false**. IAP/payment: **false**.
- Combat authoritative activation: **false** (`combat_authoritative=false` invariato).
- Battle engine: **untouched**. Combat runtime: **untouched**. Tower: **untouched**.
- Character Bible: **untouched** (solo letta/citata nel source map).
- Skill catalog data files: **untouched**.
- gacha rates: **untouched**.
- `data/design/**` esistenti (Bibles): **0 modificati**; solo NUOVO file `data/design/battle_power/battle_power_bonus_source_map_v1.json` (cartella nuova).
- Artifact / Divine Weapon / Cosmetic live activation: **false** (deferred dichiarato esplicitamente nel source map).
- Synergy battle activation: **false** (deferred).
- Gear / Gem / Rune live activation: **false** (deferred).
- Skill `final_numbers` as final balance: **false** (preservato Pack 115G `foundation_draft preview-only`).
- Red Dot: **non implementato** (verificato out-of-scope).
- Chat/Bot cleanup: **non implementato** (verificato out-of-scope).
- N+1 chiamate per card: **eliminate** (batch-load `db.heroes.find({"id": {"$in": [...]}})`).
- N+1 chiamate UI: **nessuna** (power letto da payload, verificato dal validator).
- Tracked `.pyc` / `__pycache__` in git: **0** (hygiene 115F/116A FIX-A preservate).

## Truth statement — "Esclusi" vs "Deferred canonical"
**Correzione semantica importante (richiesta dal pack):**

Pack 116A aveva una lista `excluded_power_sources` che poteva essere interpretata come "esclusi per sempre". Pack 116A-EXT chiarisce ufficialmente:

| Old terminologia (116A) | Nuova terminologia (116A-EXT) | Significato |
|---|---|---|
| `excluded_power_sources` | `excluded_from_current_formula_only` | NON applicato in 116A, **MA non escluso per sempre** |
| (n/a) | `active_power_sources_now` | Attivamente incluso nel calcolo 116A |
| (n/a) | `deferred_canonical_power_sources` | Sorgente canonica futura, in attesa di resolver runtime-safe (Pack 117+) |

Il source map e' la fonte autoritativa di questa classificazione. Le Bible esistenti restano la fonte numerica/design di ogni sistema.

## Deferred (post-116A-EXT roadmap)
- **116B — Chat/Bot quality + legacy chat cleanup**: cleanup UI/routing chat-bot, separato.
- **116C — Red Dot notification badge foundation**: badge, separato.
- **117+ — Resolver runtime-safe per i 13 deferred canonical**: gear, gem, rune, artifact_global, divine_weapon, team_synergy, cosmetics cappati, ascension, elevation, reincarnation, constellations, skill_upgrade. Ognuno richiede un Pack dedicato con resolver server-scoped + cap chiari + balance pass.

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 116B** prima del re-audit esplicito.
