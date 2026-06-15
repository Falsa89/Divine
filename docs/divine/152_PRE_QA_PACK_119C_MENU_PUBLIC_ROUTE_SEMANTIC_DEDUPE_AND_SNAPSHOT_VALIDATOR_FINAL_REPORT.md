# Pack 119C — Menu Public Route Semantic Dedupe & Snapshot Validator — Final Report

> **Codice pack:** `PRE_QA_PACK_119C_MENU_PUBLIC_ROUTE_SEMANTIC_DEDUPE_AND_SNAPSHOT_VALIDATOR`
> **Tipo:** Pulizia semantica menu pubblico (dedupe route `/soul-forge`,
> disambiguazione hub-modalità vs pre-battle-lobby) + snapshot/validator
> statico del menu pubblico filtrato.
> **Scope file:** `frontend/app/(tabs)/menu.tsx` + nuovo validator backend
> `backend/scripts/validate_pre_qa_pack_119c_menu_public_snapshot.py` +
> questo report.
> **No-touch:** backend runtime, battle_engine.py, combat runtime, gacha,
> shop, VIP, Battle Pass, reward, DB, tutorial, onboarding, starter claim,
> account reset, Home 119A, hero scale, menu redesign grafico, bottom tab
> layout, Character Bible, assets, skill/status runtime, Divine Weapon
> runtime, Artifact runtime.

## 0. Numerazione del report

Il prossimo numero libero dopo `151_PRE_QA_PACK_119B_...` è **152** (i numeri
153–165 sono pure liberi, ma rispettiamo la sequenza incrementale stretta).

## 1. Obiettivi del pack

1. **Rimuovere il doppione `/soul-forge`** dal menu pubblico (esistevano due
   voci che puntavano alla stessa URL, una in Progressione l'altra in
   Economia).
2. **Disambiguare semanticamente** la categoria hub-modalità dalla categoria
   pre-battle-lobby (entrambe contenevano voci tipo "Storia" e "Torre" con
   route diverse).
3. **Aggiungere uno snapshot/validator statico** del menu pubblico filtrato
   per consentire al Game Master di verificare il contenuto del menu senza
   testare manualmente ogni voce.

## 2. Modifiche applicate

### 2.1 `frontend/app/(tabs)/menu.tsx`

#### 2.1.1 Dedupe `/soul-forge`

| Posizione | Prima | Dopo |
| --- | --- | --- |
| `Progressione` | `Soul Forge` → `/soul-forge` | `Forgia dell'Anima` → `/soul-forge` |
| `Economia` | `Forgia dell'Anima` → `/soul-forge` | **rimossa** |

`/soul-forge` ora appare **una sola volta** nel menu pubblico, con label
canonica IT `Forgia dell'Anima`, nella categoria Progressione. La route, la
schermata `/soul-forge` e l'economia interna NON sono toccate; il deep link
resta funzionante.

#### 2.1.2 Disambiguazione hub-modalità vs pre-battle-lobby

| Categoria | Prima | Dopo |
| --- | --- | --- |
| Titolo categoria hub-modalità | `Combattimento` | `Avventura` |
| Voce hub story | `Storia` → `/story` | `Capitoli Storia` → `/story` |
| Voce hub torre | `Torre degli Inferi` → `/tower-of-the-hells` | invariata |
| Categoria pre-battle-lobby | `Battaglia` | invariata |
| Voci pre-battle-lobby | `Storia / Torre / Arena PvP / Addestramento / Raid` → `/pre-battle-lobby?mode=...` | invariate |

Le due categorie non sembrano più doppioni:

- **Avventura** (`/story`, `/tower-of-the-hells`) = hub di accesso alle
  modalità live (capitoli, torre).
- **Battaglia** (`/pre-battle-lobby?mode=...`) = pre-battle-lobby canonica
  che instrada al renderer reale.

Nessun uso di token tecnici (no "Hub", no "preview", no "renderer", no "v90",
no "TEST", no "QA"). Le route esistenti restano funzionanti; nessun
pre-battle-lobby è stato rimosso.

### 2.2 `backend/scripts/validate_pre_qa_pack_119c_menu_public_snapshot.py`

Nuovo validator statico (regex-based, no runtime TSX) che:

1. Parsa `frontend/app/(tabs)/menu.tsx` ed estrae l'array `CATEGORIES`
   (categorie + voci `label`/`route`).
