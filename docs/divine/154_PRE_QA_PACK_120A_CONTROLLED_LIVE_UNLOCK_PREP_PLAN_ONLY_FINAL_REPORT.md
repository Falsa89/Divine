# Pack 120A — Controlled Live Unlock Prep — Plan-Only Final Report

> **Codice pack:** `PRE_QA_PACK_120A_CONTROLLED_LIVE_UNLOCK_PREP_PLAN_ONLY_FROM_119D_MATRIX`
> **Tipo:** PLAN-ONLY / READ-ONLY. Niente unlock live, niente runtime
> flip, niente DB write, niente reward live, niente gacha/shop/VIP/BP live.
> **Sorgente:** matrice 119D (route_matrix + classification + blocked
> routes) + sorgenti `menu.tsx` / `preQaNavGuard.ts` letti read-only.
> **Output:** piano JSON + validator + questo report.

## 0. Numerazione del report

Ultimo report PRE_QA: `153_PRE_QA_PACK_119D_...`. Prossimo libero: **154**.

## 1. Obiettivo

Creare un **piano formale, statico e verificabile** per decidere quali
route/sistemi potranno essere sbloccati o testati in modo controllato nei
prossimi pack, basandosi sulla matrice di rischio prodotta dal Pack 119D.

Il pack:

- **NON applica unlock live.**
- **NON flippa flag runtime.**
- **NON modifica `menu.tsx` o `preQaNavGuard.ts`.**
- **NON modifica DB, backend, reward, gacha, shop, VIP, Battle Pass,
  combat, story runtime.**

Produce esclusivamente un piano dichiarativo (`*_plan_v1.json`), un
validator statico che lo verifica e questo report.

## 2. File creati

```text
data/design/pre_qa_controlled_unlock/controlled_live_unlock_prep_120a_plan_v1.json
backend/scripts/validate_pre_qa_pack_120a_controlled_unlock_prep.py
docs/divine/154_PRE_QA_PACK_120A_CONTROLLED_LIVE_UNLOCK_PREP_PLAN_ONLY_FINAL_REPORT.md
```

`menu.tsx` e `preQaNavGuard.ts` non sono stati modificati. Letti
read-only durante il parsing del validator 119D già esistente.

## 3. Fonte 119D

| Campo | Valore |
| --- | --- |
| Report 119D | `docs/divine/153_PRE_QA_PACK_119D_PUBLIC_MENU_ROUTE_TARGET_HEALTH_AND_MUTATION_CLASSIFICATION_FINAL_REPORT.md` |
| JSON 119D latest | `backend/reports/pre_qa_pack_119d_public_menu_route_health_latest.json` |
| Visible categories | 6 |
| Visible items | 22 |
| `unsafe_exposed` | 0 |
| `unknown_needs_review` | 0 |
| `leaked_blocked_routes` | 0 |

Tutte le 22 voci visibili 119D sono presenti come candidate nel piano
120A.

## 4. Tier breakdown del piano

| Tier | Definizione | Count |
| --- | --- | --- |
| Tier 0 | Already safe / no unlock needed | **1** |
| Tier 1 | Safe visual/manual QA candidate | **5** |
| Tier 2 | Controlled gated interaction candidate | **11** |
| Tier 3 | Battle preview / no reward candidate | **5** |
| Tier 4 | Hard blocked until future pack | 0 in candidate matrix (gestiti in `hard_blockers`) |

### 4.1 Tier 0 — Already safe (1)

| Route | Label | Razionale |
| --- | --- | --- |
| `/rankings` | Classifiche | `safe_read_only`, nessuna HTTP mutante, nessun keyword di mutazione, gating non necessario. |

### 4.2 Tier 1 — Safe visual/manual QA candidate (5)

