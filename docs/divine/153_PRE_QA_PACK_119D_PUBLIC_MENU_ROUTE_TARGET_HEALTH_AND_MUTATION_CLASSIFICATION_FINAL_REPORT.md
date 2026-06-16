# Pack 119D — Public Menu Route Target Health & Mutation Classification — Final Report

> **Codice pack:** `PRE_QA_PACK_119D_PUBLIC_MENU_ROUTE_TARGET_HEALTH_AND_MUTATION_CLASSIFICATION`
> **Tipo:** Validazione/classificazione statica delle route player-facing
> visibili dal menu pubblico filtrato. Audit READ-ONLY, niente modifiche
> runtime/backend/DB/reward/gacha/shop/VIP/BP.
> **Scope file:** nuovo validator
> `backend/scripts/validate_pre_qa_pack_119d_public_menu_route_health.py` +
> questo report. Nessuna modifica a `menu.tsx` o `preQaNavGuard.ts`:
> il validator non ha trovato route unsafe esposte.

## 0. Numerazione del report

Ultimo report PRE_QA: `152_PRE_QA_PACK_119C_...`. Prossimo libero: **153**.

## 1. Obiettivo

Validare e classificare staticamente per rischio tutte le route player-facing
attualmente visibili dal menu pubblico filtrato (guard di default ON), in
preparazione di qualsiasi futuro pack di unlock controllato (Pack 120).

Il validator:

1. Ricostruisce il menu pubblico filtrato (stessa logica del Pack 119C
   read-only).
2. Per ogni voce visibile, risolve il file target Expo Router atteso e
   verifica che esista.
3. Esegue audit statico leggero del file target cercando chiamate HTTP
   mutanti, keyword di mutazione (strong/weak), evidenza di gating
   (LOCKED / 423 / preview-only / disabled / STRICT CONSTRAINTS / ...).
4. Classifica ogni route in una di sei classi: `safe_read_only`,
   `safe_preview_only`, `locked_deferred`, `mutation_sensitive_but_gated`,
   `unsafe_exposed`, `unknown_needs_review`.
5. Conferma che le route live/dev-only siano effettivamente assenti dal
   menu pubblico.

## 2. Risultati globali

| Metrica | Valore |
| --- | --- |
| Categorie visibili | **6** |
| Voci visibili | **22** |
| File target esistenti | 22 / 22 (100%) |
| File target mancanti | 0 |
| `safe_read_only` | 1 |
| `safe_preview_only` | 0 |
| `locked_deferred` | 3 |
| `mutation_sensitive_but_gated` | 18 |
| `unsafe_exposed` | **0** |
| `unknown_needs_review` | **0** |
| Live blocked routes leaked nel menu pubblico | **0** |

**Verdict validator 119D: PASS**.

## 3. Snapshot menu pubblico (categorie + voci visibili)

| Categoria | Voce | Route | File target |
| --- | --- | --- | --- |
| Avventura | Capitoli Storia | `/story` | `frontend/app/story.tsx` |
| Avventura | Torre degli Inferi | `/tower-of-the-hells` | `frontend/app/tower-of-the-hells.tsx` |
| Progressione | Collezione Eroi | `/hero-collection` | `frontend/app/hero-collection.tsx` |
| Progressione | Addestramento Eroico | `/hero-training` | `frontend/app/hero-training.tsx` |
| Progressione | Fucina di Efesto | `/equipment` | `frontend/app/equipment.tsx` |
| Progressione | Artefatti & Costellazioni | `/artifacts-preview` | `frontend/app/artifacts-preview.tsx` |
| Progressione | Forgia dell'Anima | `/soul-forge` | `frontend/app/soul-forge.tsx` |
| Progressione | Achievement | `/achievements` | `frontend/app/achievements.tsx` |
| Economia | Tesoreria | `/treasury` | `frontend/app/treasury.tsx` |
| Economia | Inventario | `/inventory` | `frontend/app/inventory.tsx` |
| Sociale | Fazione del Giocatore | `/player-faction` | `frontend/app/player-faction.tsx` |
| Altro | Guida / Codex | `/guide` | `frontend/app/guide.tsx` |
| Altro | Classifiche | `/rankings` | `frontend/app/rankings.tsx` |
| Altro | Seleziona Server | `/servers` | `frontend/app/servers.tsx` |
| Altro | Guida Giornaliera | `/daily-hub` | `frontend/app/daily-hub.tsx` |
| Altro | Armi Divine | `/divine-weapons-catalog` | `frontend/app/divine-weapons-catalog.tsx` |
| Altro | Sinergie Collezione | `/collection-synergies-preview` | `frontend/app/collection-synergies-preview.tsx` |
| Battaglia | Storia | `/pre-battle-lobby?mode=story` | `frontend/app/pre-battle-lobby.tsx` |
| Battaglia | Torre | `/pre-battle-lobby?mode=tower` | `frontend/app/pre-battle-lobby.tsx` |
| Battaglia | Arena PvP | `/pre-battle-lobby?mode=arena` | `frontend/app/pre-battle-lobby.tsx` |
| Battaglia | Addestramento | `/pre-battle-lobby?mode=training` | `frontend/app/pre-battle-lobby.tsx` |
| Battaglia | Raid | `/pre-battle-lobby?mode=boss` | `frontend/app/pre-battle-lobby.tsx` |

