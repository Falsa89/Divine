# Pack 123 — PRE_QA_PACK_123_PREVIEW_TEAM_FALLBACK_RUNTIME_WIRING_AND_TOWER_FLOOR_CRASH_FIX_BATCH

**Status:** ✅ COMPLETATO
**Data:** 2026-06-16
**Obiettivo finale:** `PRE_QA_ALPHA_PREVIEW_COMBAT_FLOW_DEVICE_TEST_READY`

---

## Sommario esecutivo

Il Pack 123 risolve tutti i blocker emersi dal Pack 122 che impedivano il
Device QA del combat preview:

1. **Fallback team locale deterministico** (no-write, no-DB, no-grant)
   utilizzando 6 hero_id REALI dal roster canonico `heroes_master.json`.
2. **Cablaggio runtime** del fallback in `pre-battle-lobby.tsx` e
   `combat.tsx` senza salvare team nel DB o assegnare eroi all'account.
3. **Fix del crash al tap** sui piani in `tower-of-the-hells.tsx`: ora
   apre correttamente un modal e naviga a `/pre-battle-lobby?mode=tower&floor_id=N`.
4. **"Training Preview Trial"** aggiunto in `hero-training.tsx` con CTA
   reale verso la lobby preview.
5. **Hub di preview Arena/Boss** consolidate con builder canonico
   `buildPreviewLobbyUrl`.

L'invariante assoluto **no-write / no-reward / no-progress / no-DB-mutation**
è stato mantenuto al 100% (verificato dai 5 validatori Python).

---

## Composizione del Team Preview 6v6 (canonico)

Tutti gli hero_id sono presenti in `data/design/heroes_master.json`,
3★ launch_base, no Borea, no 6★ premium, no hidden, no placeholder.

| Slot | Ruolo | hero_id | Nome (IT) | Rarità | Elemento |
|------|-------|---------|-----------|--------|----------|
| 1 | Tank | `greek_hoplite` | Hoplite | 3★ | Terra |
| 2 | DPS Melee | `norse_berserker` | Berserker | 3★ | Fuoco |
| 3 | DPS Ranged | `celtic_archer` | Arciera | 3★ | Vento |
| 4 | Mage AoE | `arcane_lightning_enchantress` | Incantatrice della Folgore | 3★ | Fulmine |
| 5 | Support / Buffer | `greek_sanctuary_muse` | Musa del Santuario | 3★ | Luce |
| 6 | Healer | `angelic_priestess` | Sacerdotessa | 3★ | Luce |

Power totale deterministico: **14 550**.

---

## File modificati

### Nuovi / riscritti
- `frontend/src/utils/previewBattleTeam.ts` — **REWRITTEN** (era stub).
  Aggiunti: `CANONICAL_PREVIEW_HERO_SLOTS`, `buildPreviewLocalTeamSnapshot`,
  `buildPreviewCombatUrl`, `buildPreviewLobbyUrl`, `previewContextFromParams`,
  `canUsePreviewTeamFallback`. Tutte fail-closed.

### Cablaggi runtime (additivi, no-refactor)
- `frontend/app/pre-battle-lobby.tsx`
  - Import e detection `previewContextFromParams`.
  - Banner UI "PACK 123 — PREVIEW TEAM FALLBACK ATTIVO".
  - Render dei 6 slot canonici quando preview attivo.
  - Bypass blocker chain SOLO se tutti i flag preview coerenti.
  - `startBattle()` usa `buildPreviewCombatUrl()` quando preview attivo.
- `frontend/app/combat.tsx`
  - Iniezione minimale: render del preview team snapshot nella schermata
    `preview_locked` (lista 6 hero_id reali, totale power, mode).
  - Fail-closed: nessun side-effect se non in contesto preview.
- `frontend/app/tower-of-the-hells.tsx`
  - **FIX CRASH:** handler `handleOpenPreviewLobby()` con try/catch.
  - Bottone "Avvia Preview Lobby" nel modal del piano selezionato.
  - Navigazione a `/pre-battle-lobby?mode=tower&floor_id=N` con tutti i
    flag preview coerenti.