| Route | Label | Razionale |
| --- | --- | --- |
| `/hero-collection` | Collezione Eroi | `locked_deferred`, nessuna mutazione. |
| `/artifacts-preview` | Artefatti & Costellazioni | `locked_deferred`, preview/locked. |
| `/guide` | Guida / Codex | `locked_deferred`, consultivo. |
| `/divine-weapons-catalog` | Armi Divine | Catalog read-only, gating=8, preview=16. Keyword `gacha` solo tematica. |
| `/collection-synergies-preview` | Sinergie Collezione | Design-only, gating=3, preview=8. |

### 4.3 Tier 2 — Controlled gated interaction candidate (11)

| Route | Label | Razionale gating |
| --- | --- | --- |
| `/story` | Capitoli Storia | Hub Storia, HTTP=1 (read), gating=6. Battle Launch Contract v1 preview-only. |
| `/tower-of-the-hells` | Torre degli Inferi | Hub Torre, gating=5, preview=4. |
| `/hero-training` | Addestramento Eroico | STRICT CONSTRAINTS in header, gating=16. |
| `/equipment` | Fucina di Efesto | HTTP=1, gating=2. Richiede audit endpoint scrittura. |
| `/soul-forge` | Forgia dell'Anima | `postqa_d_locked_endpoints`, gating=14. |
| `/achievements` | Achievement | strong `claim:3`, HTTP=1, gating=2. Endpoint claim deve restare 423. |
| `/treasury` | Tesoreria | strong `claim:1, summon:1`, gating=4, preview=9. |
| `/inventory` | Inventario | HTTP=1 (read), gating=2. No use/destroy live. |
| `/player-faction` | Fazione del Giocatore | HTTP=1 (read), gating=5. |
| `/servers` | Seleziona Server | HTTP=2, strong `claim:2` (claim slot, non reward), gating=7. Funzione esistente. |
| `/daily-hub` | Guida Giornaliera | strong `claim:1` (link aggregator), gating=1. Resta link-only. |

### 4.4 Tier 3 — Battle preview / no reward candidate (5)

Cinque entry-point della **stessa** pre-battle-lobby (file
`frontend/app/pre-battle-lobby.tsx`), condividono le stesse precondizioni:

- `blocked_no_team_for_server` resta attivo;
- `reward_live=false`, `ranking_live=false`, `db_writes=0`,
  `endpoint_live=false`;
- source canonica deterministica + no random opponents;
- `startBattle` keyword presente ma renderer reale resta preview/no
  commit.

| Route | Mode |
| --- | --- |
| `/pre-battle-lobby?mode=story` | story |
| `/pre-battle-lobby?mode=tower` | tower |
| `/pre-battle-lobby?mode=arena` | arena |
| `/pre-battle-lobby?mode=training` | training |
| `/pre-battle-lobby?mode=boss` | boss (Raid) |

## 5. Hard blockers (Tier 4 — sistemi che restano bloccati)

| ID | Descrizione | Routes affected |
| --- | --- | --- |
| `BLOCK_GACHA_LIVE` | Gacha (summon) live: DB write + currency spend | `/gacha` |
| `BLOCK_SHOP_LIVE` | Shop / Item Shop purchase live | `/shop`, `/item-shop` |
| `BLOCK_VIP_LIVE` | VIP subscription / premium grant live | `/vip` |
| `BLOCK_BATTLEPASS_LIVE` | Battle Pass purchase / claim live | `/battlepass` |
| `BLOCK_PVP_LIVE` | PvP matchmaking live + reward live | `/pvp` |
| `BLOCK_GUILD_LIVE` | Guild create/join/contribute live | `/guild`, `/gvg` |
| `BLOCK_RAID_LIVE_REWARD` | Raid Cooperativi reward live | `/raid` |
| `BLOCK_MAIL_CLAIM_LIVE` | Mail attachments claim live | `/mail` |
| `BLOCK_EVENTS_REWARD_LIVE` | Eventi giornalieri reward live | `/events` |
| `BLOCK_SOCIAL_LIVE` | Friends / DM / Plaza / Territory live | `/friends`, `/dm`, `/plaza`, `/territory` |
| `BLOCK_ECONOMY_SPEND_LIVE` | Spend currency/gem/soul-essence live | (tutte) |
| `BLOCK_REWARD_LIVE` | Grant reward live (achievement claim, daily claim, raid drop, ...) | (tutte) |
| `BLOCK_DB_WRITE_PRE_QA` | DB write live in pre-QA (eccetto auth/session approvati) | (tutte) |