## 4. Route Matrix — classificazione e rischio

> Legenda mutazioni: `HTTP` = chiamate `axios/apiClient/api/http.post|put|patch|delete`
> + pattern `fetch({method:'POST|PUT|PATCH|DELETE'})` (count nel codice
> ripulito dai commenti). `Strong KW` = keyword forti (`claim`, `purchase`,
> `spend`, `redeem`, `summon`, `pullGacha`, `gachaPull`, `subscribeVip`,
> `startBattle`, `startMatch`). `Weak KW` = keyword deboli (`reward`, `buy`,
> `gacha`, `vip`, `battlepass`, `shop`, `forge`, `upgrade`, `equip`,
> `complete`, `progress`, `ledger`). `Gating` = somma occorrenze marker tipo
> `LOCKED`, `423`, `preview-only`, `STRICT CONSTRAINTS`, `disabled=`, ecc.

| Categoria | Route | HTTP | Strong KW | Weak KW | Gating | Classificazione |
| --- | --- | --- | --- | --- | --- | --- |
| Avventura | `/story` | 1 | — | progress:1 | 6 | mutation_sensitive_but_gated |
| Avventura | `/tower-of-the-hells` | 0 | — | reward:1, progress:5 | 5 | mutation_sensitive_but_gated |
| Progressione | `/hero-collection` | 0 | — | — | 1 | locked_deferred |
| Progressione | `/hero-training` | 0 | — | reward:1 | 16 | mutation_sensitive_but_gated |
| Progressione | `/equipment` | 1 | — | upgrade:1, equip:2 | 2 | mutation_sensitive_but_gated |
| Progressione | `/artifacts-preview` | 0 | — | — | 1 | locked_deferred |
| Progressione | `/soul-forge` | 1 | — | shop:2, forge:18 | 14 | mutation_sensitive_but_gated |
| Progressione | `/achievements` | 1 | claim:3 | reward:1 | 2 | mutation_sensitive_but_gated |
| Economia | `/treasury` | 0 | claim:1, summon:1 | shop:8 | 4 | mutation_sensitive_but_gated |
| Economia | `/inventory` | 1 | — | shop:1 | 2 | mutation_sensitive_but_gated |
| Sociale | `/player-faction` | 1 | — | — | 5 | mutation_sensitive_but_gated |
| Altro | `/guide` | 0 | — | — | 2 | locked_deferred |
| Altro | `/rankings` | 0 | — | — | 0 | **safe_read_only** |
| Altro | `/servers` | 2 | claim:2 | — | 7 | mutation_sensitive_but_gated |
| Altro | `/daily-hub` | 0 | claim:1 | battlepass:2, shop:2 | 1 | mutation_sensitive_but_gated |
| Altro | `/divine-weapons-catalog` | 0 | — | gacha:5 | 8 | mutation_sensitive_but_gated |
| Altro | `/collection-synergies-preview` | 0 | — | equip:1 | 3 | mutation_sensitive_but_gated |
| Battaglia | `/pre-battle-lobby?mode=story` | 1 | startBattle:2 | — | 21 | mutation_sensitive_but_gated |
| Battaglia | `/pre-battle-lobby?mode=tower` | 1 | startBattle:2 | — | 21 | mutation_sensitive_but_gated |
| Battaglia | `/pre-battle-lobby?mode=arena` | 1 | startBattle:2 | — | 21 | mutation_sensitive_but_gated |
| Battaglia | `/pre-battle-lobby?mode=training` | 1 | startBattle:2 | — | 21 | mutation_sensitive_but_gated |
| Battaglia | `/pre-battle-lobby?mode=boss` | 1 | startBattle:2 | — | 21 | mutation_sensitive_but_gated |