- `frontend/app/hero-training.tsx`
  - Nuova card **"Training Preview Trial"** con CTA "Avvia Preview Trial".
  - Handler `openTrainingPreviewTrial()` con `buildPreviewLobbyUrl()`.
- `frontend/app/arena-preview.tsx`
  - Switch a `buildPreviewLobbyUrl()` con flag preview completi.
- `frontend/app/boss-raid-preview.tsx`
  - Switch a `buildPreviewLobbyUrl()` con flag preview completi.

---

## Validatori Python (tutti PASS)

| Validator | Status | Coverage |
|-----------|--------|----------|
| `validate_pre_qa_pack_123_preview_team_runtime_wiring.py` | ✅ PASS | 9 export utility + 6 consumer cablati |
| `validate_pre_qa_pack_123_canonical_hero_ids.py` | ✅ PASS | 6 hero_id verificati canonici + role coverage 6v6 |
| `validate_pre_qa_pack_123_tower_floor_tap_no_crash.py` | ✅ PASS | handler + try/catch + route lobby presenti |
| `validate_pre_qa_pack_123_no_db_write_invariant.py` | ✅ PASS | 0 chiamate live introdotte, gate positivi presenti |
| `validate_pre_qa_pack_123_preview_hubs_complete.py` | ✅ PASS | arena 3 + boss 3 + training trial completi |

Report JSON dettagliati: `backend/scripts/reports/pack_123_*.json`.

---

## Invarianti rispettati

- ❌ NO write su database
- ❌ NO save team / save formation
- ❌ NO grant heroes / mutazione roster
- ❌ NO reward / EXP / progress / drop / affinity
- ❌ NO gacha / shop / VIP / battlepass / IAP mutation
- ❌ NO chiamate live a backend mutante (`/api/battle/simulate`,
  `/api/team/save*`, `/api/*/grant`, `/api/gacha/*`, ecc.)
- ❌ NO modifiche a `backend/battle_engine.py`, `backend/battle_core.py`,
  `backend/server.py`, `backend/game_systems.py`, `.env`, schema DB
- ✅ Fail-closed: ogni gate ritorna `null` o disattiva il fallback se i
  flag preview non sono coerenti
- ✅ Banner UI esplicito visibile in lobby + combat (no fake-real)
- ✅ Hero IDs reali e canonici, no fittizi

---

## Verifica visuale eseguita

- Schermata Torre carica correttamente (no crash).
- Tap su Floor 1 (unlocked) apre il modal con bottone primario
  "Avvia Preview Lobby" (verificato via screenshot).
- TypeScript: 0 errori introdotti dal Pack 123 sui file modificati
  (errori pre-esistenti su `combat.tsx`/`home.tsx`/`servers.tsx` non sono
  in scope di questo pack).
- Frontend service: **RUNNING** (`expo` supervisor status OK).

---

## Prossimi passi suggeriti

1. **Device QA** (a carico utente) — testare il flusso reale su iOS/Android:
   - Tower: tap piani → lobby → preview combat.
   - Hero Training: Trial preview.
   - Arena / Boss preview hubs → lobby → combat.
2. `servers.tsx` lock marker hygiene (P3, separato dal Pack 123).
3. Preparare `CONTROLLED_LIVE_UNLOCK` per future iterazioni.

---

## Hash / Provenance

- Pack: `PRE_QA_PACK_123_PREVIEW_TEAM_FALLBACK_RUNTIME_WIRING_AND_TOWER_FLOOR_CRASH_FIX_BATCH`
- Goal: `PRE_QA_ALPHA_PREVIEW_COMBAT_FLOW_DEVICE_TEST_READY`
- Schema policy: `data/design/vertical_slice_qa/pack_123_preview_team_runtime_policy_v1.json` (v2)
- Manifest QA: `data/design/vertical_slice_qa/pack_123_device_qa_manifest_v3.json`
- Lingua report: **Italiano** (come da requisito utente).
