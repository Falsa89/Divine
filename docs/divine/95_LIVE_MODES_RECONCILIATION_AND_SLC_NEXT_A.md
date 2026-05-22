# 95 — LIVE-MODES-RECONCILIATION-A + SLC-NEXT-PREP-A

> **Status**: ✅ PASS · **Mode**: DESIGN-ONLY / CONTRACT-ONLY / READ-ONLY / AUDIT-ONLY
> **Date (UTC)**: 2026-05-22 · **Suite globale**: 278 PASS / 0 FAIL / 0 MISS

---

## 1. File creati

### JSON design

In `/app/data/design/live_modes/`:
- `divine_live_mode_benchmark_reconciliation_v1.json` (16 modalità, mapping corretto)
- `divine_live_mode_calendar_v1.json` (8 finestre live, orari approvati)
- `divine_live_mode_reward_framework_v1.json` (10 categorie reward + 6 anti-P2W)
- `divine_live_mode_broadcast_policy_v1.json` (`max_visible_announcements=3`)
- `divine_live_mode_benchmark_risk_policy_v1.json` (12 pattern vietati/cappati)
- `divine_live_mode_war_avatar_usage_v1.json` (display-only, no combat mutation)
- `sanctuary_housing_dimora_divina_design_note_v1.json` (design note, no runtime)

In `/app/data/design/server_lifecycle/`:
- `slc_next_after_be_route_patch_dryrun_plan_v1.json` (SLC-F plan, `execute_now=false`)
- `slc_next_after_be_blocker_status_v1.json` (7 blocker documentati)
- `slc_next_after_be_recommended_sequence_v1.json` (SLC-F/G/D/H, tutti `execute_now=false`)

In `/app/data/design/system_safety/`:
- `live_modes_slc_next_readiness_rollup_v1.json`

### Script Python (`/app/backend/scripts/`)
- `_live_modes_common.py` (helper)
- `validate_live_mode_benchmark_reconciliation_v1.py`
- `validate_live_mode_calendar_v1.py`
- `validate_live_mode_reward_framework_v1.py`
- `validate_live_mode_broadcast_policy_v1.py`
- `validate_live_mode_benchmark_risk_policy_v1.py`
- `validate_sanctuary_housing_dimora_divina_note_v1.py`
- `audit_live_mode_reconciliation_runtime_safety_v1.py`
- `validate_slc_next_after_be_plan_v1.py`
- `validate_live_modes_slc_next_combo_v1.py`

### Doc
- `/app/docs/divine/95_LIVE_MODES_RECONCILIATION_AND_SLC_NEXT_A.md` (questo file)

---

## 2. File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py`
  — aggiunti 9 entry OPTIONAL per LIVE-MODES + SLC-NEXT. Nessun REQUIRED rimosso o indebolito.

Nessun altro file di codice o runtime è stato modificato.

---

## 3. Mapping corretto delle 16 modalità

| ID | Nome modalità Divine | Bleach Online | Altri benchmark / Note |
|----|----------------------|---------------|------------------------|
| 1  | Giudizio di Asgard   | **non presente** | Epic Seven Dagger Sicar, Future Fight World Event |
| 2  | Cammino dell'Ade     | **Hueco Mundo Attack** | — |
| 3  | Scala dell'Olimpo    | non presente | Summoners War Trial of Ascension, Idle Angels Sky-tower, AFK Arena tower |
| 4  | Sigilli degli Dei    | non presente | BLEACH Brave Souls Senkaimon rules, Raid Faction Wars, Genshin Imaginarium Theater |
| 5  | Torre degli Inferi   | non Bleach Online | **SAO Memory Defrag Floor Clearing Castle** / BLEACH Brave Souls Senkaimon |
| 6  | Troni dell'Eclissi   | non presente | Nikke Solo/Union Raid, Mythic Heroes Pantheon, Raid Hydra, Epic Seven Advent |
| 7  | Prove del Pantheon   | non presente | Epic Seven Dagger Sicar, Genshin objectives, BBS Challenge Orders |
| 8  | Abisso del Colosso   | non presente | Raid Doom Tower, Mythic Heroes Hades' Hell, Future Fight World Boss |
| 9  | Crepuscolo dei Titani| **Void Region** | — |
| 10 | Giudizio delle Stirpi| **Evil Spirit** | — |
| 11 | Fronti del Valhalla  | **Guild War** | — |
| 12 | Guerra dei Tre Troni | non Bleach | **Marvel Future Fight Alliance Conquest** |
| 13 | Fame del Behemoth    | non presente | Raid Clan Boss, Nikke Union Raid, Mythic Guild Daemons |
| 14 | Furie del Pantheon   | non presente | Nikke Union Raid, Mythic Heroes Wardragons |
| 15 | Titanomachia         | **Protect Seireitei** | — |
| 16 | Assalto del Ragnarök | **Ryoka Attack** | — |

