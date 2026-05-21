# COSMETIC-SKIN-TITLE-SYSTEM-A — DESIGN-ONLY FOUNDATION

**Task origin**: `COSMETIC-SKIN-TITLE-SYSTEM-A`
**Status**: ✅ **PASS** (5/5 validator COSMETIC-A + suite globale 237/237)
**Mode**: **DESIGN-ONLY / READ-ONLY** (zero runtime, zero battle, zero DB write)
**Date (UTC)**: 2026-05-21

---

## 1. Files Created (20)

### Policy (5 — `/app/data/design/cosmetics/`)
- `cosmetic_system_policy_v1.json`
- `cosmetic_rarity_bonus_table_v1.json`
- `cosmetic_power_cap_policy_v1.json`
- `cosmetic_account_server_scope_policy_v1.json`
- `cosmetic_source_and_rerun_policy_v1.json`

### Schema (6 — `/app/data/design/cosmetics/`)
- `skin_catalog_schema_v1.json`
- `title_catalog_schema_v1.json`
- `cosmetic_bonus_schema_v1.json`
- `cosmetic_unlock_condition_schema_v1.json`
- `cosmetic_equipment_state_schema_v1.json`
- `cosmetic_prestige_score_schema_v1.json`

### Examples (2)
- `cosmetic_skin_examples_v1.json` (8 skin)
- `cosmetic_title_examples_v1.json` (12 titoli)

### Validators (5 — `/app/backend/scripts/`)
- `validate_cosmetic_system_policy_v1.py`
- `validate_cosmetic_schemas_v1.py`
- `validate_cosmetic_examples_v1.py`
- `audit_cosmetic_runtime_safety_v1.py`
- `validate_cosmetic_skin_title_system_a_combo.py`

### Documentation (1)
- `/app/docs/divine/91_COSMETIC_SKIN_TITLE_SYSTEM_A_FOUNDATION.md` (questo doc)

### Result JSONs auto-generati dai validator (4 — `_*.json`)
- `_validate_cosmetic_system_policy_v1_result.json`
- `_validate_cosmetic_schemas_v1_result.json`
- `_validate_cosmetic_examples_v1_result.json`
- `_audit_cosmetic_runtime_safety_v1_result.json`

## 2. Files Modified (1)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` → aggiunte 5 optional entries (`COSMETIC-SYSTEM-POLICY-A`, `COSMETIC-SCHEMAS-A`, `COSMETIC-EXAMPLES-A`, `COSMETIC-RUNTIME-SAFETY-A`, `COSMETIC-SKIN-TITLE-COMBO-A`)

> **NIENTE** modificato in: `battle_engine.py`, `battle_core.py`, `combat.tsx`, `affinity_gift_spend.py`, gacha, roster, Character Bible, hero/skill/divine weapon catalogs, final_numbers, assets, AF2-N/Stage4 systems.

---

## 3. Policy Summary
- **equipped_title_limit = 1** (un solo titolo attivo per player)
- **skin_bonus_scope = hero_bound**, **title_bonus_scope = team/player/account_server**
- **PvE cap totale ≤ 15%**, **PvP/Guild War ≤ 8%**, **Boss ≤ 10%**
- **Initial Rage cap**: PvE +20, PvP +10 (sum di tutti i cosmetici)
- **Speed cap**: PvE +10, PvP +5
- **Paid cosmetics**: ownership account-wide, **bonus solo dove equipaggiati**
- **Server-first / competitive cosmetics**: server_bound, **no rerun**
- **Prestige collection bonus**: capped PvE 5% / PvP 2%
- `design_only=true`, `runtime_attached=false`, `battle_runtime_attached=false` su tutti i file

## 4. Skin Schemas
Required fields: `skin_id, hero_id, display_name, rarity, source_type, scope_type, is_limited, rerun_policy, unlock_condition_ids, bonus_profile, asset_status, design_only, runtime_attached, battle_runtime_attached`

Bonus target: **hero** (skin sono hero-bound). Borea hero IDs (`borea`, `greek_borea`, `primordial_gaia`) sono in `forbidden_hero_ids` esplicito.

## 5. Title Schemas
Required fields: `title_id, display_name, rarity, source_type, scope_type, equip_limit_group="active_title", bonus_profile, unlock_condition_ids, seasonality, server_first_allowed, design_only, runtime_attached, battle_runtime_attached`

Bonus target: **team / player / account_server**. `max_active_title_per_player = 1`.

## 6. Bonus Schemas
**27 bonus types**: team_*_flat/pct, hero_*_pct, role/faction/element pct, initial_rage_flat, speed_flat, boss/pve/pvp/guild_war damage pct, damage_reduction_pct, healing_done_pct, shield_strength_pct, utility (gold/exp/affinity/gift/material pct), prestige_score_flat.

