# SERVER-LIFECYCLE-CALENDAR-A — DESIGN-ONLY / AUDIT-ONLY FOUNDATION

**Task origin**: `SERVER-LIFECYCLE-CALENDAR-A`
**Status**: ✅ **PASS** (5/5 validator SLC-A + suite globale 243/243)
**Mode**: **DESIGN-ONLY / AUDIT-ONLY / READ-ONLY**
**Date (UTC)**: 2026-05-21

---

## 1. Files Created (19)

### Policy / schema (12 — `/app/data/design/server_lifecycle/`)
- `account_server_data_scope_policy_v1.json`
- `server_entity_schema_v1.json`
- `server_profile_schema_v1.json`
- `server_opening_cadence_policy_v1.json`
- `server_age_calendar_schema_v1.json`
- `server_age_calendar_example_first_180_days_v1.json`
- `global_real_world_event_override_policy_v1.json`
- `server_merge_eligibility_policy_v1.json`
- `event_banner_recovery_classification_policy_v1.json`
- `merge_recovery_season_policy_v1.json`
- `merge_catch_up_pool_schema_v1.json`
- `merged_mature_calendar_policy_v1.json`

### Audit JSON (read-only, generated)
- `server_shard_isolation_audit_v1.json`

### Validator Python scripts (6 — `/app/backend/scripts/`)
- `audit_server_shard_isolation_v1.py`
- `validate_server_lifecycle_policies_v1.py`
- `validate_server_age_calendar_schema_v1.py`
- `validate_server_merge_recovery_policy_v1.py`
- `audit_server_shard_isolation_safety_v1.py`
- `validate_server_lifecycle_calendar_a_combo.py`

### Documentation
- `/app/docs/divine/92_SERVER_LIFECYCLE_CALENDAR_A_FOUNDATION.md` (questo)

## 2. Files Modified (1)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` → 6 optional entries SLC-A (no validator esistente indebolito)

> **NIENTE** modificato in: `battle_engine.py`, `battle_core.py`, `combat.tsx`, `affinity_gift_spend.py`, gacha, roster, Character Bible, hero/skill/divine weapon catalogs, final_numbers, assets, AF2-N/Stage4 systems, auth, runtime routing.

---

## 3. Audit Results (Shard Isolation)
- **563 file Python** scansionati nel backend (read-only, **zero connessione DB, zero scrittura**)
- **15 categorie collezioni** auditate: accounts/users/auth, user_heroes, inventory, currencies, paid_currency_purchase, gacha_history, teams, story_progress, guilds, arena_rankings, affinity, gift_transaction_ledger, cosmetics, event_progress, server_config
- **379 candidate cross-server leak risks** identificati: file con keyword di collezioni server-bound che usano solo `user_id` SENZA `server_id` nel routing query/update
- **Priorità migration suggerite** (consultive, design-only):
  - **P1**: tutte le 13 collezioni server-bound che mostrano file con `user_id` only — necessitano `server_id` come chiave composta in una futura migration gated
  - **P2**: account_wide (`accounts_users_auth`, `paid_currency_purchase`) — non richiedono server_id

> ⚠️ Questi sono **rischi candidati**, non bug confermati: l'audit è statico/heuristico. Una migration plan dedicata sarà necessaria in una task futura.

## 4. Server Data Policy (account vs server)
- **Account-wide**: identity (account_id, auth, ban_state), economy (paid_currency_balance + ledger, purchase_history, VIP level), paid cosmetic ownership
- **Server-bound** (strict isolation): profile (level, created_at, last_login), free currency (gold, diamonds_free, event_currency), roster (heroes, star/level/equip/artifacts/skin/affinity/skills), inventory (materials, gifts, equipment, shards), teams, progress (story/tower/castle/clears/events/achievements), social (guild), competitive (arena, pvp_season, guild_war), affinity_and_gifts, achievement cosmetics, prestige_score_local, active_title_equipped, event_state
- **Mixed**: VIP level (account_wide) ma VIP claim_state e reward_inventory (server_bound); paid cosmetics (ownership account_wide, equip/bonus server_bound); paid currency balance (account_wide) ma spend ledger view (per_server)

## 5. Calendar Policy
- **Cadenza iniziale**: settimanale (Tuesday 10:00 UTC default), 1 server/settimana, accelerazione gated da capacity health check
- **Server selection**: nuovo account → newest open server (default); selezione manuale solo se open; join friend non consentito su closed/crowded
- **Capacity**: target 200 real active users, crowded 80%, closed 100%, reopen <60%
- **Server-age calendar schema v1**: 18 event_type, 4 recovery_classes, 17 entries esempio nei primi 180 giorni:
  - 9 must_catch_up (rush, summon meta, summon counter, server_boss, pvp_season, tower_trial, titan_hunt, guild_war_intro, castle_floor)
  - 4 optional_catch_up (login_starter, zodiac_house, affinity_event, skin_title)
  - 2 compress (material_week, top_up_minor)
  - 2 skip (lucky_wheel_minor, real_world_seasonal_filler)
