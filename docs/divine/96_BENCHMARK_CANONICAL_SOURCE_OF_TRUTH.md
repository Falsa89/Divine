# 96 — Divine Benchmark Canonical Source-of-Truth

> **Status**: ✅ PASS · **Mode**: DESIGN-ONLY / AUDIT-ONLY / READ-ONLY / SOURCE-OF-TRUTH
> **Date (UTC)**: 2026-05-22 · **Suite globale**: 292 PASS / 0 FAIL / 0 MISS

---

## 1. Scopo

Stabilire una **fonte canonica interna al progetto** per TUTTE le decisioni
benchmark-derived. Sostituisce ogni riferimento vago (es. "modalità X = modalità Y
di Bleach") con descrizioni precise, autonome, dettagliate, future-proof.

Le wiki sono state analizzate da ChatGPT, NON da Emergent. Questo pack è
l'unica fonte autoritativa che Emergent deve usare per future
implementazioni runtime.

**MODE**: DESIGN-ONLY / AUDIT-ONLY / READ-ONLY / SOURCE-OF-TRUTH.

---

## 2. File creati

### Markdown sources (in `/app/docs/divine/`)
- `96_BENCHMARK_CANONICAL_SOURCE_OF_TRUTH.md` — questo documento
- `96_LIVE_SPECIAL_MODES_CANONICAL.md` — 16 modalità live, descrizioni dettagliate
- `96_BENCHMARK_SYSTEM_LIBRARY.md` — sistemi benchmark oltre le modalità
- `96_SLC_F_ROUTE_PATCH_DRYRUN_NEXT_CHECKPOINT.md` — prompt SLC-F design-only

### JSON design (in `/app/data/design/benchmark_canonical/`)
1. `benchmark_canonical_index_v1.json`
2. `live_special_modes_canonical_v1.json` (16 modes + Scrigni dell'Elisio)
3. `benchmark_system_library_v1.json`
4. `benchmark_risk_policy_expanded_v1.json`
5. `sanctuary_housing_dimora_divina_canonical_v1.json`
6. `summon_pity_fragment_canonical_v1.json`
7. `server_lifecycle_calendar_merge_canonical_v1.json`
8. `event_hub_daily_guide_canonical_v1.json`
9. `guild_social_coop_canonical_v1.json`
10. `equipment_forge_relic_canonical_v1.json`
11. `battle_stats_reporting_canonical_v1.json`
12. `slc_f_next_checkpoint_canonical_v1.json`
13. `benchmark_canonical_readiness_rollup_v1.json`

### Script Python (in `/app/backend/scripts/`)
- `_benchmark_canonical_common.py` (helper)
- 12 validator individuali (`validate_*_canonical_v1.py`)
- `audit_benchmark_canonical_runtime_safety_v1.py`
- `validate_benchmark_canonical_combo_v1.py` (orchestrator)

Ogni JSON include obbligatoriamente:
```
design_only: true
runtime_attached: false
battle_runtime_attached: false
source_pack: "DIVINE_BENCHMARK_CANONICAL_SOURCE_PACK"
implementation_allowed_now: false
```

---

## 3. Copertura canonica

| Sistema | Stato | JSON | Validator |
|---|---|---|---|
| 16 live/special modes | design-only | `live_special_modes_canonical_v1.json` | ✅ |
| Server lifecycle/calendar/merge | design-only | `server_lifecycle_calendar_merge_canonical_v1.json` | ✅ |
| Event Hub + Daily Guide | design-only | `event_hub_daily_guide_canonical_v1.json` | ✅ |
| Summon / pity / fragments / wishlist | design-only | `summon_pity_fragment_canonical_v1.json` | ✅ |
| Cosmetics / skins / titles / furniture | design-only | (in `benchmark_system_library_v1.json`) | ✅ |
| Sanctuary Housing / Dimora Divina | design-only | `sanctuary_housing_dimora_divina_canonical_v1.json` | ✅ |
| Guild / social / co-op | design-only | `guild_social_coop_canonical_v1.json` | ✅ |
| Tower / castle / roguelike | design-only | (in `benchmark_system_library_v1.json`) | ✅ |
| Equipment / relic / forge | design-only | `equipment_forge_relic_canonical_v1.json` | ✅ |
| Battle stats / reporting | design-only | `battle_stats_reporting_canonical_v1.json` | ✅ |
| Monetized events guardrails | design-only | (in `benchmark_system_library_v1.json` + risk policy) | ✅ |
| Benchmark risk policy | design-only | `benchmark_risk_policy_expanded_v1.json` | ✅ |

Ogni voce ha i 4 blocchi canonici richiesti dal pack:
- **how_works_in_divine** (descrizione autonoma, NON wiki-rephrase)
- **import_from_benchmark** o **benchmark_inspiration** o **confirmed_benchmark**
- **do_not_import** (pattern espliciti vietati)
- **runtime_status** (`not_implemented` o `design_only_runtime_pending`)

---

## 4. Riconciliazione 16 modalità (canonical)

Confermati:
- **Cammino dell'Ade** ← Bleach Online Hueco Mundo Attack
- **Crepuscolo dei Titani** ← Bleach Online Void Region
- **Giudizio delle Stirpi** ← Bleach Online Evil Spirit
- **Fronti del Valhalla** ← Bleach Online Guild War
- **Titanomachia** ← Bleach Online Protect Seireitei
- **Assalto del Ragnarök** ← Bleach Online Ryoka Attack
- **Torre degli Inferi** ← SAO Memory Defrag Floor Clearing Castle / BBS Senkaimon
- **Guerra dei Tre Troni** ← Marvel Future Fight Alliance Conquest

Correzioni esplicite documentate:
- **Troni dell'Eclissi**: NON è Seireitei Soul Palace (correzione riportata in `live_special_modes_canonical_v1.json.modes[5].important_correction`)
- **Giudizio di Asgard**: NON presente su Bleach Online; benchmark Epic Seven Dagger Sicar / Future Fight World Event
- **Titanomachia**: ora correttamente mappata su Protect Seireitei

Non presenti su Bleach Online (con benchmark cross-game): Scala dell'Olimpo, Sigilli degli Dei, Prove del Pantheon, Abisso del Colosso, Fame del Behemoth, Furie del Pantheon, Troni dell'Eclissi, Giudizio di Asgard.

Modalità co-op aggiuntiva: **Scrigni dell'Elisio** (always available, first 3 daily runs rewarded).

---

## 5. Server lifecycle / calendar / merge (canonical)

- 7 statuses: planned / open / crowded / closed_to_new / merge_pending / merged / archived
- 6 daily windows + 2 weekly windows (incl. prep days di Guerra dei Tre Troni)
- Merge recovery: redirect profili esistenti, NO cloning cross-server, catch-up pool definito in SLC-A
- New player default: newest open → fallback newest open not crowded
- Existing player default: return to last active server
- Legacy single-shard → s1 via futura SLC-G migration

---

## 6. Summon / pity / fragments / wishlist (canonical)

- Soft pity + hard pity per banner
- Wishlist solo per permanent banner
- Free + paid currencies separati (paid account-wide, free server-bound)
- Pity scope **oggi**: `(user_id, banner_id)` single-shard
- Pity scope **futuro post-SLC**: `(account_id, server_id, banner_id)`
- NO cross-banner pity leak
- NO hidden odds, NO paid-only pity acceleration

---

## 7. Sanctuary Housing — Dimora Divina (canonical)

- Housing interno al Santuario; rooms/altars/decorative furniture
- Comfort/prestige score + bonus globali piccoli e cappati
- Equipped state e bonus **server-bound**; paid furniture ownership **account-wide**
- PvP caps più stretti del PvE
- Tutti i bonus passano per il **cosmetic/global cap resolver**
- `runtime_status: not_implemented`

---

## 8. Guild / social / co-op (canonical)

- Guild server-bound; una membership per `(account_id, server_id)`
- Roles: leader, officers, members
- Activity points finanziano open di Furie del Pantheon, Fame del Behemoth
- Co-op (Scrigni dell'Elisio): first 3 daily runs rewarded
- Social: friend list, gifts server-bound, profile visits, war reports
- Chat: rate-limited per-server

---

## 9. Equipment / relic / forge (canonical)

- Equipment per hero (rarità + substats); relic in catalog separato (locked)
- Forge: upgrade, enchant, salvage; cappato dal resolver dove stat-impacting
- Substat re-roll con anti-gambling cap
- QoL: batch upgrade, preset loadouts, auto-equip by score
- Server-bound dopo SLC migration

---

## 10. Battle stats / reporting (canonical)

- Post-battle stats: damage in/out, healing, ultimates, status applied, kills, deaths
- Per-hero contribution chart
- Replays per guild war modes (Valhalla, Tre Troni, Titanomachia)
- Leaderboards per damage / kills / streaks
- Telemetry NON tocca AF2-N runtime
- NO leak di opponent set bonuses pre-battle

---

## 11. Benchmark risk policy (expanded)

`benchmark_risk_policy_expanded_v1.json` lista **18 pattern vietati o cappati**:
paid cooldown clear · paid morale boost · VIP skip · paid revive ranking ·
uncapped extra entries · final blow rewards · occupation bonuses ·
guild donation power · ranking-only meta-critical · server transfer paid-only ·
public spend UI senza approval · STACK-G wiring senza resolver · hidden odds ·
FOMO competitive · alt-account co-op exploit · cross-server data clone ·
borea exposure · second server opening senza approval.

**Hard invariants** registrati e validati: AF2-N cap=50000, allowlist=2500,
`second_server_opening_allowed=false`, `server_profiles_runtime_enabled=false`,
`borea_hidden_from_api_heroes_list=true`, `primordial_gaia_404=true`.

---

## 12. SLC-F (next checkpoint) — design-only

`slc_f_next_checkpoint_canonical_v1.json` — `execute_now=false`.

Output futuri (NON ancora prodotti):
1. server-aware route patch matrix
2. per-route risk classification
3. server-bound/account-wide collection mapping
4. pseudo-diff / patch contract only
5. dry-run resolver simulation per `account_id + server_id`
6. protected-file no-diff audit
7. DB no-write audit
8. future phase recommendations

Hard guardrails SLC-F: NO runtime patch, NO DB writes, NO migrations, NO route creation, NO auth runtime change, NO UI, NO second server opening, NO modifiche a battle_engine/battle_core/combat.tsx/affinity_gift_spend/AF2-N/Stage4.

---

## 13. Runtime safety audit

`benchmark_canonical_runtime_safety_audit_v1.json`:
- Protected files SHA-256 = SLC-C baseline ✅ (battle_engine, battle_core, combat.tsx, affinity_gift_spend)
- AF2-N cap S2 (50000) marker present ✅
- `SERVER_PROFILES_RUNTIME_ENABLED` unset ✅
- `SECOND_SERVER_OPENING_ENABLED` unset ✅
- 0 benchmark/sanctuary/live-special-modes collections in MongoDB ✅

---

## 14. Suite + baseline + API smoke

### Combo
```
[benchmark_canonical_combo_v1] PASS  (13/13)
```

### Suite globale
```
Overall: PASS  (pass=292, fail=0, miss=0)
```
14 nuovi entry OPTIONAL aggiunti. Nessun REQUIRED indebolito.

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
| AF2-N cap | `min(v, 50000)` presente ✅ |
| AF2-N allowlist | 2500 invariato ✅ |

---

## 15. Safety statement

NO DB writes · NO migrations · NO new MongoDB collections/indexes · NO runtime route creation · NO auth changes · NO UI · NO modifiche a `battle_engine.py` / `battle_core.py` / `combat.tsx` / `affinity_gift_spend.py` · NO modifiche a gacha / roster / Character Bible / catalog / final_numbers / assets · NO AF2-N / Stage4 / Redis runtime changes · NO Borea exposure introdotta · NO second-server enablement · NO public spend UI · NO STACK-G wiring · NO existing validator weakened.

---

## 16. Warnings & note operative

1. **Redis container drop ricorrente**: noto issue infra; mitigato via `ensure_redis_rate_limit.sh` durante run. NON causato da questo task.
2. **`/api/heroes/borea` / `/api/heroes/greek_borea` = 200**: baseline catalog-only pre-esistente documentato; NON modificato.
3. **333 user_id refs in `/app/backend/routes/**`**: debito tecnico baseline, target di SLC-C phases 6–11; NON affrontato qui.
4. **Sanctuary Housing**: solo design note canonica; nessuna implementazione runtime/asset.
5. **Scrigni dell'Elisio**: registrato come modalità co-op aggiuntiva (non parte delle 16 competitive).

---

## 17. Recommendation

- ✅ **Accettare** questo pack come source-of-truth canonica per tutte le decisioni benchmark-derived.
- ✅ **Usare i 13 JSON canonical** come unica fonte autoritativa per future implementazioni runtime. Ogni futura pack di implementazione deve referenziare `benchmark_canonical_index_v1.json`.
- ⏳ **Prossimo checkpoint design-only consigliato**: **SLC-F** (route patch dry-run).
- ⏳ **NON procedere** a implementazione runtime senza:
  - Approval esplicito utente
  - Risoluzione dei 7 blocker SLC-Next
  - Feature flags discussi e approvati

---

## 18. Next tasks (NON eseguiti)

- 🟡 P1: **SLC-F** — route patch dry-run (design-only)
- 🟡 P1: SLC-G (default S1 migration commit, gated)
- 🟡 P1: SLC-D (merge tooling simulation offline)
- 🟡 P1: SLC-H (server selection endpoint impl, gated)
- 🟢 P2: COSMETIC-B/C/D/E
- 🔵 P3: Managed Redis Live + Alerting Sink Live (in attesa env vars)
- 🔴 P4: Broad rollout / Public spend UI / STACK-G (strictly deferred/OFF)

---

**End of report.** Divine Benchmark Canonical Source-of-Truth chiuso come DESIGN-ONLY / SOURCE-OF-TRUTH / PASS. Nessuna scrittura DB, nessuna mutazione runtime, nessuna UI, nessuna exposure Borea, nessun drift AF2-N, nessun diff su file critici.