2. Parsa `frontend/src/utils/preQaNavGuard.ts` ed estrae i set canonici
   `PRE_QA_BLOCKED_PLAYER_ROUTES` e `PRE_QA_BLOCKED_CATEGORIES`.
3. Applica la stessa logica di filtro del menu (categoria bloccata +
   `isRouteAllowedInPreQa`) per produrre lo **snapshot del menu pubblico
   filtrato**.
4. Verifica i criteri Pack 119C (token tecnici nelle label, token QA nelle
   categorie, prefissi dev nelle route, duplicati route full-URL,
   `/soul-forge` unico, presenza route live-blocked nel guard).

Onesto e non-fragile: ogni assert fallisce in modo verboso con `rc=1`. Nessun
runtime TSX, nessun rischio Metro/Expo, parsing scoping esplicito.

## 3. Snapshot menu pubblico filtrato (Pack 119C)

```json
{
  "categories_visible": 6,
  "items_visible": 22,
  "blocked_player_routes": 37,
  "blocked_categories": 3,
  "duplicate_route_exceptions": [],
  "failures": 0,
  "verdict": "PASS"
}
```

### 3.1 Categorie e voci visibili (guard di default ON, EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=OFF)

| # | Categoria | Voce | Route |
| --- | --- | --- | --- |
| 1 | **Avventura** | Capitoli Storia | `/story` |
| 2 | Avventura | Torre degli Inferi | `/tower-of-the-hells` |
| 3 | **Progressione** | Collezione Eroi | `/hero-collection` |
| 4 | Progressione | Addestramento Eroico | `/hero-training` |
| 5 | Progressione | Fucina di Efesto | `/equipment` |
| 6 | Progressione | Artefatti & Costellazioni | `/artifacts-preview` |
| 7 | Progressione | Forgia dell'Anima | `/soul-forge` |
| 8 | Progressione | Achievement | `/achievements` |
| 9 | **Economia** | Tesoreria | `/treasury` |
| 10 | Economia | Inventario | `/inventory` |
| 11 | **Sociale** | Fazione del Giocatore | `/player-faction` |
| 12 | **Altro** | Guida / Codex | `/guide` |
| 13 | Altro | Classifiche | `/rankings` |
| 14 | Altro | Seleziona Server | `/servers` |
| 15 | Altro | Guida Giornaliera | `/daily-hub` |
| 16 | Altro | Armi Divine | `/divine-weapons-catalog` |
| 17 | Altro | Sinergie Collezione | `/collection-synergies-preview` |
| 18 | **Battaglia** | Storia | `/pre-battle-lobby?mode=story` |
| 19 | Battaglia | Torre | `/pre-battle-lobby?mode=tower` |
| 20 | Battaglia | Arena PvP | `/pre-battle-lobby?mode=arena` |
| 21 | Battaglia | Addestramento | `/pre-battle-lobby?mode=training` |
| 22 | Battaglia | Raid | `/pre-battle-lobby?mode=boss` |

### 3.2 Categorie bloccate (PRE_QA_BLOCKED_CATEGORIES)

- `Battle Preview QA (v88) — Wireframe Deprecato v90` (Pack 119B)
- `Modalità Live & Guild QA (v92)`
- `Playability & Announcements QA (v93)`

### 3.3 Route player bloccate principali (PRE_QA_BLOCKED_PLAYER_ROUTES, totale 37)

Live/deferred:
`/shop`, `/vip`, `/battlepass`, `/gacha`, `/pvp`, `/guild`, `/gvg`, `/raid`,
`/territory`, `/plaza`, `/dm`, `/events`, `/mail`, `/friends`.

Cataloghi interni / dev / wireframe deprecato (Pack 119B):
`/playable-mode-battle-preview`, `/skill-status-vfx-catalogs`,
`/hero-skill-kits-catalog`, `/safe-previews`.

Altre legacy/deferred:
`/affinity`, `/arena`, `/artifacts`, `/blessings`, `/constellations`,
`/cosmetics`, `/exclusive-items`, `/fragments`, `/item-shop`,
`/level-sharing`, `/materials`, `/profile`, `/quests`, `/research`,
`/runes`, `/sanctuary`, `/tower`, `/unique-items`, `/wallet`.

### 3.4 Duplicati route player-facing