- **Global real-world override**: 7 eventi (christmas, new_year, halloween, valentine, summer, anniversary, collab) P1, possono ritardare ma NON cancellare must_catch_up
- **Precedence**: P0 safety/maintenance > P1 real_world > P2 merge_recovery > P3 server_age_critical > P4 weekly_filler

## 6. Merge Policy
- **Eligibility inputs**: server_age_min 90d, active users <60, guild attivi <3, arena <10/g, queue health, revenue trend (30d), calendar gap analysis required, no active critical event (eccetto maintenance)
- **Decision**: minimum 4 segnali sotto soglia OR forced merge for safety
- **Protected states** (bloccanti salvo override): pvp_season, guild_war, anniversary, collab, real_world_seasonal
- **Approval chain**: product → liveops → sre → final_user_approval
- **Required artifacts**: merge_plan_json, calendar_gap_analysis_json, catch_up_pool_design_json, player_communication_plan

## 7. Recovery Classes
> **Invariant chiave**: *"Recover missed critical milestones, not skipped weeks."*

| Class | Descrizione | Esempi | Recovery Requirement |
|-------|-------------|--------|----------------------|
| **must_catch_up** | Meta/counter/progression-critical | meta/counter banner, system unlock (boss/tower/titan/castle/gw/pvp intro), rare non-substitutable materials | DEVE entrare nella banner pool o avere rerun-equivalent |
| **optional_catch_up** | Reruns, non-core heroes, medium prestige cosmetics, valuable farmable | non-core hero reruns, affinity events, zodiac non-critical, medium cosmetic, medium top-up | Bundle in compressed shop / shorter rerun |
| **compress** | Material weeks, minor shops, generic resource events, standard top-up | material week, minor shops, resource events, daily/weekly filler non-unique | Compressi in Merge Shop + Catch-Up Bundle (no banner) |
| **skip** | Generic lucky wheels, minor gold weeks, login filler, non-exclusive cosmetics | lucky_wheel, gold_week, login filler, low-impact top-up, non-exclusive rerunnable cosmetics | Omessi dalla recovery |

## 8. Catch-Up Pool (`merge_catch_up_pool_schema_v1.json`)
**Required fields**: merge_group_id, source_server_ids (≥2), target_server_id, baseline_progress_index, missed_milestone_ids, recovery_class, affected_server_ids, banner_pool, shop_pool, compressed_rewards, start_at, end_at, max_parallel_banners (1-6), pity_policy, purchase_limit_policy, fairness_notes, design_only=true, runtime_attached=false, battle_runtime_attached=false

**Default Merge Recovery Season**: 14 giorni (configurabile 14-21d)
- **Phases**: calendar_gap_analysis → catch_up_pool_build → recovery_window_execution → route_to_mature_calendar
- **Banner pool**: max 3 paralleli (5 per merge ad alto volume), pity ereditato best-per-account, purchase limits daily/weekly shared
- **Behavior rules**: non ereditare calendario più vecchio "blindly", non rigiocare settimane, scalabile a 10+ server merge via milestone pool

**Merged Mature Calendar**: stable reruns 30d, pvp season 28d, gw 7d, tower reset 30d, titan 14d, skin/title 30d. Reseed: ranking 14d, guild boost 21d, merge carnival 7d. `new_server_rush_not_replayed=true`.

**Example pool incluso**: merge_alpha_2026q3 (s4+s7+s11 → s4, baseline day 220).

## 9. Validators (5/5 PASS via combo)
- ✓ **SLC-A-SHARD-ISOLATION-AUDIT** → 563 file scanned, 15 categorie, 379 leak candidates, 0 DB writes
- ✓ **SLC-A-POLICIES** → 8 policy file verificati (design_only, progression_server_bound, free_curr_server_bound, paid_curr_account_wide, weekly cadence, target=200, P0-P4 precedence, age_threshold≥60, 4 recovery_classes, invariant key)
- ✓ **SLC-A-CALENDAR-SCHEMA** → schema completo (18 event_types, 4 recovery_classes, Borea forbidden) + 17 esempi con ≥4 must_catch_up + ≥1 compress + ≥1 skip
- ✓ **SLC-A-MERGE-RECOVERY** → merge_recovery (default 14d, key_invariant, no inherit oldest blindly, no replay weeks, 10+ scalable) + catch_up_pool (15 required fields) + mature (new_rush_not_replayed)
- ✓ **SLC-A-SHARD-ISOLATION-SAFETY** → audit_only=True, db_writes=False, db_connection_opened=False, no Borea leak nei VALORI, 0 mutating patterns nei nuovi script

