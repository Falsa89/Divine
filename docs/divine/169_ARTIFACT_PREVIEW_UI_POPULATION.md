# 169 — PROJECT ARTIFACT PREVIEW UI POPULATION

**Verdict locale container:** `PROJECT_ARTIFACT_PREVIEW_UI_POPULATION_READY`
**Verdict sync pubblico:** `PROJECT_ARTIFACT_PREVIEW_UI_POPULATION_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Sommario

Popolata `/artifacts-preview` con 10 reliquie canoniche read-only dalla Bible v1. Nessuna API mutativa, nessuna inventory, nessun DB write. Solo design + UI.

## Track Verdicts (8/8 READY)

| Track | Verdict |
|---|---|
| A — Source manifest revalidation (20 file) | READY |
| B — Dataset 10 entries safe | READY |
| C — Frontend UI implementation | READY |
| D — Route + lock guard | READY |
| E — Beta harness smoke | READY (static-equivalent) |
| F — Static validator + suite | READY |
| G — Public repo sync | pending push |
| H — Completion | READY |

## Dataset 10 reliquie (Track B)

| ID | Nome | Categoria | Rarità |
|---|---|---|---|
| relic_aurora_eterna | Aurora Eterna | divine_relic | legendary |
| relic_calice_vespro | Calice del Vespro | divine_relic | legendary |
| relic_lacrima_oceano | Lacrima dell'Oceano | divine_relic | epic |
| relic_seme_albero_mondo | Seme dell'Albero del Mondo | divine_relic | legendary |
| relic_pluma_fenix | Piuma di Fenice | divine_relic | epic |
| relic_scaglia_drago_antico | Scaglia del Drago Antico | divine_relic | epic |
| relic_sigillo_lunare | Sigillo Lunare | sacred_symbol | epic |
| relic_mandala_otto_porte | Mandala delle Otto Porte | sacred_symbol | epic |
| relic_emblema_olimpo | Emblema dell'Olimpo | pantheon_emblem | legendary |
| relic_pagina_libro_perduto | Pagina del Libro Perduto | world_memory | epic |

**Selection rules**: tutte `launch_candidate` + `cosmetic_prestige_only`. Nessuna `future_reserved`. Nessun legacy placeholder name.

**Nota**: il pack spec referenzia `relic_piuma_fenice` (typo). La Bible canonica usa `relic_pluma_fenix`. Allineato all'ID Bible (source of truth). Display name UI: "Piuma di Fenice".

## UI Implementation (Track C)

`frontend/app/artifacts-preview.tsx` (MD5 `21df52d3df4b2b67802f8ed6872a2564`):

- Titolo: **"Reliquie Divine"**
- Banner: **"🔒 Sistema in preparazione"** + disclaimer "Nessuna evocazione, equipaggiamento, fusione o craft è disponibile."
- Chip categoria filtri (Tutte / Reliquie Divine / Simboli Sacri / Emblemi Pantheon / Memorie del Mondo)
- 10 card con:
  - Nome + categoria + icon + tint
  - Badge **"ANTEPRIMA"**
  - Stelle rarità
  - Short lore + visual hint italic
  - Status row **"● Non ottenibile ora"**
- Back button accessibile
- Footer note con disclaimer chiusura

**Zero**: API calls, fetch, apiCall, /api/artifacts/*, /api/constellations/*, EVOCA/EQUIPAGGIA/FONDI/CRAFT/ACQUISTA/OTTIENI ORA.

## Route + Lock Guards (Track D)

- `HIDDEN_BANNERS_V2 = {artifact, constellation}` ✅
- `LOCKED_BANNERS_V2 = {premium, targeted}` ✅
- `/artifacts` → `router.replace('/artifacts-preview')` ✅
- `backend/routes/artifacts.py` untouched ✅
- `backend/battle_engine.py` invariato (`151ca35a…`) ✅
- `backend/.env` invariato (`ff60bbb7…`) ✅

## Runtime changes

| Item | Valore |
|---|---|
| frontend UI changes | 1 (artifacts-preview.tsx populated read-only) |
| frontend logic changes | 0 |
| backend route/logic changes | 0 |
| DB writes da script | 0 |
| battle_engine changes | 0 |
| gacha rate changes | 0 |
| IAP / artifact banner / constellation banner / character bible mutation | false |
| backend catalog endpoint added | false |
| inventory state added | false |

## Suite

`python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel`
→ target **700 PASS / 0 FAIL / 0 MISS**

## Mobile QA checklist

- [ ] /artifacts-preview si apre senza crash
- [ ] Titolo "Reliquie Divine" visibile
- [ ] Banner "Sistema in preparazione" visibile
- [ ] Chip categoria funzionano (client-side puro)
- [ ] 10 cards con badge ANTEPRIMA + "Non ottenibile ora"
- [ ] Nessun bottone EVOCA/EQUIPAGGIA/FONDI/CRAFT/ACQUISTA/OTTIENI ORA
- [ ] Back button torna indietro
- [ ] Gacha tab: artefatti e costellazioni continuano a NON apparire
- [ ] /artifacts redirect a /artifacts-preview

## Prossimo pack consigliato

- **Primary**: `PROJECT_ARTIFACT_BACKEND_CATALOG_RO_PACK` (stage 4)
- **Alternative**: `PROJECT_IAP_DESIGN_PACK` (P1 parallelo)