**0 duplicati** (dedupe chiave: route full URL incluse query string).
`/soul-forge` appare **una sola volta** (Progressione → Forgia dell'Anima).
Le 5 voci di `/pre-battle-lobby?mode=...` hanno mode diversi e quindi route
full distinte: non sono doppioni semantici ma entry-point indipendenti per
le 5 modalità (story/tower/arena/training/boss).

Eccezioni esplicite ammesse: **nessuna**
(`ALLOWED_DUPLICATE_ROUTES = set()`).

## 4. Validazione

### 4.1 Validator 119C dedicato

```text
$ python3 backend/scripts/validate_pre_qa_pack_119c_menu_public_snapshot.py
...
[v119c PRE_QA_119C_MENU_PUBLIC_SNAPSHOT] OK categories=6 items=22 duplicates=0
  soul_forge_unique=true labels_clean=true dev_routes_hidden=true
  live_routes_blocked=true
```

✅ PASS — nessun token tecnico nelle label, nessuna categoria QA visibile,
nessuna route dev/wireframe nel menu pubblico, nessun duplicato player-facing,
`/soul-forge` unico, tutte le route live-blocked presenti nel guard.

### 4.2 Pre-QA Safety Validator Suite (regression)

```text
$ python3 backend/scripts/run_pre_qa_safety_validator_suite.py
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  SKIPPED: 0
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

✅ Tutti i 24 validator pre-QA esistenti restano PASS. Nessuna regressione
introdotta dal Pack 119C (incluso `Pack 110 Menu Cleanup` che continua a
certificare routes/categorie unsafe bloccate).

### 4.3 Repo hygiene

```text
$ python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

✅ Repo hygiene pulita. Nessun artefatto Python compilato staged.

### 4.4 TypeScript

`npx tsc --noEmit -p .` non riporta errori per
`frontend/app/(tabs)/menu.tsx`. Errori TS pre-esistenti su
`app/(tabs)/home.tsx` e `app/combat.tsx` sono fuori scope e non toccati.

## 5. Acceptance criteria — checklist

- [x] `/soul-forge` appare una sola volta nel menu pubblico.
- [x] Label finale: `Forgia dell'Anima` (Progressione).
- [x] Hub-modalità (`Avventura`) e pre-battle-lobby (`Battaglia`) sono
      semanticamente distinte e non sembrano doppioni identici.
- [x] Nessuna label tecnica o QA torna visibile.
- [x] Nessuna route unsafe/live viene sbloccata.
- [x] Gating Pack 119B intatto (categorie + route).
- [x] Menu funzionale, frontend HTTP 200 dopo restart Expo.
- [x] Validator 119C PASS.
- [x] Safety suite 24/24 PASS.
- [x] Repo hygiene clean.
- [x] Report in italiano.

## 6. Conferma no-touch (backend / runtime / DB / gacha / reward)

- ✅ Nessun file backend modificato eccetto il **nuovo validator statico
      read-only** `validate_pre_qa_pack_119c_menu_public_snapshot.py` (non
      tocca DB, non avvia network, non modifica stato).
- ✅ Nessuna modifica a `battle_engine.py`, combat runtime, gacha, shop,
      VIP, Battle Pass, reward, DB, tutorial, onboarding, starter claim,
      account reset.
- ✅ Nessuna modifica a Home 119A, hero scale, menu redesign grafico,
      bottom tab layout, Character Bible, assets.
- ✅ Nessuna modifica a skill/status runtime, Divine Weapon runtime,
      Artifact runtime.

## 7. File modificati (commit list)

```text
git add -- frontend/app/(tabs)/menu.tsx
git add -- backend/scripts/validate_pre_qa_pack_119c_menu_public_snapshot.py
git add -- docs/divine/152_PRE_QA_PACK_119C_MENU_PUBLIC_ROUTE_SEMANTIC_DEDUPE_AND_SNAPSHOT_VALIDATOR_FINAL_REPORT.md
```

(`frontend/src/utils/preQaNavGuard.ts` letto solo in read-only durante il
parsing del validator; non modificato.)

## 8. Verdict

**`PRE_QA_PACK_119C_MENU_PUBLIC_ROUTE_SEMANTIC_DEDUPE_AND_SNAPSHOT_VALIDATOR_READY_FOR_GAME_MASTER_REAUDIT`**

Il menu pubblico è ora dedupato semanticamente: `/soul-forge` appare una sola
volta come `Forgia dell'Anima` in Progressione; `Avventura` (hub modalità) e
`Battaglia` (pre-battle-lobby) sono categorie distinte e non confondibili; lo
snapshot statico è verificabile via validator riproducibile in CI/manuale.

## 9. Commit SHA

Verrà aggiornato dopo `git commit` (vedi sezione finale).