## 10. Suite / Baseline
- `run_hero_skill_kit_validator_suite.py`: **Overall PASS** — `pass=243, fail=0, miss=0`
- Baseline diff combat files: **vuoto** (battle_engine.py, battle_core.py, combat.tsx invariati)
- Nessun altro file backend/frontend modificato in questo task

## 11. API smoke (read-only)
| Endpoint / azione | Esito |
|-------------------|-------|
| `/api/heroes` | 100 eroi, no borea leak ✅ |
| `/api/affinity/gift-spend/canary-status` | cap=50000, allowlist=2500, rl=redis ✅ |
| POST gift-spend `borea` | 404 ✅ |
| POST gift-spend `greek_borea` | 404 ✅ |
| POST gift-spend `primordial_gaia` | 404 ✅ |

## 12. Safety
- ✅ Nessun DB write / migration eseguita
- ✅ Nessuna connessione MongoDB aperta dai nuovi script (audit puramente file-system)
- ✅ Nessun runtime change al routing/auth/AF2-N/Stage4
- ✅ Nessuna UI aggiunta, nessuna merge execution implementata
- ✅ Nessun cambio a paid/free currency logic live
- ✅ Borea (`borea`, `greek_borea`, `primordial_gaia`) **mai esposto**: forbidden esplicito nello schema calendar (banner_id), invariant nelle policy, audit safety check sui valori, API /heroes invariata, 3/3 alias 404
- ✅ `design_only=true, runtime_attached=false, battle_runtime_attached=false` su tutti i 12 file policy/schema
- ✅ AF2-N/Stage4 state INVARIATO (cap=50000, allowlist=2500, broad_rollout=false, public_spend_ui=false)
- ✅ Nessun validator esistente indebolito

## 13. Warnings
- ⚠️ **Shard isolation audit**: 379 file backend mostrano riferimenti a collezioni server-bound usando solo `user_id` senza `server_id`. È **atteso** in un sistema pre-multi-server (l'attuale runtime opera a singolo shard). Una migration plan gated sarà necessaria PRIMA di aprire un secondo server.
- ⚠️ **Validator `audit_server_shard_isolation_safety_v1`** fix in-flight: il check Borea inizialmente flaggava la stessa chiave di policy `no_borea_exposure` come "leak". Risolto: ora il walker controlla solo i VALORI (non le chiavi) e salta i `sample_lines` (citazioni read-only di codice esistente che BLOCCA Borea).
- ⚠️ **Container Redis recurrence**: caduto 0× in questo task (auto-ripristinato da `ensure_redis_rate_limit.sh` durante warm-up).
- ⚠️ Tutte le policy hanno `notes` o `safety` che dichiarano esplicitamente design-only — nessuna applicazione runtime in questo task.

## 14. Final Recommendation
**SERVER-LIFECYCLE-CALENDAR-A PASS — SAFE TO HALT HERE.**

Tutte le acceptance gates rispettate:
- [x] design-only / audit-only files created
- [x] no DB writes / migrations
- [x] no runtime change (eccetto suite optional entries)
- [x] no battle/combat/gacha/roster/catalog/AF2-N changes
- [x] account/server policy creata
- [x] server calendar schema creato
- [x] merge recovery policy creata
- [x] shard isolation audit creato (379 risk candidates documentati)
- [x] tutti i validator PASS (5/5)
- [x] suite globale PASS (243/243)
- [x] baseline diff PASS (combat files no-diff)
- [x] Borea remains safe/hidden (3/3 alias 404, banner forbidden, audit-safe)

## 15. Suggested Next Tasks (NOT EXECUTED)
- 🟡 **SERVER-LIFECYCLE-B** — Server profile creation contract (design-only API contract, no implementation)
- 🟡 **SERVER-LIFECYCLE-C** — Migration plan from current single-shard to multi-server with server_id (gated, separate task)
- 🟡 **SERVER-LIFECYCLE-D** — Merge tooling design (offline plan generator + dry-run simulator, NO live merge)
- 🟡 **SERVER-LIFECYCLE-E** — Server selection endpoint contract (no writes, read-only API design)
- 🔴 Tutti richiedono esplicita approvazione user prima dell'esecuzione

---

*Documento generato automaticamente da SERVER-LIFECYCLE-CALENDAR-A — design-only / audit-only foundation.*