Resolver contract `cosmetic_power_cap_resolver_v1` definito ma `runtime_attached=false, battle_attached=false`. Order: skin → title → prestige → category subcap → global mode cap → flat initial_rage cap → flat speed cap.

## 7. Unlock Condition Schemas
**15 condition types**: topup_amount_event, paid_crystal_purchase, pvp_rank_reached, tower_floor_reached, weekly_castle_clears, zodiac_house_commander_hours, hero_affinity_level, titan_kill_count, guild_war_kill_streak, guild_war_kills_cumulative, event_wins_count, battle_power_reached, hero_star_reached, server_first_achievement, seasonal_event_completion.

Supporto AND/OR compound logic con max nesting depth = 2. Server-first: 1 player/server, server_bound, no rerun.

## 8. Example Seeds
**8 skin examples** (Premium Atena, Top-up Ares, PvP Apollo, Tower Era, Affinity Afrodite, Titan Artemide, Guild War Efesto, Hero-Star Zeus) — tutti `design_only=true`, asset_status `DESIGN_ONLY_NO_ASSET`, bonus entro rarity caps.

**12 title examples**:
- title_spezzatitani (epic / titan / account_wide) — boss_damage_pct 1.0%, team_atk_flat 80
- title_dominatore_arena (legendary / pvp_achievement / server_bound) — team_atk_pct 1.5%, pvp_damage_pct 1.0%, initial_rage_flat 6
- title_primo_sovrano_server (divine / server_first / server_bound) — team_hp_flat 2000, team_atk_flat 200, team_def_flat 200
- title_oracolo_gemelli (legendary / seasonal / account_wide) — initial_rage_flat 8, team_atk_pct 1.0%
- title_cacciatore_colosso (epic / titan / account_wide) — pve_damage_pct 1.0%, team_atk_pct 0.5%
- title_lama_gilda (legendary / guild_war / server_bound) — guild_war_damage_pct 1.5%, team_def_pct 1.0%
- title_scalatore_infinito (epic / tower / server_bound) — team_hp_flat 1000, team_def_pct 1.0%
- title_devoto_atena (rare / affinity / account_wide) — team_def_pct 0.5%, faction_bonus_pct 0.5% greek_olympian
- title_patrono_divino (mythic / top_up / account_wide) — gold/exp gain 4%, prestige_score_flat 32
- title_maestro_ascensione (legendary / hero_star / account_wide) — team_atk_pct 1.0%, team_hp_pct 1.0%
- title_custode_rocca (rare / event_wins / server_bound) — team_hp_flat 500, healing_done_pct 0.5%
- title_comandante_zodiacale (mythic / zodiac / server_bound) — team_atk_pct 1.5%, speed_flat 4, prestige_score_flat 24

Tutti `design_only=true`, `runtime_attached=false`, `battle_runtime_attached=false`. Nessuno fa riferimento a Borea.

## 9. Cap Policy
| Modalità | Total Cosmetic Power Cap | Initial Rage Cap | Speed Cap |
|----------|--------------------------|------------------|-----------|
| **PvE** | ≤ 15% | +20 | +10 |
| **PvP** | ≤ 8% (stricter) | +10 | +5 |
| **Guild War** | ≤ 8% | +10 | +5 |
| **Boss** | ≤ 10% | (PvE rules) | (PvE rules) |

Category subcaps: boss_damage 6%, pve_damage 5%, pvp_damage 3%, guild_war_damage 3%, damage_reduction 4%, healing_done 4%, shield_strength 4%, role/faction/element 2%.
Utility caps: gold/exp gain 10%, affinity/gift/material 5%.

**Invariant PvP-stricter-than-PvE**: validato da `validate_cosmetic_system_policy_v1.py`.

## 10. Account vs Server-bound Scope Policy
- **account_wide**: premium_paid, top_up_milestone, affinity_max, titan_hunt, hero_star, seasonal, top_up titles. Ownership replicato cross-server, **bonus attivo solo dove equipaggiato + valido**.
- **server_bound**: server_first, pvp_achievement, tower_achievement, guild_war, zodiac_house_commander, event_wins_milestone. **Non trasferibili in alcun caso**.
- Hybrid (paid + event): treated as account_wide ownership, server-of-origin bonus activation.