### Logica di classificazione

| Condizione | Classe |
| --- | --- |
| `HTTP ≥ 1` o `Strong KW ≥ 1` con `Gating ≥ 1` | mutation_sensitive_but_gated |
| `HTTP ≥ 1` o `Strong KW ≥ 1` senza `Gating` | **unsafe_exposed (FAIL)** |
| Solo `Weak KW ≥ 1` con `Gating ≥ 1` | mutation_sensitive_but_gated |
| Solo `Weak KW ≥ 1` senza `Gating` | unknown_needs_review |
| Nessuna mutazione + `Gating ≥ 1` | locked_deferred |
| Nessuna mutazione, nessun gating, `preview ≥ 3` | safe_preview_only |
| Nessun segnale | safe_read_only |

> Le keyword sono cercate nel codice **ripulito dai commenti** per evitare
> false-positive del tipo `// "No purchases / claim"` nei file stub. I
> marker di gating sono invece cercati nel sorgente raw, perché tipicamente
> appaiono nell'header doc dei file preview/stub.

## 5. Conferma route live/dev-only bloccate

Le seguenti route NON appaiono nel menu pubblico filtrato (verifica
incrociata via `PRE_QA_BLOCKED_PLAYER_ROUTES` + filtro categoria/voce):

| Route | Bloccata nel guard | Presente nel menu pubblico | OK |
| --- | --- | --- | --- |
| `/shop` | ✅ | ❌ | ✅ |
| `/vip` | ✅ | ❌ | ✅ |
| `/battlepass` | ✅ | ❌ | ✅ |
| `/gacha` | ✅ | ❌ | ✅ |
| `/pvp` | ✅ | ❌ | ✅ |
| `/guild` | ✅ | ❌ | ✅ |
| `/gvg` | ✅ | ❌ | ✅ |
| `/raid` | ✅ | ❌ | ✅ |
| `/territory` | ✅ | ❌ | ✅ |
| `/plaza` | ✅ | ❌ | ✅ |
| `/dm` | ✅ | ❌ | ✅ |
| `/events` | ✅ | ❌ | ✅ |
| `/mail` | ✅ | ❌ | ✅ |
| `/friends` | ✅ | ❌ | ✅ |
| `/playable-mode-battle-preview` | ✅ | ❌ | ✅ |
| `/skill-status-vfx-catalogs` | ✅ | ❌ | ✅ |
| `/hero-skill-kits-catalog` | ✅ | ❌ | ✅ |
| `/safe-previews` | ✅ | ❌ | ✅ |

**Tutte le 18 route live/dev-only restano effettivamente bloccate.**
`leaked_blocked_routes_count = 0`.

## 6. Azioni correttive

**Nessuna azione correttiva applicata.** Il validator non ha trovato:

- nessuna `unsafe_exposed`;
- nessuna `unknown_needs_review`;
- nessuna live/dev-only route esposta;
- nessun file target mancante.

Quindi **`menu.tsx` e `preQaNavGuard.ts` non vengono modificati** in questo
pack. Conformemente al contratto Pack 119D: scope read-only, modifiche
ammesse SOLO se serve gatare una route effettivamente unsafe esposta.

## 7. Note sulla classe `mutation_sensitive_but_gated`

Le 18 voci classificate come `mutation_sensitive_but_gated` sono "sensibili
ma protette": contengono codice di mutazione (HTTP write o strong keyword)
**ma** mostrano evidenza esplicita di gating nel file (es. `LOCKED`,
`postqa_d_locked`, `STRICT CONSTRAINTS`, `preview-only`, `423`,
`disabled=`, `blocked_no_team_for_server`, ecc.).

Esempi notevoli (dal report JSON):

- **`/pre-battle-lobby`** — `startBattle:2`, HTTP:1, gating:21. Pre-battle
  lobby con guard `blocked_no_team_for_server`, fallback team sicuro,
  preview-only fetch.