## 6. Safety gates

| ID | Descrizione | Evidenza |
| --- | --- | --- |
| `GATE_A_STATIC_ROUTE_SAFETY` | Target file esiste; no live-blocked; no `unsafe_exposed`; no `unknown_needs_review`. | validator 119D + 119C |
| `GATE_B_MUTATION_CONTAINMENT` | POST/PUT/PATCH/DELETE assenti o gated (423/disabled/preview-only); no grant premium; no spend; no inventory mutation. | classification 119D + audit endpoint |
| `GATE_C_ECONOMY_ISOLATION` | Shop/Gacha/VIP/BP non esposti; no purchase route; no claim reale; no reward live. | 119C + 119D blocked_route_checks |
| `GATE_D_BATTLE_ISOLATION` | No authoritative battle commit; no EXP/progress/reward; pre-battle-lobby preview/no-write. | 119D classification pre-battle-lobby |
| `GATE_E_MANUAL_QA_CONTROLLED` | QA solo dopo audit statico; un solo Tier alla volta; non esplorativo. | stage_plan S0→S1→S2 |
| `GATE_F_ROLLBACK_AND_KILL_SWITCH` | Flag-gated; kill-switch; reversibile senza migration distruttiva. | future per-route pack design |

## 7. Stage plan

| Stage | Descrizione | Routes target |
| --- | --- | --- |
| **S0** `VISUAL_QA_ONLY` | QA visivo Tier 0 + Tier 1, nessuna scrittura, no tap su CTA write-like. | 6 route (Tier 0/1) |
| **S1** `CONTROLLED_GATED_INTERACTION_DRY_RUN` | Test mirato Tier 2: tap UI, verificare endpoint scrittura → 423/disabled. Nessun spend/grant. | 11 route (Tier 2) |
| **S2** `BATTLE_PREVIEW_VISUAL_PASS` | Test visivo pre-battle-lobby preview-only. | 5 mode (Tier 3) |
| **S3** `PER_ROUTE_LIVE_UNLOCK_DESIGN` | Pack futuri DEDICATI per ogni candidate Tier 2 con scrittura live. Non in questo pack. | 0 in questo pack |

## 8. Rollback requirements

- Tutti i futuri unlock devono essere **flag-gated** via env
  (`EXPO_PUBLIC_*`) o feature flag backend.
- Ogni unlock deve avere **kill-switch** documentato (variabile env o
  endpoint admin feature-flag).
- Nessun unlock deve richiedere **migration DB distruttiva**.
- Ogni unlock deve essere **revertibile** via revert del singolo commit
  o spegnimento flag, senza data loss.

## 9. Manual QA requirements

- QA visivo Tier 0/1 (6 route): scroll, navigazione, **no tap** su CTA
  write-like.
- QA Tier 2 (11 route): aprire ogni route, verificare disabled state,
  **NON tappare** 'avvia/claim/upgrade/forge/equip' live.
- QA Tier 3 (5 mode pre-battle-lobby): aprire lobby, verificare
  preview/no-write, source canonica deterministica.
- Tutti i test devono essere registrati nel report del pack QA dedicato
  successivo (es. 120B/120C/120D).

## 10. Prossimi pack raccomandati

In ordine sequenziale strettamente staged:

1. `PRE_QA_PACK_120B_VISUAL_QA_EVIDENCE_TIER0_TIER1` — evidenza QA visivo
   per le 6 route Tier 0/1.