### Mapping errati esplicitamente corretti
- **Troni dell'Eclissi**: prima mappato erroneamente su Bleach Online Seireitei Soul Palace → ora correttamente `not_present` (usare meccaniche Divine + confronto con sistemi seasonal multi-boss/modifier/ranking).
- **Giudizio di Asgard**: prima collegato a una trial Bleach incerta → ora `not_present` (usare benchmark non-Bleach).
- **Titanomachia**: prima descritto come "generic titan boss" → ora correttamente **Protect Seireitei** (assedio gilda).

---

## 4. Sintesi meccaniche per modalità

| Modalità | Tipo | Note chiave |
|---|---|---|
| Giudizio di Asgard | survival competitive gauntlet | 10 roster simili, HP/rage/team persistenti, milestone 33/66/100 |
| Cammino dell'Ade | branching survival run | percorsi ramificati, shop, santuari cura/resurrezione, buff 1 di 3, stato persistente |
| Scala dell'Olimpo | wave endurance progression | ondate classiche + varianti elementali, HP/rage persistenti, ripartenza poco sotto max precedente |
| Sigilli degli Dei | special-rule tactical | sequenze brevi con vincoli elemento/ruolo/fazione/composizione |
| Torre degli Inferi | seasonal floor tower w/ roster lock | scalata stagionale, boss floor, lock eroi, rollout 25→50→75→100 piani |
| Troni dell'Eclissi | seasonal multi-boss modifier ranking | leaderboard per boss + classifica stagionale, modifier elementali |
| Prove del Pantheon | objective tactical challenge | win in X turni, no caduti, composizioni richieste |
| Abisso del Colosso | individual boss survival ladder | sequenza boss/mini-boss, stato non resettato |
| Crepuscolo dei Titani | server-wide titan boss | lun/mer/ven 20:30–21:30, respawn 60s, reward partecipazione/damage/kill |
| Giudizio delle Stirpi | faction live boss | boss derivato dal team più forte di un player della fazione, finestre 09–10 e 14–15, 1 reward/giorno |
| Fronti del Valhalla | guild lane front war | giornaliero 17–18, avanzata progressiva, scontri istantanei |
| Guerra dei Tre Troni | three-guild territory conquest | mar/gio/sab 22–23 battaglia, lun/mer/ven prep, 3 zone speciali con buff non dominanti |
| Fame del Behemoth | infinite guild boss | barre HP progressive, reward barre+damage, prima battaglia manuale |
| Furie del Pantheon | guild elemental raid | aperto da GM/ruoli autorizzati spendendo guild activity, ondate + boss finale |
| Titanomachia | major guild fortress siege | giornaliero 15:30–16:30, guardiano → cancello esterno → interno, HP persistenti |
| Assalto del Ragnarök | live wave attack | finestre 11–12 e 19–20, reward da ondata raggiunta + leaderboard, 1 reward/giorno |

Nota: **Scrigni dell'Elisio** (trial co-op gioielli sempre disponibile, prime 3 run rewarded/giorno) è inclusa concettualmente nel pacchetto di meccaniche Divine come trial supplementare (non rientra tra le 16 live/special competitive).

---