- **`/soul-forge`** — HTTP:1, forge:18, shop:2, gating:14. Importa
  `postqa_d_locked_endpoints`, UI pre-QA con disabled buttons.
- **`/hero-training`** — reward:1, gating:16. Header esplicito
  `STRICT CONSTRAINTS / No backend calls / No state mutation / No
  purchases / claim / Buttons are visually disabled`.
- **`/treasury`** — strong `claim:1`, `summon:1`, gating:4. UI tesoreria
  con voci consultive e preview di valute.
- **`/divine-weapons-catalog`** — weak `gacha:5`, gating:8, preview:16.
  Catalogo Armi Divine read-only (cataloghi inert post Pack 119A/B).

Queste route NON sono blocker per il Pack 119D: il loro stato live verrà
riconsiderato singolarmente quando il Pack 120 (`CONTROLLED_LIVE_UNLOCK_PREP`)
selezionerà candidate per l'attivazione live.

## 8. Validazione

### 8.1 Validator 119D dedicato

```text
$ python3 backend/scripts/validate_pre_qa_pack_119d_public_menu_route_health.py
================ PACK 119D — ROUTE HEALTH MATRIX ================
  visible categories: 6
  visible items:      22
  unsafe_exposed:     0
  unknown_needs_review: 0
  leaked blocked routes: 0
  missing target files: 0
  classification counter:
    - safe_read_only                   1
    - safe_preview_only                0
    - locked_deferred                  3
    - mutation_sensitive_but_gated     18
    - unsafe_exposed                   0
    - unknown_needs_review             0
  verdict: PASS
==================================================================

[v119d PRE_QA_119D_PUBLIC_MENU_ROUTE_HEALTH] OK unsafe_exposed=0
  unknown_needs_review=0 leaked=0 file_targets_existing=22
```

JSON output prodotti:

- `backend/reports/pre_qa_pack_119d_public_menu_route_health_<UTC>.json`
- `backend/reports/pre_qa_pack_119d_public_menu_route_health_latest.json`

### 8.2 Validator 119C (regression)

```text
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK categories=6 items=22
  duplicates=0 soul_forge_unique=true labels_clean=true
  dev_routes_hidden=true live_routes_blocked=true
```

### 8.3 Pre-QA Safety Validator Suite (regression)

```text
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  SKIPPED: 0
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

✅ Tutti i 24 validator pre-QA esistenti continuano a passare.

### 8.4 Repo hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

## 9. Conferma no-touch (backend / runtime / DB / reward / gacha / shop / VIP / BP)

- ✅ Nessuna modifica a backend runtime, `battle_engine.py`, combat,
      gacha, shop, VIP, Battle Pass, reward, DB, tutorial, onboarding,
      starter claim, account reset.
- ✅ Nessuna modifica a Home 119A, hero scale/grounding, bottom tab
      layout, Character Bible, assets.
- ✅ Nessuna modifica a skill/status runtime, Divine Weapon runtime,
      Artifact runtime.
- ✅ `menu.tsx` e `preQaNavGuard.ts` **NON modificati**.
- ✅ Unico file nuovo: validator statico read-only
      `backend/scripts/validate_pre_qa_pack_119d_public_menu_route_health.py`
      (non tocca DB, non avvia network, non importa runtime TSX).

## 10. File creati

```text
git add -- backend/scripts/validate_pre_qa_pack_119d_public_menu_route_health.py
git add -- docs/divine/153_PRE_QA_PACK_119D_PUBLIC_MENU_ROUTE_TARGET_HEALTH_AND_MUTATION_CLASSIFICATION_FINAL_REPORT.md
```

(Nessun file frontend modificato.)

## 11. Verdict

**`PRE_QA_PACK_119D_PUBLIC_MENU_ROUTE_TARGET_HEALTH_AND_MUTATION_CLASSIFICATION_READY_FOR_GAME_MASTER_REAUDIT`**

Il menu pubblico filtrato è completamente classificato. Nessuna route
unsafe esposta, nessuna route unknown, nessuna live/dev-only route leakata.
La matrice è pronta per il prossimo step (Pack 120
`CONTROLLED_LIVE_UNLOCK_PREP`), che selezionerà candidate per unlock
controllato a partire dalla colonna `mutation_sensitive_but_gated`.

## 12. Commit SHA

Verrà aggiornato dopo `git commit`.