## 11. Validators
- ✓ **COSMETIC-SYSTEM-POLICY-A** → policy file consistency (PvP stricter, IR/Speed caps, equip_title=1, scope rules)
- ✓ **COSMETIC-SCHEMAS-A** → schema completeness (27 bonus types, 15 condition types, equip_limit_group=active_title, forbidden_hero_ids include Borea)
- ✓ **COSMETIC-EXAMPLES-A** → 8 skin + 12 title, bonus values entro rarity caps, no Borea hero_id, all design_only
- ✓ **COSMETIC-RUNTIME-SAFETY-A** → no runtime imports/mutations in scripts, no Mongo writes, no battle attachment, combat guardrails clean
- ✓ **COSMETIC-SKIN-TITLE-COMBO-A** → composite (4 sub-validator)

## 12. Suite / Baseline
- `run_hero_skill_kit_validator_suite.py`: **Overall PASS** — `pass=237, fail=0, miss=0`
- Baseline diff combat files: **vuoto** (`battle_engine.py`, `battle_core.py`, `combat.tsx` invariati)
- Affinity route: nessun cambio in questo task (la modifica V30 Cap S2 è pre-esistente)

## 13. API Smoke (read-only)
| Check | Esito |
|-------|-------|
| `/api/heroes` | 100 eroi, no borea leak ✅ |
| `/api/affinity/gift-spend/canary-status` | cap=50000, allowlist=2500, rl=redis ✅ |
| POST gift-spend `borea` | 404 ✅ |
| POST gift-spend `greek_borea` | 404 ✅ |
| POST gift-spend `primordial_gaia` | 404 ✅ |

## 14. Runtime Safety
- ✅ Nessuna applicazione runtime di bonus cosmetici
- ✅ Nessun wiring a battle/combat
- ✅ Nessuna mutazione DB (no MongoDB writes)
- ✅ Nessuna migration creata
- ✅ Nessun endpoint POST/PUT/PATCH/DELETE aggiunto
- ✅ Nessun import runtime nei nuovi script (no motor, no pymongo, no redis.Redis, no requests.post)
- ✅ Nessun cambio a AF2-N / Stage4 state (cap=50k, allowlist=2500, broad_rollout=false, public_spend_ui=false, battle_wiring=false invariati)
- ✅ Borea (`borea`, `greek_borea`, `primordial_gaia`) **mai esposto**: catalog schema ha `forbidden_hero_ids` esplicito + esempi audit-verificati + API /heroes invariata + 3/3 alias 404
- ✅ Frontend audit: 7 file referenziano keyword `cosmetic|skin_|title_` ma **0 mutazioni** verso endpoint cosmetic

## 15. Warnings
- ⚠️ Durante l'esecuzione iniziale, 2 title example (`title_spezzatitani`, `title_cacciatore_colosso`) avevano bonus pct sopra il rarity cap di epic (1%). Fix in-flight: valori abbassati a 1.0% (entro cap).
- ⚠️ Lo script `audit_cosmetic_runtime_safety_v1.py` contiene di proposito i pattern proibiti come stringhe per il match → self-skip aggiunto + esclusione dei result JSON `_*.json` dalla scansione.
- ⚠️ Container Redis caduto 1× durante il task, auto-ripristinato da `/app/ops/ensure_redis_rate_limit.sh` (issue ambiente pre-esistente, non bloccante).
- ⚠️ Resolver `cosmetic_power_cap_resolver_v1` è **solo contratto design-only**. Nessuna implementazione runtime; attivazione futura richiede esplicita approvazione user + task separato gated.

## 16. Final Recommendation
**COSMETIC-SKIN-TITLE-SYSTEM-A PASS — SAFE TO HALT HERE.**

Tutte le acceptance gates rispettate:
- [x] design-only files created
- [x] no runtime application
- [x] no battle/combat changes
- [x] no affinity_gift_spend changes (in questo task)
- [x] no gacha/roster/catalog changes
- [x] no DB writes / migrations
- [x] no public UI changes
- [x] tutti i validator PASS (5/5)
- [x] suite globale PASS (237/237)
- [x] baseline diff PASS (combat files no-diff)
- [x] Borea remains hidden/safe
- [x] AF2-N/Stage4 state NOT modified (cap=50k, allowlist=2500, broad_rollout=false invariati)

## 17. Suggested Next Tasks (NOT EXECUTED)
- 🟡 **COSMETIC-B** — Inert resolver preview (design-time bonus aggregator senza side effects; deferred runtime)
- 🟡 **COSMETIC-C** — Read-only UI catalog preview (galleria skin/titoli, no equip mutation, no public exposure)
- 🟡 **COSMETIC-D** — Unlock tracking design (schema + counters design-only)
- 🟡 **COSMETIC-E** — Runtime gated bonus resolver (resolver attivo ma **non** battle-attached, gated come AF2-N stage4)
- 🔴 Tutti i task COSMETIC-B…E richiedono esplicita approvazione user prima dell'esecuzione

---

*Documento generato automaticamente da COSMETIC-SKIN-TITLE-SYSTEM-A — design-only foundation.*