## 5. Benchmark imports

Patterns da importare in modo controllato (vedi `divine_live_mode_reward_framework_v1.json` e i campi `import_from_benchmark` nelle singole modalità):

- **Cammino dell'Ade** ← Hueco Mundo Attack: daily reset, coin exchange shop, sequenza nemici progressiva, revive controllato
- **Torre degli Inferi** ← SAO MD Floor Clearing Castle / BBS Senkaimon: floor clearing identity, pacing release piani, lock eroi, special floor rules, medal exchange, clear time tracking
- **Fronti del Valhalla** ← Guild War Bleach: registrazione, lane selection, auto-resolved clashes, win streak scoring, ranking personale + gilda
- **Guerra dei Tre Troni** ← Marvel Future Fight Alliance Conquest: 3 gilde su mappa a zone, spawn cardinale, conquista solo confinanti, zone-punti, zone speciali
- **Assalto del Ragnarök** ← Ryoka Attack: wave pacing, damage ranking, participation rewards, threshold buffs, revive timer

---

## 6. Rischi benchmark vietati/cappati

`divine_live_mode_benchmark_risk_policy_v1.json` lista 12 pattern vietati o cappati:

1. paid cooldown clear in modalità competitive
2. paid morale boost che influisce sul ranking
3. VIP skip in modalità competitive
4. paid revive che decide leaderboard
5. uncapped extra entries
6. final blow come reward principale
7. occupation bonus troppo alti
8. guild donation power scaling troppo alto
9. ranking-only meta-critical rewards
10. server transfer paid-only
11. public spend UI senza approvazione finale
12. STACK-G battle wiring senza approvazione resolver

`divine_live_mode_reward_framework_v1.json` rinforza la stessa policy con 6 regole anti-P2W esplicite.

---

## 7. Calendario live (validato esattamente)

| Orario | Modalità | Frequenza | Note |
|---|---|---|---|
| 09:00–10:00 | Giudizio delle Stirpi | daily | one rewarded participation/day across windows |
| 11:00–12:00 | Assalto del Ragnarök | daily | one rewarded participation/day across windows |
| 14:00–15:00 | Giudizio delle Stirpi | daily | alternative window |
| 15:30–16:30 | Titanomachia | daily | — |
| 17:00–18:00 | Fronti del Valhalla | daily | — |
| 19:00–20:00 | Assalto del Ragnarök | daily | alternative window |
| 20:30–21:30 | Crepuscolo dei Titani | mon_wed_fri | — |
| 22:00–23:00 | Guerra dei Tre Troni | tue_thu_sat | prep_days = mon_wed_fri |

Il validator `validate_live_mode_calendar_v1.py` controlla esattamente 8 finestre con i 8 orari, modalità e frequenza attesi.

---

## 8. Sanctuary Housing — Dimora Divina (design note)

`sanctuary_housing_dimora_divina_design_note_v1.json` — **solo design note**, nessun runtime.

- Housing interno al Santuario
- Stanze/altari/arredi decorativi, slot equipaggiamento furniture
- Display eroi preferiti
- Comfort/prestige score
- Bonus globali piccoli, **cappati dal cosmetic/global cap resolver**
- **PvP caps più stretti del PvE**
- No infinite stacking, max slot furniture attivi
- **Paid furniture ownership account-wide**, **equipped state e bonus server-bound**
- Non obbligatorio per gioco competitivo

Benchmark sources: Figure Fantasy Otaku Zone, Nikke Outpost, Genshin Serenitea Pot, AFK Arena Oak Inn, League of Angels Homestead/Garden, Omniheroes Valkyrie Manor.

Il validator verifica che il design note non contenga chiavi runtime e che le bonus_rules includano i pattern di sicurezza richiesti.

---

## 9. SLC-BE baseline summary (accettato come baseline)

