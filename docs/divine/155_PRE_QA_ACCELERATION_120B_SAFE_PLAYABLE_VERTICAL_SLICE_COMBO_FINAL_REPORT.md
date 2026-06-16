# Pack 120B — Safe Playable Vertical Slice Combo — Final Report

> **Codice pack:** `PRE_QA_ACCELERATION_120B_SAFE_PLAYABLE_VERTICAL_SLICE_COMBO`
> **Tipo:** Macro-pack unico che unifica Track A (Tier 0/1 visual QA),
> Track B (Tier 2 controlled gated dry-run), Track C (Tier 3 battle
> preview visual pass), Track D (unified harness/report).
> **Scope:** READ-ONLY + validator unico. Nessuna modifica a UI/guard
> richiesta perché l'audit non ha trovato unsafe esposto.
> **No-touch:** DB, backend runtime live, reward grant, claim live,
> currency spend, gacha, shop, VIP, Battle Pass, IAP, authoritative
> battle commit, EXP/progress commit, ranking live, guild live,
> raid reward live, Character Bible, assets, Home 119A hero
> scale/grounding, bottom nav layout, tutorial/onboarding live,
> account reset, Divine Weapon runtime, Artifact runtime,
> skill/status runtime.

## 0. Numerazione del report

Ultimo report PRE_QA: `154_PRE_QA_PACK_120A_...`. Prossimo libero: **155**.

## 1. Obiettivo

Accelerare la fase Pre-QA evitando tre micro-pack separati (120B/120C/120D)
e unificare in un solo macro-pack controllato:

1. **Track A** — QA visuale Tier 0/1 evidence.
2. **Track B** — Tier 2 controlled gated interaction dry-run.
3. **Track C** — Tier 3 battle preview visual pass.
4. **Track D** — harness/report unico.

Trasformare la fase corrente da "menu pulito" a "vertical slice pre-QA
realmente navigabile/testabile ma ancora non live".

## 2. File creati / modificati

```text
backend/scripts/validate_pre_qa_acceleration_120b_safe_playable_vertical_slice_combo.py
docs/divine/155_PRE_QA_ACCELERATION_120B_SAFE_PLAYABLE_VERTICAL_SLICE_COMBO_FINAL_REPORT.md
backend/reports/pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json
```

**Nessuna modifica a:** `menu.tsx`, `preQaNavGuard.ts`,
`pre-battle-lobby.tsx`, `combat.tsx`, backend runtime, DB, env flag,
file frontend di runtime. L'audit unificato non ha riscontrato
unsafe-esposto e quindi non è stato necessario applicare correzioni UI.

## 3. Risultati globali

| Metrica | Valore |
| --- | --- |
| Candidate totali (da 120A) | **22** |
| Tier 0 (visual ready) | 1 |
| Tier 1 (visual ready) | 5 |
| Tier 2 (dry-run ready) | 11 |
| Tier 3 (battle preview ready) | 5 |
| **Track A** visual QA ready | **6/6** |
| **Track B** dry-run ready | **11/11** |
| **Track C** battle preview ready | **5/5** |
| Live blocked routes leaked | **0** |
| `unsafe_exposed` (119D regression) | 0 |
| `unknown_needs_review` (119D regression) | 0 |
| Failures validator 120B | **0** |

**Verdict validator 120B: PASS**.

## 4. Track A — Tier 0/Tier 1 Visual QA Evidence

Le 6 route Tier 0/1 sono visual-QA-ready (file target esistenti, label
player-facing pulite, nessun mutation strong senza gating).

| Route | Tier | Label | File target | Classification 119D | Visual QA ready |
| --- | --- | --- | --- | --- | --- |
| `/rankings` | 0 | Classifiche | `frontend/app/rankings.tsx` | `safe_read_only` | ✅ |
| `/hero-collection` | 1 | Collezione Eroi | `frontend/app/hero-collection.tsx` | `locked_deferred` | ✅ |
| `/artifacts-preview` | 1 | Artefatti & Costellazioni | `frontend/app/artifacts-preview.tsx` | `locked_deferred` | ✅ |
| `/guide` | 1 | Guida / Codex | `frontend/app/guide.tsx` | `locked_deferred` | ✅ |
| `/divine-weapons-catalog` | 1 | Armi Divine | `frontend/app/divine-weapons-catalog.tsx` | `mutation_sensitive_but_gated` | ✅ |
| `/collection-synergies-preview` | 1 | Sinergie Collezione | `frontend/app/collection-synergies-preview.tsx` | `mutation_sensitive_but_gated` | ✅ |