2. `PRE_QA_PACK_120C_CONTROLLED_GATED_INTERACTION_DRY_RUN_TIER2` — dry-run
   QA gated per le 11 route Tier 2.
3. `PRE_QA_PACK_120D_BATTLE_PREVIEW_VISUAL_PASS_TIER3` — visual pass
   pre-battle-lobby.
4. `PRE_QA_PACK_121_PER_ROUTE_LIVE_UNLOCK_DESIGN_TIER4_INDIVIDUAL` —
   design pack-per-pack dedicato per ogni candidato Tier 2 con
   scrittura live (uno alla volta).

## 11. Validazione

### 11.1 Validator 120A dedicato

```text
$ python3 backend/scripts/validate_pre_qa_pack_120a_controlled_unlock_prep.py
[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP] OK candidates=22 safety_gates=6
  hard_blockers=13 plan_only=true runtime_unlock_applied=false
```

Verifiche eseguite:

- ✅ Piano JSON esiste e parsabile.
- ✅ `mode = plan_only`, `runtime_unlock_applied = false`,
  `db_write_allowed = false`, `reward_live_allowed = false`,
  `gacha_shop_vip_bp_allowed = false`.
- ✅ Tutte le 22 route 119D presenti nel piano (0 mancanti).
- ✅ Ogni candidate ha tier, classification_119d, risk_notes,
  future_gate, apply_now=false, live_reward_enabled=false,
  economy_live_enabled=false.
- ✅ Nessuna route live-blocked marcata `apply_now=true`.
- ✅ 6 safety_gates dichiarati (≥ 5 richiesti).
- ✅ Hard blockers richiesti (`BLOCK_GACHA_LIVE`, `BLOCK_SHOP_LIVE`,
  `BLOCK_VIP_LIVE`, `BLOCK_BATTLEPASS_LIVE`, `BLOCK_REWARD_LIVE`,
  `BLOCK_DB_WRITE_PRE_QA`) tutti presenti.
- ✅ Report finale corrispondente esiste (questo file).

### 11.2 Pre-QA Safety Validator Suite (regression)

```text
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

### 11.3 Validator 119C / 119D (regression)

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK ...
[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK ...
```

### 11.4 Repo hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ clean = True
```

## 12. Conferma no-touch

- ✅ Nessun unlock applicato (`runtime_unlock_applied = false`).
- ✅ Nessuna modifica a backend runtime, `battle_engine.py`, combat,
  gacha, shop, VIP, Battle Pass, reward, DB, tutorial, onboarding,
  starter claim, account reset, Home 119A, hero scale, bottom tab
  layout, Character Bible, assets, skill/Divine Weapon/Artifact
  runtime.
- ✅ Nessuna modifica a `menu.tsx` o `preQaNavGuard.ts`.
- ✅ Nessuna env flag modificata.
- ✅ Nessuna route live introdotta.
- ✅ Unico nuovo file backend: validator statico read-only
  `validate_pre_qa_pack_120a_controlled_unlock_prep.py` (pure file IO +
  JSON parsing).

## 13. Verdict

**`PRE_QA_PACK_120A_CONTROLLED_LIVE_UNLOCK_PREP_PLAN_ONLY_FROM_119D_MATRIX_READY_FOR_GAME_MASTER_REAUDIT`**

Il piano dichiarativo plan-only è completo, copre tutte le 22 route della
matrice 119D, classifica ogni route in tier 0–3 con risk notes,
precondizioni, test richiesti, rollback e future gate. Tier 4 (gacha,
shop, VIP, Battle Pass, reward live, DB writes pre-QA) resta hardcoded
nei blocker. Sei safety gates dichiarati. Validator dedicato verifica
la conformità. Pronto per il re-audit del Game Master.

## 14. Commit SHA

`2ae93117c` — `Pack 120A: controlled live unlock prep (plan-only, no runtime flip)`