| Item | Valore |
|---|---|
| Suite SLC-BE post-completion | 269 PASS / 0 FAIL / 0 MISS |
| `runtime_enabled` | false |
| `db_write` | false |
| `migration_applied` | false |
| `second_server_opening_allowed` | false |
| `route_patch_required` | true |
| `default_s1_migration_required` | true |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset |
| `SECOND_SERVER_OPENING_ENABLED` | unset |
| `/api/heroes` | 100 |
| `/api/heroes/primordial_gaia` | 404 |
| `/api/heroes/borea` | 200 catalog-only inert baseline (pre-esistente, NON modificato) |
| `/api/heroes/greek_borea` | 200 catalog-only inert baseline (pre-esistente, NON modificato) |
| AF2-N cap | 50000 |
| AF2-N allowlist | 2500 |
| Borea hidden from `/api/heroes` list | ✅ |
| Broad rollout / public spend UI / STACK-G | OFF |

---

## 10. SLC-Next — sequenza consigliata (NON eseguita)

`slc_next_after_be_recommended_sequence_v1.json`: tutti i passi hanno `execute_now=false`.

| Step | Descrizione | Execute now |
|---|---|---|
| SLC-F | server-aware route patch dry-run | false |
| SLC-G | default S1 migration commit (strictly gated) | false |
| SLC-D | merge tooling simulation offline | false |
| SLC-H | server selection endpoint implementation (strictly gated) | false |

**Blockers** (7 documentati in `slc_next_after_be_blocker_status_v1.json`):
1. migration_required_before_runtime
2. route_patch_required
3. default_s1_migration_required
4. server_id isolation debt in existing routes
5. second server opening locked
6. runtime feature flags unset
7. user approval required for each runtime/DB phase

---

## 11. Validator results

### Combo
```
[live_modes_slc_next_combo_v1] PASS
  PASS  reconciliation
  PASS  calendar
  PASS  reward_framework
  PASS  broadcast_policy
  PASS  benchmark_risk_policy
  PASS  sanctuary_housing_note
  PASS  runtime_safety_audit
  PASS  slc_next_plan
```

### Runtime safety audit (read-only)
- `no_live_mode_runtime_routes`: ✅ true
- `protected_files_match` (battle_engine, battle_core, combat.tsx, affinity_gift_spend): ✅ tutti SHA-256 = SLC-C baseline
- `af2n_cap_s2_marker_present`: ✅ true (50000 presente)
- `live_mode_collections_found` in MongoDB: ✅ vuoto (40 collection scansionate)
- `SERVER_PROFILES_RUNTIME_ENABLED` / `SECOND_SERVER_OPENING_ENABLED`: ✅ unset

---

## 12. Suite globale + baseline diff + API smoke

### Suite
```
Overall: PASS  (pass=278, fail=0, miss=0)
```
9 nuovi entry OPTIONAL aggiunti (LIVE-MODES-RECONCILIATION-A, LIVE-MODES-CALENDAR-A, LIVE-MODES-REWARD-FRAMEWORK-A, LIVE-MODES-BROADCAST-POLICY-A, LIVE-MODES-RISK-POLICY-A, SANCTUARY-HOUSING-DESIGN-NOTE-A, LIVE-MODES-RUNTIME-SAFETY-AUDIT-A, SLC-NEXT-PREP-A, LIVE-MODES-SLC-NEXT-COMBO-A). Nessun REQUIRED indebolito.

### Baseline diff
```
Invariants: 5★=20, 6★=13, DW=13
final_numbers / runtime flags: clean across 5★+6★ slots
Marchio Boreale leak: 0 in non-Borea
Forbidden hero IDs: 0 (borea / primordial_gaia / aliases)
```

### API smoke (read-only)
| Endpoint | Status |
|---|---|
| `/api/heroes` count | 100 ✅ |
| `/api/heroes/primordial_gaia` | 404 ✅ |
| `/api/heroes/borea` | 200 (baseline catalog-only inert, immutato) |
| `/api/heroes/greek_borea` | 200 (baseline catalog-only inert, immutato) |
| `affinity_gift_spend.py` cap | `return min(v, 50000)` ✅ |
| AF2-N allowlist | 2500 ✅ |

---

## 13. Safety statement