Le ultime due hanno classificazione `mutation_sensitive_but_gated` solo
per termini tematici (`gacha`, `equip`); il file è di fatto catalog
read-only con marker preview/locked dominanti. Sicure per QA visivo.

**Polish backlog non bloccante**: nessuno individuato.

## 5. Track B — Tier 2 Controlled Gated Interaction Dry-Run

Le 11 route Tier 2 hanno tutte file target esistente, sono classificate
come `mutation_sensitive_but_gated` da 119D, e ogni route con
mutation HTTP o strong-keyword ha evidenza di gating > 0.

| Route | Label | HTTP | Strong KW | Gating | Dry-run ready |
| --- | --- | --- | --- | --- | --- |
| `/story` | Capitoli Storia | 1 | — | 6 | ✅ |
| `/tower-of-the-hells` | Torre degli Inferi | 0 | — | 5 | ✅ |
| `/hero-training` | Addestramento Eroico | 0 | — | 16 | ✅ |
| `/equipment` | Fucina di Efesto | 1 | — | 2 | ✅ |
| `/soul-forge` | Forgia dell'Anima | 1 | — | 14 | ✅ |
| `/achievements` | Achievement | 1 | claim:3 | 2 | ✅ |
| `/treasury` | Tesoreria | 0 | claim:1, summon:1 | 4 | ✅ |
| `/inventory` | Inventario | 1 | — | 2 | ✅ |
| `/player-faction` | Fazione del Giocatore | 1 | — | 5 | ✅ |
| `/servers` | Seleziona Server | 2 | claim:2 | 7 | ✅ |
| `/daily-hub` | Guida Giornaliera | 0 | claim:1 | 1 | ✅ |

**Tutte le 11 Tier 2 sono dry-run-ready**: l'utente può navigare,
osservare disabled state, ma NON deve tappare CTA live (claim, upgrade,
forge, equip, ecc.). Endpoint write restano 423/disabled.

## 6. Track C — Tier 3 Battle Preview Visual Pass

Le 5 entry-point pre-battle-lobby (un'unica file `pre-battle-lobby.tsx`)
sono battle-preview-ready.

### 6.1 Token canonici verificati

`frontend/app/pre-battle-lobby.tsx` contiene i marker preview-only
richiesti:

| Token | Presente |
| --- | --- |
| `is_preview` | ✅ |
| `reward_policy` | ✅ |
| `preview` | ✅ |
| `blocked_no_team_for_server` | ✅ |
| `battle_engine_mode` | ✅ |

`frontend/app/combat.tsx` contiene i lock canonici autoritativi:

| Token | Presente |
| --- | --- |
| `PREVIEW_REWARD_LOCK_ACTIVE` | ✅ |
| `PREVIEW_NON_AUTHORITATIVE` | ✅ |

### 6.2 Mode pre-battle-lobby (5/5)

| Route | Mode | Visual preview ready |
| --- | --- | --- |
| `/pre-battle-lobby?mode=story` | story | ✅ |
| `/pre-battle-lobby?mode=tower` | tower | ✅ |
| `/pre-battle-lobby?mode=arena` | arena | ✅ |
| `/pre-battle-lobby?mode=training` | training | ✅ |
| `/pre-battle-lobby?mode=boss` | boss (Raid) | ✅ |

### 6.3 Vertical slice verticale

```text
Menu/Home ──▶ Battaglia ──▶ Pre-Battle Lobby ──▶ Combat visual preview
                                                  (PREVIEW_REWARD_LOCK_ACTIVE)
```

Garanzie:

- ✅ NO reward.
- ✅ NO EXP.
- ✅ NO progress commit.
- ✅ NO ranking commit.
- ✅ NO battle result DB write.
- ✅ NO authoritative battle runtime.
- ✅ NO gacha/shop/VIP/BP.
- ✅ NO random live matchmaking.
- ✅ NO live raid reward.
- ✅ Source canonica deterministica + `blocked_no_team_for_server` se assente team.

## 7. Quali route sono device-test-ready

**TUTTE le 22** route candidate sono device-test-ready in modalità
**preview / dry-run / read-only**, suddivise per tipo di test:

| Tipo test | Routes | Cosa fare in QA device |
| --- | --- | --- |
| Visual QA passivo | 6 (Tier 0/1) | Scroll, navigazione. NON tappare CTA write-like. |
| Dry-run gated | 11 (Tier 2) | Tap UI, osservare disabled state, NO claim/upgrade/forge/equip live. |
| Battle preview | 5 (Tier 3) | Aprire lobby, verificare `PREVIEW_REWARD_LOCK_ACTIVE`, NO commit reward. |

## 8. Quali route restano locked/deferred

Le route classificate `locked_deferred` da 119D (Tier 1):

- `/hero-collection`
- `/artifacts-preview`
- `/guide`

Nessuna mutazione, nessun unlock necessario. Restano consultive.

## 9. Quali route sono hard-blocked (Tier 4)

Confermato dal Pack 120A: 13 hard blocker IDs. Le 18 route live/dev-only
restano **NON esposte** nel menu pubblico (`leaked_blocked_routes = 0`):

`/shop`, `/vip`, `/battlepass`, `/gacha`, `/pvp`, `/guild`, `/gvg`,
`/raid`, `/territory`, `/plaza`, `/dm`, `/events`, `/mail`, `/friends`,
`/playable-mode-battle-preview`, `/skill-status-vfx-catalogs`,
`/hero-skill-kits-catalog`, `/safe-previews`.

## 10. Bug / polish backlog non bloccante

**Nessuno individuato** in questo audit. Tutte le 22 route soddisfano
i criteri Track A/B/C. Niente da escalare come blocker, niente da
correggere come polish urgente.

## 11. Conferma no-touch (zero live unlock)

| Vincolo | Stato |
| --- | --- |
| zero unlock live | ✅ |
| zero reward live | ✅ |
| zero DB write | ✅ |
| zero gacha/shop/VIP/BP esposti | ✅ |
| zero claim live (Daily Hub link-only, Achievement 423) | ✅ |
| zero currency spend live | ✅ |
| zero authoritative battle commit | ✅ |
| zero EXP/progress commit | ✅ |
| zero ranking live | ✅ |
| zero guild/raid reward live | ✅ |
| zero env flag toccata | ✅ |
| zero file runtime proibito modificato | ✅ |

`runtime_unlock_applied = false` (verificato dal piano 120A).

## 12. Validazione

### 12.1 Validator 120B (unificato)

```text
$ python3 backend/scripts/validate_pre_qa_acceleration_120b_safe_playable_vertical_slice_combo.py
============== PACK 120B — VERTICAL SLICE COMBO ==============
  candidates: 22
  tier counts: {'tier_0_visual': 1, 'tier_1_visual': 5,
                'tier_2_dry_run': 11, 'tier_3_battle_preview': 5}
  Track A visual QA ready: 6/6
  Track B dry-run ready:   11/11
  Track C battle preview ready: 5/5
  failures: 0
  verdict: PASS
===============================================================
[v120b PRE_QA_120B_VERTICAL_SLICE_COMBO] OK candidates=22 tier01_ready=6
  tier2_ready=11 tier3_ready=5 live_blocked_leaked=0 unsafe_exposed=0
  unknown=0
```

JSON output:

- `backend/reports/pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_<UTC>.json`
- `backend/reports/pre_qa_acceleration_120b_safe_playable_vertical_slice_combo_latest.json`

### 12.2 Regression validators

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK categories=6 items=22
  duplicates=0 soul_forge_unique=true labels_clean=true
  dev_routes_hidden=true live_routes_blocked=true
[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK unsafe_exposed=0
  unknown_needs_review=0 leaked=0 file_targets_existing=22
[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP] OK candidates=22
  safety_gates=6 hard_blockers=13 plan_only=true
  runtime_unlock_applied=false
```

### 12.3 Pre-QA Safety Validator Suite

```text
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

### 12.4 Repo hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

## 13. Verdict

**`PRE_QA_ACCELERATION_120B_SAFE_PLAYABLE_VERTICAL_SLICE_COMBO_READY_FOR_GAME_MASTER_REAUDIT`**

La fase Pre-QA è ora una **vertical slice safe playable**: il giocatore
può navigare l'intero menu pubblico, aprire ogni route consultiva o
gated, attraversare il flow `Menu → Battaglia → Pre-Battle Lobby →
Combat preview` senza che il sistema esegua reward, EXP, progress,
ranking, DB write, gacha, shop, VIP, BP, o qualsiasi authoritative
battle commit. Tutte le 22 route 120A sono device-test-ready nel
rispettivo modo (visual / dry-run / battle preview).

## 14. Commit SHA

Verrà aggiornato dopo `git commit`.