NO DB writes · NO migration · NO new MongoDB collections/indexes · NO runtime routes per le 16 modalità o per Sanctuary Housing · NO auth changes · NO UI · NO modifiche a `battle_engine.py` / `battle_core.py` / `frontend/app/combat.tsx` / `affinity_gift_spend.py` · NO modifiche a gacha / roster / Character Bible / hero/skill/divine-weapon catalogs / final_numbers / assets · NO AF2-N / Stage4 / Redis runtime changes · NO Borea exposure introdotta · NO second-server enablement · NO public spend UI · NO STACK-G wiring · NO existing validator weakened.

---

## 14. Warnings

1. **Redis container drop ricorrente**: noto problema infra (vedi handoff precedente), mitigato via `ensure_redis_rate_limit.sh` (eseguito durante il run quando necessario). NON causato da questo task.
2. **`/api/heroes/borea` e `/api/heroes/greek_borea` rispondono 200 catalog-only**: stato **pre-esistente** documentato; baseline registrato in `_slc_c_api_smoke_readonly_v1_result.json`. Non modificato in questo task.
3. **333 riferimenti `user_id` in `/app/backend/routes/**`**: debito tecnico già rilevato in SLC-C preflight, da risolvere dalle fasi 6–11 di SLC-C; **NON** affrontato qui (out of scope).
4. **Sanctuary Housing** è solo design note: nessun bonus/asset/runtime implementato; ogni futura attivazione richiederà passaggio attraverso cosmetic/global cap resolver e approvazione esplicita.
5. **Scrigni dell'Elisio** è descritto come trial co-op supplementare, non inserito tra le 16 modalità live; resta candidato design separato.

---

## 15. Final recommendation

- ✅ **Accettare** LIVE-MODES-RECONCILIATION-A come source-of-truth corretto per il mapping 16 modalità ↔ benchmark.
- ✅ **Accettare** SLC-NEXT-PREP-A come piano sequenziale design-only.
- ✅ **Accettare** Sanctuary Housing come design note autonoma.
- ⏳ **NON procedere** ad alcuna implementazione runtime, DB write, route creation, UI, o apertura secondo server finché:
  - L'utente non ha approvato esplicitamente la SLC-C migration phase 0 (freeze + snapshot)
  - I 7 blocker del rollup non sono risolti
  - I 4 feature flag (`SERVER_PROFILES_RUNTIME_ENABLED`, `SERVER_AWARE_READS_ENABLED`, `SERVER_AWARE_WRITES_ENABLED`, `SECOND_SERVER_OPENING_ENABLED`) non sono stati discussi con l'utente
- ⏳ Quando si sceglierà di procedere, il prossimo step DESIGN-ONLY raccomandato è **SLC-F** (server-aware route patch dry-run), poiché tutto il resto (G/D/H) dipende dalla strategia di patch delle route attualmente `user_id`-keyed.

---

## 16. Next tasks (NON eseguiti)

- 🟡 P1: **SLC-F** — server-aware route patch dry-run (design-only)
- 🟡 P1: **SLC-G** — default S1 migration commit (strictly gated)
- 🟡 P1: **SLC-D** — merge tooling simulation offline (design-only)
- 🟡 P1: **SLC-H** — server selection endpoint implementation (strictly gated)
- 🟢 P2: **COSMETIC-B/C/D/E** — ulteriori implementazioni cosmetic (read-only/inert)
- 🔵 P3: **Managed Redis Live** + **Alerting Sink Live** (in attesa env vars `REDIS_MANAGED_URL` / `ALERT_WEBHOOK_URL`)
- 🔴 P4: **Broad Rollout / Public Spend UI Activation / STACK-G wiring** — strettamente deferred / OFF

---

**End of report.** LIVE-MODES-RECONCILIATION-A + SLC-NEXT-PREP-A chiusi come DESIGN-ONLY / PASS. Nessun runtime mutation, nessuna scrittura DB, nessuna UI, nessuna exposure Borea, nessun drift AF2-N, nessun diff su file critici.
